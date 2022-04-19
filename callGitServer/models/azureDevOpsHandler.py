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

		threadStatus = kwargs[ 'threadStatus' ] if ( 'threadStatus' in kwargs and kwargs[ 'threadStatus' ] ) else 1

		url		= f'{self.host}/{self.organization}/{self.projectName}/_apis/git/repositories/{self.repositoryId}/pullRequests/{pullRequestId}/threads?api-version=6.0'
		payload	= { 'comments': [ { 'parentCommentId': 0, 'content': commentBody, 'commentType': 1 } ], 'status' : threadStatus }
		headers	= { 'Authorization': f'Basic {token}', 'Content-Type' : 'application/json' }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'Adding new Thread to:', [
			( 'Host URL', self.host ), ( 'Project', self.projectName ),
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 200:
			commentId = response.responseBody[ 'id' ]
			print( f'Thread created succesfully with id \'{commentId}\'' )
			print( f'##vso[task.setvariable variable=pr_thread_id]{commentId}' )
		else:
			print( f'Could not create thread on pull request {pullRequestId} ({response.responseBody} -- {response.statusCode})' )


	def edit_comment(self, sslVerify, token, pullRequestId, commentBody, buildId, workspace, **kwargs):
		#self.update_thread(sslVerify, token, pullRequestId, commentBody, **kwargs)
		self.update_comment(sslVerify, token, pullRequestId, commentBody, **kwargs)


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
			print( f'Could not create thread on pull request {pullRequestId} ({response.responseBody} -- {response.statusCode})' )


	def update_comment(self, sslVerify, token, pullRequestId, commentBody, **kwargs):
		''' Edits the first comment of the thread, adds new comment '''

		token = base64.b64encode( bytes( f':{token}', 'utf-8' ) ).decode( 'ascii' )
		threadId = kwargs[ 'threadId' ]
		url = f'{self.host}/{self.organization}/{self.projectName}/_apis/git/repositories/{self.repositoryId}/pullRequests/{pullRequestId}/threads/{threadId}/comments/1?api-version=6.0'
		headers	= { 'Authorization': f'Basic {token}', 'Content-Type' : 'application/json' }

		# Get content of previous comment
		previousPayload = json.dumps( {} )
		previousData	= previousPayload.encode( 'utf-8' )

		previousResponse = http_request(url, previousData, headers, 'GET', sslVerify)

		if previousResponse.statusCode != 200:
			print( f'Could not edit previous comment in thread of pull request {pullRequestId} ({previousResponse.responseBody} -- {previousResponse.statusCode})' )

		previousContent = previousResponse.responseBody['content']
		content = f'{previousContent}\n{commentBody[0]}'

		# Add previous content + new content
		payload = { 'content' : content }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		response = http_request( url, data, headers, 'PATCH', sslVerify )

		if response.statusCode == 200:
			print( f'Thread updated succesfully' )
		else:
			print( f'Could not update comment on pull request {pullRequestId} ({response.responseBody} -- {response.statusCode})' )
