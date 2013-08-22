import json
import urlparse
from paymentutils import sever_to_server

# default connector - this is the server to server model used within Toksi.. change as you will, as long as you return
# code (int), body (json), result (object)
# e.g. code = 200, body = [{'id': 1,}], result = <Response 200>
def Connector(settings,table,keys):
    try:
        access_key = settings.CONMAN_ACCESS[settings.CONMAN_ACCESS_KEY]['key']
        secret_key = settings.CONMAN_ACCESS[settings.CONMAN_ACCESS_KEY]['secret']
    except:
        access_key = False
        secret_key = False


    if not all([secret_key, access_key]):
        raise ValueError('Unable to locate access and secret keys for Server to Server Auth')

    auth = sever_to_server.Server_to_server()
    auth.connect(
        url=settings.WAFER_THIN_MINT['client']['host'],
        key=access_key,
        secret=secret_key
    )
    params = ''
    for k in keys:
        params += '&{}__exact={}'.format(k,keys[k])

    fullpath = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']+params

    result = auth.get(fullpath)

    code = result.status_code

    if 'objects' in json.loads(result.content):
        body = json.loads(result.content)['objects']
    else:
        body = None

    return code, body, result