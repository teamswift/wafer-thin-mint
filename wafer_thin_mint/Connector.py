import json
import urlparse
from paymentutils import sever_to_server

# default connector - this is the server to server model used within Toksi.. change as you will, as long as you return
# code (int), body (json), result (object)
# e.g. code = 200, body = [{'id': 1,}], result = <Response 200>
def Connector(settings,table,keys,method=None,resource=None):
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
    fullpath = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']+params
    schema = settings.WAFER_THIN_MINT['client']['tables'][table]+'schema/'+settings.WAFER_THIN_MINT['client']['suffix']

    res = auth.get(schema)
    if res.status_code == 200:
        # we can confirm our search params
        r = res.content
        r = json.loads(r)


    if method is None or method == 'get':
        for k in keys:
            if r:
                if 'filtering' in r:
                    if k in r["filtering"]:
                        params += '&{}__exact={}'.format(k,keys[k])
                else:
                    params += '&{}__exact={}'.format(k,keys[k])

        fullpath = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']+params
        result = auth.get(fullpath)

    elif method == 'post':
        fullpath = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']
        body = json.dumps(keys)
        result = auth.post(fullpath, body, content_type='json')

    elif method == 'put':
        fullpath = resource+settings.WAFER_THIN_MINT['client']['suffix']
        body = json.dumps(keys)
        result = auth.put(fullpath, body, content_type='json')

    elif method == 'delete':
        fullpath = resource+settings.WAFER_THIN_MINT['client']['suffix']
        body = json.dumps(keys)
        result = auth.delete(fullpath, body, content_type='json')

    else:
        raise AttributeError('Unrecognised transport method')

    code = result.status_code

    if code == 201:
        # then we created an object..
        body = result.headers['location']
    elif code == 204:
        body = None
    elif code == 410:
        raise StandardError('Cannot fetch/delete as resource is already gone')
    elif code == 500 or code == 501:
        if method=='post':
            # item already exists or bad form
            raise StandardError('Cannot create, possible unique reference or other SQL related prevention')
        elif method == 'put':
            raise StandardError('Cannot save record')
        else:
            # just bad form
            raise StandardError('Unable to fetch row, may be due to improperly setup mapping URLs or bad lookup')
    else:
        if 'objects' in json.loads(result.content):
            body = json.loads(result.content)['objects']
        else:
            body = None

    return code, body, result