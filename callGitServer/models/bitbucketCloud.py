''' Bitbucket Server Interface '''
import json
from modules.utils import INFO_TAG, WARNING_TAG, ERROR_LINE, print_key_value_list
from modules.git_server_callout import http_request
from modules.comment_operations import get_last_comment, append_new_comments, save_comment_to_file

class BitbucketCloud():

	def __init__(self, host, owner, projectName):
		self.host			= host
		self.owner			= owner
		self.projectName	= projectName

	def create_branch(self, sslVerify, token, branchName, commitHash, **kwargs):
		''' Method for creating new branch '''

		url     = ( f'{self.host}/api/2.0/repositories/{self.owner}/{self.projectName}/refs/branches' )
		headers = { 'authorization' : f'Basic {token}', 'Content-Type' : 'application/json' }
		payload = { 'name' : branchName, 'target': { 'hash' : commitHash } }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Creating branch:', [ 
			( 'Remote URL', self.host ), ( 'Owner', self.owner ), ( 'Project Name', self.projectName ), 
			( 'Branch Name', branchName ), ( 'Source Ref', commitHash ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			print( f'{INFO_TAG} Branch \'{branchName}\' created' )
		else:
			print( f'{WARNING_TAG} Branch \'{branchName}\' not created. Status code: {response.statusCode}' )

	def create_tag(self, sslVerify, token, tagName, commitHash, **kwargs):
		''' Method for creating new tag '''

		url     = ( f'{self.host}/api/2.0/repositories/{self.owner}/{self.projectName}/refs/tags' )
		headers = { 'authorization' : f'Basic {token}', 'Content-Type' : 'application/json' }
		payload = { 'name' : tagName, 'target' : { 'hash' : commitHash } }
		payload = json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Creating tag with:', [ 
			( 'Remote URL', self.host ), ( 'Owner', self.owner ), ( 'Project Name', self.projectName ), 
			( 'Tag Name', tagName ), ( 'Ref', commitHash ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			print( f'{INFO_TAG} Tag Created' )
		else:
			print( f'{WARNING_TAG} TAG \'{tagName}\' not created. Status code: {response.statusCode}' )

	def update_commit_status(self, sslVerify, token, commitHash, status, buildUrl, **kwargs):
		''' Updates the commit status '''

		url		= ( f'{self.host}/api/2.0/repositories/{self.owner}/{self.projectName}/commit/{commitHash}/statuses/build' )
		headers	= { 'authorization' : f'Basic {token}', 'Content-Type' : 'application/json' }
		payload	= { 'url' : buildUrl, 'state' : status, 'key' : f'BUILD_{commitHash}' }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Updating commit status:', [ 
			( 'Host URL', self.host ), ( 'Commmit SHA', commitHash ), ( 'Status', status ), 
			( 'Build URL', buildUrl ), ( 'Endpoint', url ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			print( f'{SUCCESS_LINE} Commit status updated Successfully' )
		else:
			print( f'{ERROR_LINE} Could not update commit status' )

	def add_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		''' Adds a new comment to the pull request '''

		commentBody	= ' '.join( newComments )

		url		= ( f'{self.host}/api/2.0/repositories/{self.owner}/{self.projectName}/pullrequests/{pullRequestId}/comments' )
		headers	= { 'Authorization' : f'Basic {token}', 'Content-Type' : 'application/json' }
		payload	= { 'content' : { 'raw' : commentBody } }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )
		
		print_key_value_list( f'{INFO_TAG} Adding new Comment to:', [
			( 'Host URL', self.host ), ( 'Owner', self.owner ), ( 'Project Name', self.projectName ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			commentId = str( response.responseBody[ 'id' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not create comment on pull request ({response.responseBody} -- {response.statusCode})' )

	def edit_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		''' Appends message to the pull request's comments '''

		commentId, lastComments	= get_last_comment( workspace, buildId )
		commentBody				= append_new_comments( newComments, lastComments )

		url		= ( f'{self.host}/api/2.0/repositories/{self.owner}/{self.projectName}/pullrequests/{pullRequestId}/comments/{commentId}' )
		headers	= { 'Authorization' : f'Basic {token}', 'Content-Type' : 'application/json' }
		payload	= { 'content' : { 'raw' : commentBody } }
		payload	= json.dumps( payload )
		data	= payload.encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Edditing Comment to:', [
			( 'Host URL', self.host ), ( 'Owner', self.owner ), ( 'Project Name', self.projectName ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'PullRequest Id', pullRequestId )
		] )

		response = http_request( url, data, headers, 'PUT', sslVerify )

		if response.statusCode == 200:
			commentId = str( response.responseBody[ 'id' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not edit comment on pull request ({response.responseBody} -- {response.statusCode})' )