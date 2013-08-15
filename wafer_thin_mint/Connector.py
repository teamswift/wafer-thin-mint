from toksi import settings
import json
import urlparse
from paymentutils import sever_to_server

# default connector - this is the server to server model used within Toksi.. change as you will, as long as you return
# code (int), body (json), result (object)
# e.g. code = 200, body = [{'id': 1,}], result = <Response 200>
def Connector(table):
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
        url=settings.table_urls['client']['host'],
        key=access_key,
        secret=secret_key
    )

    path = urlparse.urlparse(settings.table_urls['client']['tables'][table]+settings.table_urls['client']['suffix'])

    result = auth.get(path.path)

    code = result.status_code

    body = json.loads(result.content)['objects']

    return code, body, result
