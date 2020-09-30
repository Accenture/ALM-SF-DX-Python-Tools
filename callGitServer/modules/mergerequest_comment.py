''' Module to comment of Merge Requests '''
from models.gitServer import GitServer

def add_comment(host, token, mergeRequestId, newComments, buildId, workspace, sslVerify, **kwargs):
    ''' Adds a new comment to the merge request '''

    gitHandler = GitServer( host, sslVerify, **kwargs )
    gitHandler.add_comment( token, mergeRequestId, newComments, buildId, workspace, **kwargs )

def edit_comment(host, token, mergeRequestId, newComments, buildId, workspace, sslVerify, **kwargs):
    ''' Appends comment to a previous one '''

    gitHandler = GitServer( host, sslVerify, **kwargs )
    gitHandler.edit_comment( token, mergeRequestId, newComments, buildId, workspace, **kwargs )