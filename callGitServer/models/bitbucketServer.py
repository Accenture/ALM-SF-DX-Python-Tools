''' Bitbucket Server Interface '''
import json
from modules.utils import INFO_TAG, WARNING_TAG, ERROR_LINE, SUCCESS_LINE, print_key_value_list
from modules.git_server_callout import http_request
from modules.comment_operations import get_last_comment, append_new_comments, save_comment_to_file

class BitbucketServer():

	def __init__(self, host, project, repository):
		self.host		= host
		self.project	= project
		self.repository	= repository

	def create_branch(self, sslVerify, token, branchName, commitHash, **kwargs):
		''' Method for creating new branch '''

		url		= ( f'{self.host}/rest/api/1.0/projects/{self.project}/repos/{self.repository}/branches' )
		headers	= { 'Authorization' : f'Bearer {token}', 'Content-Type' : 'application/json' }
		payload	= { 'name' : branchName, 'startPoint' : commitHash }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Creating branch:', [ 
			( 'Remote URL', self.host ), ( 'Project', self.project ), ( 'Repository', self.repository ), 
			( 'Branch Name', branchName ), ( 'Source Ref', commitHash ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 200:
			print( f'{INFO_TAG} Branch \'{branchName}\' created' )
		else:
			print( f'{WARNING_TAG} Branch \'{branchName}\' not created. Status code: {response.statusCode}' )

	def create_tag(self, sslVerify, token, tagName, commitHash, **kwargs):
		''' Method for creating new tag '''

		message	= kwargs[ 'releaseDescription' ]

		url		= ( f'{self.host}/rest/api/1.0/projects/{self.project}/repos/{self.repository}/tags' )
		headers	= { 'Authorization' : f'Bearer {token}', 'Content-Type' : 'application/json' }
		payload	= { 'name' : tagName, 'startPoint' : commitHash, 'message' : message }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Creating tag with:', [ 
			( 'Remote URL', self.host ), ( 'Project', self.project ), ( 'Repository', self.repository ), 
			( 'Tag Name', tagName ), ( 'Ref', commitHash ), ( 'Message', message ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 200:
			print( f'{INFO_TAG} Tag Created' )
		else:
			print( f'{WARNING_TAG} TAG \'{tagName}\' not created. Status code: {response.statusCode}' )

	def update_commit_status(self, sslVerify, token, commitHash, status, buildUrl, **kwargs):
		''' Updates the commit status '''

		description	= kwargs[ 'description' ]
		buildId		= kwargs[ 'buildId' ]

		url			= ( f'{self.host}/rest/build-status/1.0/commits/{commitHash}' )
		headers		= { 'authorization' : f'Bearer {token}', 'Content-Type' : 'application/json' }
		payload		= { 'url' : buildUrl, 'state': status, 'key' : f'BUILD_{buildId}', 'name' : buildId, 'description' : description }
		payload		= json.dumps( payload )
		data		= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Updating commit status:', [ 
			( 'Host URL', self.host ), ( 'Commmit SHA', commitHash ), ( 'Status', status ), 
			( 'Build URL', buildUrl ), ( 'Endpoint', url ), ( 'Description', description ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 204:
			print( f'{SUCCESS_LINE} Commit status updated Successfully' )
		else:
			print( f'{ERROR_LINE} Could not update commit status' )

	def add_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		''' Adds a new comment to the pull request '''

		commentBody	= ' '.join( newComments )

		url			= ( f'{self.host}/rest/api/1.0/projects/{self.project}/repos/{self.repository}/pull-requests/{pullRequestId}/comments' )
		headers		= { 'Authorization' : f'Bearer {token}', 'Content-Type' : 'application/json' }
		payload		= { 'text' : commentBody }
		payload		= json.dumps( payload )
		data		= payload.encode( 'utf-8' )
		
		print_key_value_list( f'{INFO_TAG} Adding new Comment to:', [
			( 'Host URL', self.host ), ( 'Project Name', self.project ), ( 'Repository', self.repository ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			commentId		= str( response.responseBody[ 'id' ] )
			commentVersion	= str( response.responseBody[ 'version' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace, commentVersion )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not create comment on pull request ({response.responseBody} -- {response.statusCode})' )

	def edit_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		''' Appends message to the pull request's comments '''

		commentId, lastComments	= get_last_comment( workspace, buildId )
		commentVersion			= lastComments.pop( 0 ).strip()
		commentBody				= append_new_comments( newComments, lastComments )

		url		= ( f'{self.host}/rest/api/1.0/projects/{self.project}/repos/{self.repository}/pull-requests/{pullRequestId}/comments/{commentId}' )
		payload	= { 'version' : commentVersion, 'text' : commentBody }
		headers	= { 'Authorization' : f'Bearer {token}', 'Content-Type' : 'application/json' }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Edditing Comment to:', [
			( 'Host URL', self.host ), ( 'Project Name', self.project ), ( 'Repository', self.repository ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId ), ( 'Comment Version', commentVersion )
		] )

		response = http_request( url, data, headers, 'PUT', sslVerify )

		if response.statusCode == 200:
			commentId		= str( response.responseBody[ 'id' ] )
			commentVersion	= str( response.responseBody[ 'version' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace, commentVersion )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not edit comment on pull request ({response.responseBody} -- {response.statusCode})' )