''' Module to comment of Merge Requests '''
from models.gitServer import GitServer

def approve(host, token, mergeRequestId, userSlug, sslVerify, **kwargs):
    ''' Approve Pull Request  '''
    gitHandler = GitServer(host, sslVerify, **kwargs)
    gitHandler.approve_pull_request(token, mergeRequestId, userSlug, **kwargs )
