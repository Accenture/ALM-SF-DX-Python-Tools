''' Bitbucket Server Interface '''
import json
import urllib
import base64
from modules.utils import print_key_value_list
from modules.git_server_callout import http_request

class AzureDevOpsHandler():

	def __init__(self, host, organization, projectName, repositoryId):
		self.host			= host
		self.organization	= organization
		self.projectName	= projectName
		self.repositoryId	= repositoryId


	def add_comment(self, sslVerify, token, pullRequestId, commentBody, buildId, workspace, **kwargs):
		self.create_thread(sslVerify, token, pullRequestId, commentBody, **kwargs)


	def create_thread(self, sslVerify, token, pullRequestId, commentBody, **kwargs):
		''' Adds a new comment to the merge request '''

		token = base64.b64encode( bytes( f':{token}', 'utf-8' ) ).decode( 'ascii' )
		commentBody = commentBody[ 0 ]

		url		= f'{self.host}/{self.organization}/{self.projectName}/_apis/git/repositories/{self.repositoryId}/pullRequests/{pullRequestId}/threads?api-version=6.0'
		payload	= { 'comments': [ { 'parentCommentId': 0, 'content': commentBody, 'commentType': 1 } ], 'status' : 1 }
		headers	= { 'Authorization': f'Basic {token}', 'Content-Type' : 'application/json' }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )
		
		print_key_value_list( f'Adding new Thread to:', [
			( 'Host URL', self.host ), ( 'Project', self.projectName ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )
		print( response )

		if response.statusCode == 200:
			commentId = response.responseBody[ 'id' ]
			print( f'Thread created succesfully with id \'{commentId}\'' )
		else:
			print( f'Could not create threat on pull request {pullRequestId} ({response.responseBody} -- {response.statusCode})' )


	def edit_comment(self, sslVerify, token, pullRequestId, commentBody, buildId, workspace, **kwargs):
		self.update_thread(sslVerify, token, pullRequestId, commentBody, **kwargs)


	def update_thread(self, sslVerify, token, pullRequestId, commentBody, **kwargs):
		''' Adds a new comment to the merge request '''

		token = base64.b64encode( bytes( f':{token}', 'utf-8' ) ).decode( 'ascii' )
		commentBody = commentBody[ 0 ]
		threadId = kwargs[ 'threadId' ]

		url		= f'{self.host}/{self.organization}/{self.projectName}/_apis/git/repositories/{self.repositoryId}/pullRequests/{pullRequestId}/threads/{threadId}?api-version=6.0'
		payload	= { 'comments': [ { 'parentCommentId': 0, 'content': commentBody, 'commentType': 1 } ], 'status' : kwargs[ 'threadStatus' ] }
		headers	= { 'Authorization': f'Basic {token}', 'Content-Type' : 'application/json' }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )
		
		print_key_value_list( f'Adding new Thread to:', [
			( 'Host URL', self.host ), ( 'Project', self.projectName ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'PATCH', sslVerify )

		if response.statusCode == 200:
			print( f'Thread updated succesfully' )
		else:
			print( f'Could not create threat on pull request {pullRequestId} ({response.responseBody} -- {response.statusCode})' )