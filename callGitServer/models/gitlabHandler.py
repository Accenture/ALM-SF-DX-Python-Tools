''' Bitbucket Server Interface '''
import urllib
from modules.utils import INFO_TAG, WARNING_TAG, ERROR_LINE, SUCCESS_LINE, print_key_value_list
from modules.git_server_callout import http_request
from modules.comment_operations import get_last_comment, append_new_comments, save_comment_to_file

class GitlabHandler():

	def __init__(self, host, projectId):
		self.host		= host
		self.projectId	= projectId

	def create_branch(self, sslVerify, token, branchName, commitHash, **kwargs):
		''' Method for creating new branch '''

		url		= ( f'{self.host}/api/v4/projects/{self.projectId}/repository/branches' )
		headers	= { 'Private-Token' : token }
		payload	= { 'branch' : branchName, 'ref' : commitHash }
		data	= urllib.parse.urlencode( payload ).encode( "utf-8" )

		print_key_value_list( f'{INFO_TAG} Creating branch:', [ 
			( 'Remote URL', self.host ), ( 'Project Id', self.projectId ),  
			( 'Branch Name', branchName ), ( 'Source Ref', commitHash ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			print( f'{INFO_TAG} Branch \'{branchName}\' created' )
		else:
			print( f'{WARNING_TAG} Branch \'{branchName}\' not created. Status code: {response.statusCode}' )

	def create_tag(self, sslVerify, token, tagName, commitHash, **kwargs):
		''' Method for creating new tag '''

		message				= kwargs[ 'message' ]
		releaseDescription	= kwargs[ 'releaseDescription' ]

		url		= ( f'{self.host}/api/v4/projects/{self.projectId}/repository/tags' )
		headers	= { 'Private-Token' : token }
		payload	= { 'tag_name' : tagName, 'ref' : commitHash, 'message' : message, 'release_description' : releaseDescription }
		data	= urllib.parse.urlencode( payload ).encode( "utf-8" )

		print_key_value_list( f'{INFO_TAG} Creating tag with:', [ 
			( 'Remote URL', self.host ), ( 'Project Id', self.projectId ), ( 'Tag Name', tagName ),
			( 'Ref', commitHash ), ( 'Message', message ), ( 'Description', releaseDescription ), ( 'Endpoint', f'{url}' ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			print( f'{INFO_TAG} Tag Created' )
		else:
			print( f'{WARNING_TAG} TAG \'{tagName}\' not created. Status code: {response.statusCode}' )

	def update_commit_status(self, sslVerify, token, commitHash, status, buildUrl, **kwargs):
		''' Updates the commit status '''

		jobName	= kwargs[ 'jobName' ]

		url		= ( f'{self.host}/api/v4/projects/{self.projectId}/statuses/{commitHash}' )
		headers	= { 'Private-Token' : token }
		payload	= { 'state' : status, 'target_url' : buildUrl, 'name' : jobName }
		data	= urllib.parse.urlencode( payload ).encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Updating commit status:', [ 
			( 'Host URL', self.host ), ( 'Commmit SHA', commitHash ), ( 'Status', status ), 
			( 'Build URL', buildUrl ), ( 'Endpoint', url ) 
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 200:
			print( f'{SUCCESS_LINE} Commit status updated Successfully' )
		else:
			print( f'{ERROR_LINE} Could not update commit status' )

	def add_comment(self, sslVerify, token, mergeRequestId, newComments, buildId, workspace, **kwargs):
		''' Adds a new comment to the merge request '''

		commentBody	= ' '.join( newComments )

		url		= ( f'{self.host}/api/v4/projects/{self.projectId}/merge_requests/{mergeRequestId}/notes' )
		payload	= { 'body': commentBody }
		headers	= { 'Private-Token': token }
		data	= urllib.parse.urlencode( payload ).encode( 'utf-8' )
		
		print_key_value_list( f'{INFO_TAG} Adding new Comment to:', [
			( 'Host URL', self.host ), ( 'Project Id', self.projectId ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'MergeRequest Id', mergeRequestId )
		] )

		response = http_request( url, data, headers, 'POST', sslVerify )

		if response.statusCode == 201:
			commentId = str( response.responseBody[ 'id' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not create comment on merge request ({response.responseBody} -- {response.statusCode})' )

	def edit_comment(self, sslVerify, token, mergeRequestId, newComments, buildId, workspace, **kwargs):
		''' Appends message to the merge request's comments '''

		commentId, lastComments	= get_last_comment( workspace, buildId )
		commentBody				= append_new_comments( newComments, lastComments )

		url		= ( f'{self.host}/api/v4/projects/{self.projectId}/merge_requests/{mergeRequestId}/notes/{commentId}' )
		payload	= { 'body': commentBody }
		headers	= { 'Private-Token': token }
		data	= urllib.parse.urlencode( payload ).encode( 'utf-8' )

		print_key_value_list( f'{INFO_TAG} Edditing Comment to:', [
			( 'Host URL', self.host ), ( 'Project Id', self.projectId ), 
			( 'Target Endpoint', url), ( 'Comment', commentBody ), ( 'MergeRequest Id', mergeRequestId )
		] )

		response = http_request( url, data, headers, 'PUT', sslVerify )

		if response.statusCode == 200:
			commentId = str( response.responseBody[ 'id' ] )
			save_comment_to_file( commentBody, buildId, commentId, workspace )
			print( f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt' )
		else:
			print( f'{ERROR_LINE} Could not edit comment on merge request ({response.responseBody} -- {response.statusCode})' )