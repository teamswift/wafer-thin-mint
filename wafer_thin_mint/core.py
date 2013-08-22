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
        class_.table = '{}'.format(class_.__name__).lower()
        return type.__init__(class_, name, supers, attrs)

    @property
    def objects(cls):
        settings = getattr(cls,'__settings__',None)
        if settings is not None:
            # we try to import
            cls.using(settings) # reuse using method
        else:
            cls.settings = None

        return cls

    def check(cls, k, v):
        if not(hasattr(cls, k)):
            raise ValueError('<{}> field does not exist'.format(k))

            # check instance of the value of our param is equal to that of the type set.. otherwise our value has been given an incorrect value
            if not(isinstance(v, getattr(cls, k))):
                raise TypeError('<{}> value "{}" is not of {}... instead of {}'.format(k, v, getattr(cls,k), type(v)))

    def using(cls, settings):
        try:
            cls.settings = importlib.import_module(settings)
        except:
            raise EnvironmentError('Unable to reference settings file - cannot import settings')
        return cls

    def get(cls, **kwargs):
        if cls.settings is None:
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
        print '""saving""'
        pass

    def create(cls):
        print '""creating""'
        pass

    def call(cls,keys):

        if not(cls.settings.WAFER_THIN_MINT['client']['tables'][cls.table]):
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


        c = importlib.import_module(cls.settings.WAFER_THIN_MINT['connector_model'])
        code, body, result = c.Connector(cls.settings,cls.table,keys)

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