from toksi import settings

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
        return cls

    def check(cls, k, v):
        if not(hasattr(cls, k)):
            raise ValueError('<{}> field does not exist'.format(k))

        if not(isinstance(v, getattr(cls, k))):
            raise TypeError('<{}> value "{}" is not of {}... instead of {}'.format(k, v, getattr(cls,k), type(v)))

    def get(cls, **kwargs):
        # iterate through provided fields
        for k,v in kwargs.items():
            # check values/fields ok
            cls.check(k,v)
            # make API call with elements
            code, body, res = cls.call()
            # are we ok?
            if code != 200:
                raise EnvironmentError('Unable to connect to 3rd party database API')

            # are the fields we have correct?
            if k not in body[0]:
                raise ValueError('Improperly setup DB API object - field not found in response')

            # with our field.. filter
            for i in body:
                if v == i[k]:
                    object = i
                    break

                #            for o in object:
                #                print o

            # set results back to objects
            for o in object:
                if not hasattr(cls, o):
                    setattr(cls, o, object[o])

        # return instance back to object
        return cls

    def save(cls):
        print '""saving""'
        pass

    def create(cls):
        print '""creating""'
        pass

    def call(cls):

        if not(settings.table_urls['client']['tables'][cls.table]):
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

        import importlib
        c = importlib.import_module(settings.connector_model)
        code, body, result = c.Connector(cls.table)

        return code, body, result




class Model(object):
    __metaclass__ = ModelBase



from decimal import Decimal


Charfield = str
IntegerField = int
DecimalField = Decimal
TextField = str

class Client(Model):
    id = IntegerField

p = Client.objects.get(id=2)

print p.style
print p.client_reference