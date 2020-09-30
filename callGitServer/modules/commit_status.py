''' Update Commit Status Module '''
from models.gitServer import GitServer

def update_commit_status( host, token, commitHash, status, buildUrl, sslVerify, **kwargs ):
    ''' Updates the commit status of the passed commit '''

    gitHandler = GitServer( host, sslVerify, **kwargs )
    gitHandler.update_commit_status( token, commitHash, status, buildUrl, **kwargs )