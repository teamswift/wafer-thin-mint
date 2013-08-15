# this is some of the example settings required for your settings.py in Django
# here is where you set your urls, in our case we follow a standard to intercept TastyPie
table_urls = {
    'client': {
        'host': 'http://10.200.32.90',
        'suffix': '?format=json',
        'tables': {
            'client': '/pobsi/config/api/v1/client/',
            'territory': '/pobsi/config/api/v1/territory/'
        }
    }
}
# the location of your connector model - either use the standard or implement your own
connector_model = 'wafer-thin-mint.core.Connector'

# sample Connector file
#def Connector(table): # required pointer name of table - use this as your reference point for your table in your api
#    # your
#    # code
#    # goes
#    # here
#
#    # you must return these 3 elements
#    return code, body, result



# sample Model file
# system is modeled on the django ORM methodology so treat your models alike, with the one exception of pointing to the 'wafer-thin-mint' core model and the altercations in type names
#from wafer-thin-mint.core import core
#class Bob(core.Model):
#    id = core.IntegerField
#    reference = core.Charfield
#    description = core.Charfield

# field types can be named like so
#Charfield
#IntegerField
#DecimalField
#TextField