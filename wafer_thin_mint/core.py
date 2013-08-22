import importlib


class ModelBase(type):

    def __new__(meta, name, supers, attrs):
        class_types = (type, type(meta))
        directory = [n for n in dir(meta) if not n.startswith("_")]
        attributes = [n for n in directory if not callable(getattr(meta, n))]
        inner_classes = [n for n in directory if isinstance(getattr(meta, n), class_types)]

        for c in inner_classes:
            c = getattr(meta, c)
            for a in attributes:
                if not hasattr(c, a):
                    setattr(c, a, getattr(meta, a))

        return type.__new__(meta, name, supers, attrs)

    def __init__(class_, name, supers, attrs):
        class_._table = '{}'.format(class_.__name__).lower()
        return type.__init__(class_, name, supers, attrs)

    @property
    def objects(cls):
        settings = getattr(cls,'__settings__',None)
        if settings is not None:
            # we try to import
            cls.using(settings) # reuse using method
        else:
            cls._settings = None

        return cls

    def check(cls, k, v):
        if not(hasattr(cls, k)):
            raise ValueError('<{}> field does not exist'.format(k))

            # check instance of the value of our param is equal to that of the type set.. otherwise our value has been given an incorrect value
            if not(isinstance(v, getattr(cls, k))):
                raise TypeError('<{}> value "{}" is not of {}... instead of {}'.format(k, v, getattr(cls,k), type(v)))

    def using(cls, settings):
        try:
            cls._settings = importlib.import_module(settings)
        except:
            raise EnvironmentError('Unable to reference settings file - cannot import settings')
        return cls

    def get(cls, **kwargs):
        if cls._settings is None:
            raise EnvironmentError('Either set __settings__ = "module.location", or .using("module.location") to reference settings location')
            # preset our object
        object = None
        keyvars = {}
        # iterate through provided fields
        for k,v in kwargs.items():
            # check values/fields ok
            cls.check(k,v)
            if isinstance(v, ModelBase):
                # foriegn key so lets take our primary
                # primary = v._pk
                keyvars[k]=getattr(v,v._pk)
            else:
                keyvars[k]=v

        #for k,v in kwargs.items():
        # make API call with elements
        code, body, res = cls.call(keyvars)
        # are we ok?
        if code == 400:
            raise ValueError('unable to filter on specified params')
        elif code != 200:
            raise EnvironmentError('Unable to connect to 3rd party database API')


        if body is None:
            raise ValueError('unable to filter on specified params')

        # are the fields we have correct?
        if len(body) is 0:
            raise ValueError('unable to filter on specified params')

        if k not in body[0]:
            raise ValueError('Improperly setup DB API object - field not found in response')

        # with our field.. filter
        for i in body:
            #print i
            for k in keyvars:
                if keyvars[k] == i[k]:
                    object = i
                    break
                elif isinstance(i[k], dict):
                    # then we have a foriegn key
                    for ii in i[k]:
                        if isinstance(keyvars[k], ModelBase):
                            nv = getattr(keyvars[k], ii)
                            if isinstance(getattr(keyvars[k], ii), PrimaryKey):
                                if nv == i[k][ii]:
                                    object = i
                                    break
                        elif keyvars[k] == i[k][ii]:
                            object = i
                            break

        # check if we found what we were searching for...
        if not(isinstance(object, dict)):
            raise TypeError('Unable to find matching row')

        # set results back to objects
        for o in object:
            ch = getattr(cls, o, None)
            if ch == pk:
                setattr(cls, '_pk', o)

            setattr(cls, o, object[o])

        # return instance back to object
        return cls

    def save(cls):
        if not cls._pk:
            raise SystemError("Cannot save before fetching or creating items")

        d = {}
        for el in cls.__dict__:
            if not(el.startswith("_") or el == 'resource_uri'):
                var = getattr(cls, el)
                if not el == cls._pk:
                    # we have to filter out case of pk as these cannot be changed
                    d = dict(d, **{el: var})

        resource = getattr(cls, 'resource_uri', None)
        if resource is None:
            raise EnvironmentError("Failure, cannot locate resource_uri - somethings gone wrong")
        code, body, res = cls.call(d, method='put', resource=resource)
        if code == 204:
            # we have a sucess!
            #print d
            cls.get(**d)

        return cls

    def create(cls, **kwargs):
        if cls._settings is None:
            raise EnvironmentError('Either set __settings__ = "module.location", or .using("module.location") to reference settings location')

        keyvars = {}
        # iterate through provided fields
        for k,v in kwargs.items():
            # check values/fields ok
            cls.check(k,v)
            if isinstance(v, ModelBase):
                # we ignore Primary Key sets - as we await this from the source
                pass
            else:
                keyvars[k]=v


        code, body, res = cls.call(keyvars, method='post')
        if code == 201:
            import urlparse
            path = urlparse.urlparse(body) # if successful we would have retrieved the location
            sp = path.path.split('/')
            sp = filter(None,sp)
            sp = sp[::-1]

            dic = cls.__dict__
            for a in dic:
                is_pk = getattr(cls, a)
                if is_pk == pk:
                    # now we refetch our newly created object and voila all set!
                    d = dict({'{}'.format(a):sp[0]}, **keyvars)
                    # we can break out as only one pk per table allowed
                    break

            cls.get(**d)

        return cls

    def call(cls,keys, method=None, resource=None):

        if not(cls._settings.WAFER_THIN_MINT['client']['tables'][cls._table]):
            raise ValueError('Table url not found - please ensure table url is set in settings file:\n'\
                             'example:'\
                             'table_urls = {'\
                             '"client": {'\
                             '"host": "http://10.200.32.90",'\
                             '"suffix": "?json",'\
                             '"tables": {'\
                             '"client": "/pobsi/api/v1/config/client/",'\
\
                             '}'\
                             '}'\
                             ' }'\
            )

        c = importlib.import_module(cls._settings.WAFER_THIN_MINT['connector_model'])
        code, body, result = c.Connector(cls._settings,cls._table,keys,method,resource)

        return code, body, result



class Model(object):
    __metaclass__ = ModelBase


class pk(object):
    pass


from decimal import Decimal

PrimaryKey = pk
Charfield = str
IntegerField = int
DecimalField = Decimal
TextField = str
ForiegnKey = ModelBase