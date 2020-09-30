''' Module for creating releases '''
from models.gitServer import GitServer

def create_release(host, token, tagName, branchName, commitHash, sslVerify, **kwargs):
    ''' Creates a release (accepts merge + create tag + create branch) '''
    
    gitHandler = GitServer( host, sslVerify, **kwargs )
    gitHandler.create_branch( token, branchName, commitHash, **kwargs )
    gitHandler.create_tag( token, tagName, commitHash, **kwargs )
