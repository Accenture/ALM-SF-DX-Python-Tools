''' Git Server Interface '''
from models.httpResponse import HttpResponse
from models.gitlabHandler import GitlabHandler
from models.bitbucketCloud import BitbucketCloud
from models.bitbucketServer import BitbucketServer
from models.azureDevOpsHandler import AzureDevOpsHandler
from models.exceptions import DuplicateRemote
from modules.utils import ( INFO_TAG, WARNING_TAG, print_key_value_list, call_subprocess )

class GitServer():

	def __init__(self, host, sslVerify, **kwargs):
		self.host		= host
		self.sslVerify	= sslVerify
		self.__get_handler(host, **kwargs)


	def __get_handler(self, host, **kwargs):
		if 'bitbucket' in host and not kwargs[ 'isBitbucketServer' ]:
			self.gitHandler = BitbucketCloud( host, kwargs[ 'owner' ], kwargs[ 'projectName' ] )
		elif 'gitlab' in host:
			self.gitHandler = GitlabHandler( host, kwargs[ 'projectId' ] )
		elif 'dev.azure.com' in host:
			self.gitHandler = AzureDevOpsHandler( host, kwargs[ 'owner' ], kwargs[ 'projectName' ], kwargs[ 'repositoryId' ] )
		else:
			if kwargs[ 'isBitbucketServer' ]:
				self.gitHandler = BitbucketServer( host, kwargs[ 'owner' ], kwargs[ 'projectName' ] )
			else:
				raise Exception( 'Not implemented' )


	def create_branch(self, token, branchName, commitHash, **kwargs):
		if 'gitTerminal' in kwargs and kwargs[ 'gitTerminal' ]:
			self.create_branch_terminal( branchName, commitHash, **kwargs )
		else:
			self.gitHandler.create_branch( self.sslVerify, token, branchName, commitHash, **kwargs )


	def create_tag(self, token, tagName, commitHash, **kwargs):
		if 'gitTerminal' in kwargs and kwargs[ 'gitTerminal' ]:
			self.create_tag_terminal( tagName, commitHash, **kwargs )
		else:
			self.gitHandler.create_tag( self.sslVerify, token, tagName, commitHash, **kwargs )


	def update_commit_status(self, token, commitHash, status, buildUrl, **kwargs ):
		self.gitHandler.update_commit_status( self.sslVerify, token, commitHash, status, buildUrl, **kwargs )


	def add_comment(self, token, mergeRequestId, newComments, buildId, workspace, **kwargs):
		self.gitHandler.add_comment( self.sslVerify, token, mergeRequestId, newComments, buildId, workspace, **kwargs )


	def edit_comment(self, token, mergeRequestId, newComments, buildId, workspace, **kwargs):
		self.gitHandler.edit_comment( self.sslVerify, token, mergeRequestId, newComments, buildId, workspace, **kwargs )


	def create_branch_terminal(self, branchName, commitHash):

		print( f'{INFO_TAG} Flag -gt detected. branch will be created by Git Terminal' )

		print_key_value_list( f'{INFO_TAG} Creating branch with:', [ 
			( 'Remote URL', self.host ), ( 'Branch Name', branchName ), ( 'Source Ref', commitHash )
		] )

		command			= f'git checkout -b {branchName} {commitHash}'
		stdout, code	= call_subprocess( command )
		if code == 128:
			raise DuplicateRemote( branchName, commitHash, 'Branch' )
		
		command			= f'git push origin {branchName}'
		stdout, code	= call_subprocess( command )
		if code == 0:
			print( f'{INFO_TAG} Branch Created' )
		else:
			print( f"{WARNING_TAG} Branch Created but not pushed to remote." )
			raise Exception( code )


	def create_tag_terminal(self, tagName, commitHash):

		print( f'{INFO_TAG} Flag -gt detected. Tag will be created by Git Terminal' )

		print_key_value_list( f'{INFO_TAG} Creating tag with:', [ 
			( 'Remote URL', self.host ), ( 'Tag Name', tagName ), ( 'Ref', commitHash)
		] )
		
		command			= f'git tag {tagName} {commitHash}'
		stdout, code	= call_subprocess( command )
		if code == 128:
			raise DuplicateRemote( tagName, commitHash, 'Tag' )
		
		command      = f'git push origin {tagName}'
		stdout, code = call_subprocess( command )
		if code == 0:
			print( f'{INFO_TAG} Tag Created' )
		else:
			print( f"{WARNING_TAG} Tag Created but not pushed to remote." )
			raise Exception( code )
