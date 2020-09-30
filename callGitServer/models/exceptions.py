''' Exception module '''


class CallGitServerException(Exception):
    ''' Base Exception for filtering Call Git Server Exceptions '''
    STATUS_CODE = 127


class DuplicateRemote(CallGitServerException):
    ''' Exception throwed when there arent any match with the username '''
    STATUS_CODE = 128

    def __init__(self, name, branchRef, elementType):
        if 'Tag' in elementType:
            message = f'{elementType}: {name} on \"{branchRef}\" Already exist.'
        else:
            message = f'{elementType}: {name} Already exist.'
        super().__init__( self, message )