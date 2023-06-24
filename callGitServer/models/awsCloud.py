''' AWS Client Interface '''
import boto3
from modules.comment_operations import get_last_comment, append_new_comments, save_comment_to_file
from modules.utils import INFO_TAG, WARNING_TAG, ERROR_LINE, SUCCESS_LINE, print_key_value_list
from models.exceptions import ApproveSameUserAsCreated
from botocore.exceptions import ClientError

class awsCloud():
	def __init__(self, host, region, repository):
		self.host		= host
		self.region		= region
		self.repository = repository

	def get_aws_credentials_from_token(self, token):
		aws_access_key_id, aws_secret_access_key = token.split(" ")
		return aws_access_key_id, aws_secret_access_key

	def create_codecommit_client(self, region, aws_access_key_id, aws_secret_access_key):
		"""
		Creates a client to interact with the CodeCommit service.

		:param region: AWS region.
		:type region: str
		:param aws_access_key_id: AWS access key ID.
		:type aws_access_key_id: str
		:param aws_secret_access_key: AWS secret access key.
		:type aws_secret_access_key: str
		:return: CodeCommit client.
		:rtype: boto3.client
		"""
		# Create a client to interact with the CodeCommit service
		client = boto3.client(
			'codecommit',
			region_name=region,
			aws_access_key_id=aws_access_key_id,
			aws_secret_access_key=aws_secret_access_key
		)
		
		return client


	def add_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		"""
		Adds a new comment to an AWS CodeCommit pull request.

		:param sslVerify: SSL verification.
		:type sslVerify: bool
		:param token: AWS token.
		:type token: str
		:param pullRequestId: Pull request ID.
		:type pullRequestId: str
		:param newComments: New comments to add to the pull request.
		:type newComments: list of str
		:param buildId: Build ID.
		:type buildId: str
		:param workspace: Workspace path.
		:type workspace: str
		:param kwargs: Additional arguments.
		:type kwargs: dict
		"""
		# Get AWS credentials from token
		aws_access_key_id, aws_secret_access_key = self.get_aws_credentials_from_token(token)
		
    	# Create a client to interact with the CodeCommit service
		client = self.create_codecommit_client(kwargs["region"], aws_access_key_id, aws_secret_access_key)

		# Set up the details of the Pull Request and the comment
		repository_name = self.repository
		pull_request_id = str(pullRequestId)
		comment = "".join(newComments)
		
		# Post a comment on the Pull Request
		response = client.post_comment_for_pull_request(
			pullRequestId=pull_request_id,
			repositoryName=repository_name,
			beforeCommitId=kwargs["before_commit_id"],
			afterCommitId=kwargs["after_commit_id"],
			content=comment
		)

		# Check if the operation was successful
		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			# Print the comment ID and save the comment to a local file
			print(response['comment']['commentId'])
			commentId = str(response['comment']['commentId'])
			save_comment_to_file(comment, buildId, commentId, workspace)
			print(f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt')
		else:
			print(f'{ERROR_LINE} Could not create comment on pull request ({pull_request_id} -- {response["ResponseMetadata"]["HTTPStatusCode"]})')

	def edit_comment(self, sslVerify, token, pullRequestId, newComments, buildId, workspace, **kwargs):
		"""
			Edits the latest comment on an AWS CodeCommit pull request.

			:param sslVerify: SSL verification.
			:type sslVerify: bool
			:param token: AWS token.
			:type token: str
			:param pullRequestId: Pull request ID.
			:type pullRequestId: str
			:param newComments: New comments to append to the existing comment.
			:type newComments: list of str
			:param buildId: Build ID.
			:type buildId: str
			:param workspace: Workspace path.
			:type workspace: str
			:param kwargs: Additional arguments.
			:type kwargs: dict
		"""
		# Get the ID and content of the latest comment
		commentId, lastComments = get_last_comment(workspace, buildId)
		
		# Append the new comments to the content of the latest comment
		commentBody = append_new_comments(newComments, lastComments)
	
		# Get AWS credentials from token
		aws_access_key_id, aws_secret_access_key = self.get_aws_credentials_from_token(token)
		
    	# Create a client to interact with the CodeCommit service
		client = self.create_codecommit_client(kwargs["region"], aws_access_key_id, aws_secret_access_key)


		# Set up the details of the Pull Request and the comment
		repository_name = self.repository
		pull_request_id = str(pullRequestId)
		
		# Update the existing comment on the Pull Request
		response = client.update_comment(
			content=commentBody,
			commentId=commentId
		)

		# Print information about the edited comment
		print_key_value_list(f'{INFO_TAG} Edditing Comment to:', [
			('Host URL', self.host),
			('Repository', self.repository),
			('Comment', commentBody),
			('PullRequest Id', pull_request_id),
			('Comment Id', commentId)
		])
		
		# Check if the operation was successful
		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			# Save the edited comment to a local file
			save_comment_to_file(commentBody, buildId, commentId, workspace)
			print(f'{SUCCESS_LINE} Comment created succesfully with id \'{commentId}\', saved to ./{buildId}-comment.txt')
		else:
			print(f'{ERROR_LINE} Could not create comment on pull request ({pull_request_id} -- {response["ResponseMetadata"]["HTTPStatusCode"]})')

	def approve_pull_request(self, sslVerify, token, pullRequest_Id, userSlug, **kwargs):
		"""
		Approves an AWS CodeCommit pull request.

		:param sslVerify: SSL verification.
		:type sslVerify: bool
		:param token: AWS token.
		:type token: str
		:param pullRequest_Id: Pull request ID.
		:type pullRequest_Id: str
		:param userSlug: User slug.
		:type userSlug: str
		:param kwargs: Additional arguments.
		:type kwargs: dict
		"""
		# Get AWS credentials from token
		aws_access_key_id, aws_secret_access_key = self.get_aws_credentials_from_token(token)
		
		# Get pull request information
		pr_info = self.get_pull_request_info(pullRequest_Id, kwargs["region"], aws_access_key_id, aws_secret_access_key)

    	# Create a client to interact with the CodeCommit service
		client = self.create_codecommit_client(kwargs["region"], aws_access_key_id, aws_secret_access_key)

		# Update the approval state of the pull request
		try:
			response = client.update_pull_request_approval_state(
				pullRequestId=pullRequest_Id,
				revisionId=pr_info['pullRequest']['revisionId'],
				approvalState='APPROVE'
			)
		except ClientError as e:
			if e.response['Error']['Code'] == 'PullRequestCannotBeApprovedByAuthorException':
				print_key_value_list(f'{ERROR_LINE} Error approving pull request to:', [
					('Host URL', self.host),
					('Repository', self.repository),
					('PullRequest Id', pullRequest_Id),
					('PullRequest Revision Id', pr_info['pullRequest']['revisionId'])
				])
				raise ApproveSameUserAsCreated

		# Print information about the approved pull request
		print_key_value_list(f'{INFO_TAG} Approving pull request to:', [
			('Host URL', self.host),
			('Repository', self.repository),
			('PullRequest Id', pullRequest_Id),
			('PullRequest Revision Id', pr_info['pullRequest']['revisionId'])
		])

		# Check if the operation was successful
		if response['ResponseMetadata']['HTTPStatusCode'] == 200:
			print(f'{SUCCESS_LINE} Pull request approved successfully id {pullRequest_Id}')
		else:
			print(f'{ERROR_LINE} Could not approve pull request ({pullRequest_Id} -- {response.statusCode})')

	def get_pull_request_info(self, pull_request_id, region, aws_access_key_id, aws_secret_access_key):
		"""
		Gets detailed information about an AWS CodeCommit pull request.

		:param pull_request_id: Pull request ID.
		:type pull_request_id: str
		:param region: AWS region.
		:type region: str
		:param aws_access_key_id: AWS access key ID.
		:type aws_access_key_id: str
		:param aws_secret_access_key: AWS secret access key.
		:type aws_secret_access_key: str
		:return: Pull request information.
		:rtype: dict
		"""
		try:
    		# Create a client to interact with the CodeCommit service
			client = self.create_codecommit_client(region, aws_access_key_id, aws_secret_access_key)

			# Get detailed information about the pull request
			response = client.get_pull_request(
				pullRequestId=pull_request_id
			)

			# Return the pull request information
			return response
		except ClientError as e:
			print(f'An error occurred while getting pull request information: {e}')
			return None
