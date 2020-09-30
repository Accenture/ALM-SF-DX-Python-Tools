''' Git Server Callout Module '''
import json
import urllib
import urllib.request
import ssl

from models.httpResponse import HttpResponse

def http_request(url, data, headers, method, sslVerify):
    ''' Utility method for doing http requests with urllib '''

    request = urllib.request.Request( url=url, data=data, headers=headers, method=method )

    try:
        if sslVerify:
            with urllib.request.urlopen( request ) as response:
                responseStatus = response.status
                responseMsg    = response.msg
                responseReason = response.reason
                responseBody   = json.load( response )
        else:
            # Create context to avoid SSL verifications
            ctx                 = ssl.create_default_context()
            ctx.check_hostname  = False
            ctx.verify_mode     = ssl.CERT_NONE
            with urllib.request.urlopen( request, context=ctx ) as response:
                responseStatus  = response.status
                responseMsg     = response.msg
                responseReason  = response.reason
                try:
                    responseBody = json.load( response )
                except Exception as exception:
                    responseBody = {}

    except urllib.error.HTTPError as httpException:
        responseStatus  = httpException.getcode()
        responseMsg     = httpException.msg
        responseReason  = httpException.reason
        responseBody    = {}

    return HttpResponse( responseStatus, responseMsg, responseReason, responseBody )