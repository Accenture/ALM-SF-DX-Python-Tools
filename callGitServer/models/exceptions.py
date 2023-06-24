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

class ApproveSameUserAsCreated(CallGitServerException):
    ''' Exception throwed when the approver is the same than the Pull request creator '''
    STATUS_CODE = 129

    def __init__(self):
        message = f'The approval cannot be applied because the user approving the pull request matches the user who created the pull request. You cannot approve a pull request that you created.'
        super().__init__( self, message )
        