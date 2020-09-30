''' HTTP Response wrapper '''

class HttpResponse:

    def __init__( self, statusCode, message, reason, responseBody ):
        self.statusCode     = statusCode
        self.message        = message
        self.reason         = reason
        self.responseBody   = responseBody

    def __repr__( self ):
        return ( f'<HttpResponse, {self.reason} ({self.statusCode})>' )