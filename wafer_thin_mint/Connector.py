import json
import requests

# default connector using requests
# code (int), body (json), result (object)
# e.g. code = 200, body = [{'id': 1,}], result = <Response 200>
TIMEOUT = 30

def Connector(settings,table,keys,method=None,resource=None):

    params = ''
    body = ''

    try:
        host = settings.WAFER_THIN_MINT['client']['host']
        schema = settings.WAFER_THIN_MINT['client']['tables'][table]+'schema/'+settings.WAFER_THIN_MINT['client']['suffix']
        res = requests.get(host+schema, data=body, params=params, timeout=TIMEOUT)

        if res.status_code == 200:
        # we can confirm our search params
            r = res.content
            r = json.loads(r)
    except ValueError:
        raise ValueError("Missing wafer-thin-mint configuration")
    except Exception as e:
        raise e

    if method is None or method == 'get':
        for k in keys:
            if r:
                if 'filtering' in r:
                    if k in r["filtering"]:
                        params += '&{}__exact={}'.format(k,keys[k])
                else:
                    params += '&{}__exact={}'.format(k,keys[k])

        try:
            full_path = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']+params
        except ValueError:
            raise ValueError("Missing wafer-thin-mint client/table")
        except Exception as e:
            raise e

        try:
            result = requests.get(host+full_path, data=body, timeout=TIMEOUT)
        except Exception as e:
            raise e

    elif method == 'post':
        try:
            full_path = settings.WAFER_THIN_MINT['client']['tables'][table]+settings.WAFER_THIN_MINT['client']['suffix']
            body = json.dumps(keys)
            result = requests.post(host+full_path, data=body, timeout=TIMEOUT)
        except ValueError:
            raise ValueError("Missing wafer-thin-mint client/table")
        except Exception as e:
            raise e

    elif method == 'put':
        try:
            full_path = resource+settings.WAFER_THIN_MINT['client']['suffix']
            body = json.dumps(keys)
            result = requests.put(host+full_path, data=body, timeout=TIMEOUT)
        except ValueError:
            raise ValueError("Missing wafer-thin-mint client")
        except Exception as e:
            raise e

    elif method == 'delete':
        try:
            full_path = resource+settings.WAFER_THIN_MINT['client']['suffix']
            body = json.dumps(keys)
            result = requests.delete(host+full_path, data=body, timeout=TIMEOUT)
        except ValueError:
            raise ValueError("Missing wafer-thin-mint client")
        except Exception as e:
            raise e
    else:
        raise AttributeError('Unrecognised transport method')

    try:
        code = result.status_code
    except KeyError as e:
        raise e
    except Exception as e:
        raise e

    if code == 201:
        # then we created an object..
        try:
            body = result.headers['location']
        except Exception as e:
            raise e
    elif code == 204:
        body = None
    elif code == 410:
        raise StandardError('Cannot fetch/delete as resource is already gone')
    elif code == 500 or code == 501:
        if method=='post':
            # item already exists or bad form
            raise Exception('Cannot create, possible unique reference or other SQL related prevention')
        elif method == 'put':
            raise Exception('Cannot save record')
        else:
            # just bad form
            raise Exception('Unable to fetch row, may be due to improperly setup mapping URLs or bad lookup')
    else:
        if 'objects' in json.loads(result.content):
            try:
                body = json.loads(result.content)['objects']
            except Exception as e:
                raise e
        else:
            body = None

    return code, body, result