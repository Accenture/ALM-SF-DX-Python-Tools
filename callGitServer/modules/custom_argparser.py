''' Argparse module '''
import argparse
import os
import re

from modules.utils import ( ENV_BUILD_ID, ENV_BUILD_URL, ENV_JOB_NAME, ENV_TARGET_BRANCH, ENV_WORKSPACE, WARNING_TAG )


def parse_args():
    ''' Arg parser method, initializes the possible subparsers '''
    parser = argparse.ArgumentParser()

    # Global arguments
    subparsers = parser.add_subparsers(help='commands', dest='option')
    subparsers.required = True

    # Version
    subparsers.add_parser('version', help='Returns script version')

    # Create/Update Comment Subparser
    help_string = 'Creates or updates a comment into the passed mergerequest'
    comment_parser(subparsers.add_parser('comment', help=help_string))

    # Updates Commit Status Subparser
    help_string = 'Updates the build status of a commit'
    status_parser(subparsers.add_parser('status', help=help_string))

    # Updates Commit Status Subparser
    help_string = 'Accepts Merge Request, creates a Release Tag & Branch'
    release_parser(subparsers.add_parser('release', help=help_string))

    args = parser.parse_args()

    # Post Validations
    if args.option == 'comment':
        post_comment_parse_validation(args, parser)

    if args.option == 'status':
        post_status_parse_validation(args, parser)

    if args.option == 'release':
        if 'release_branch' not in args or not args.release_branch:
            args.release_branch = f'V/{args.tag_name}'
        post_release_parse_validation(args, parser)

    if 'ssl_verify' in args and not args.ssl_verify:
        print(f'{WARNING_TAG} Not performing SSL verification')

    if 'host' in args and 'force_https' in args and args.force_https:
        old_host = args.host
        args.host = re.sub('^http://', 'https://', args.host)
        if old_host != args.host:
            print( f"{WARNING_TAG} Redirecting Git host from '{old_host}' to '{args.host}'" )

    return args

def post_comment_parse_validation(args, parser):
    ''' Post Comment Validation Errors '''
    missing_args = []
    if not args.build_id:
        missing_args.append( ( f'${ENV_BUILD_ID}', 'Build Id' ) )
    if not args.workspace:
        missing_args.append( ( f'${ENV_WORKSPACE}', 'Workspace' ) )
    if missing_args:
        missing_args_list   = [ f'{value} ({key})' for key, value in missing_args ]
        missing_args_str    = '; '.join( missing_args_list )
        parser.error( f'Missing arguments not present as env variables: {missing_args_str}' )

def post_status_parse_validation(args, parser):
    ''' Post Comment Validation Errors '''
    missing_args = []
    if not args.build_url:
        missing_args.append( ( f'${ENV_BUILD_URL}', 'Build URL' ) )
    if not args.build_id:
        missing_args.append( ( f'${ENV_BUILD_ID}', 'Build Id' ) )
    if not args.job_name:
        missing_args.append( ( f'${ENV_JOB_NAME}', 'Job Name' ) )
    if missing_args:
        missing_args_list   = [ f'{value} ({key})' for key, value in missing_args ]
        missing_args_str    = '; '.join( missing_args_list )
        parser.error( f'Missing arguments not present as env variables: {missing_args_str}' )

def post_release_parse_validation(args, parser):
    ''' Post Comment Validation Errors '''
    missing_args = []
    if not args.target_branch:
        missing_args.append( ( f'${ENV_TARGET_BRANCH}', 'Target Branch' ) )
    if missing_args:
        missing_args_list   = [ f'{value} ({key})' for key, value in missing_args ]
        missing_args_str    = '; '.join( missing_args_list )
        parser.error( f'Missing arguments not present as env variables: {missing_args_str}' )

def comment_parser(parser):
    ''' Adds general credentials arguments to passed parser '''
    parser.add_argument( '-b', '--build-id', default=os.environ.get( ENV_BUILD_ID ), help='Current build id' )
    parser.add_argument( '-e', '--edit', action='store_true', help='Launch in append instead of clear mode' )
    parser.add_argument( '-m', '--message', required=True, nargs='*', help='Message content (edit = append to last message)' )
    parser.add_argument( '-mr', '--merge-request-iid', required=True, help='Merge Request project identifier' )
    parser.add_argument( '-w', '--workspace', default=os.environ.get( ENV_WORKSPACE ), help='Workspace Path' )
    parser.add_argument( '-t', '--token', required=True, help='Git API Token (required)' )
    parser.add_argument( '-ns', '--no-ssl', action='store_false', dest='ssl_verify', help='Flag to verify the SSL in requests' )
    parser.add_argument( '-fh', '--force-https', action='store_true', help='Flag to force https Git host' )
    parser.add_argument( '-p', '--project', required=True, help='Project Id (Gitlab) or Project Name (Bitbucket/Azure DevOps) identifier' )
    parser.add_argument( '-o', '--owner', help='Owner (Bitbucket) identifier or Organization (Azure DevOps)' )
    parser.add_argument( '-r', '--host', required=True, help='Repository host' )
    parser.add_argument( '-bs', '--bitbucketServer', type=checkBoolean, default=False, help='Flag to use Bitbucket Server' )
    parser.add_argument( '-ri', '--repositoryId', help='Repository for Azure DevOps' )
    parser.add_argument( '-ti', '--threadId', help='Thread Id for Azure DevOps' )
    parser.add_argument( '-ts', '--threadStatus', help='Thread status for Azure DevOps' )


def status_parser(parser):
    ''' Adds validate notification arguments to passed parser '''
    parser.add_argument( '-t', '--token', required=True, help='Git API Token' )
    parser.add_argument( '--status', '-s', required=True, help='New build status of the commit' )
    parser.add_argument( '--commit', '-c', required=True, help='Commit to update' )
    parser.add_argument( '--build_url', '-b', default=os.environ.get( ENV_BUILD_URL ), help='Commit to update' )
    parser.add_argument( '--job-name', '-j', default=os.environ.get( ENV_JOB_NAME ), help='Job Name' )
    parser.add_argument( '-ns', '--no-ssl', action='store_false', dest='ssl_verify', help='Flag to verify the SSL in requests' )
    parser.add_argument( '-fh', '--force-https', action='store_true', help='Flag to force https Git host' )
    parser.add_argument( '--description', '-d', default=None,  help='Description for Bitbucket builds' )
    parser.add_argument( '-bid', '--build-id', default=os.environ.get( ENV_BUILD_ID ), help='Current build id' )
    parser.add_argument( '-p', '--project', required=True, help='Project Id (Gitlab) or Project Name (Bitbucket) identifier' )
    parser.add_argument( '-o', '--owner', help='Owner (Bitbucket) identifier' )
    parser.add_argument( '-r', '--host', required=True, help='Repository host' )
    parser.add_argument( '-bs', '--bitbucketServer', type=checkBoolean, default=False, help='Flag to use Bitbucket Server' )


def release_parser(parser):
    ''' Parser for release option '''
    parser.add_argument( '-to', '--token', help='Git API Token (required if not using git terminal)' )
    parser.add_argument( '-mr', '--merge-request-iid', default=None, help='Merge Request project identifier' )
    parser.add_argument( '-t', '--target-branch', default=os.environ.get( ENV_TARGET_BRANCH ), help='Merge Request Target Branch' )
    parser.add_argument( '-tn', '--tag_name', required=True, help='Name for creating the tag and branch' )
    parser.add_argument( '-rb', '--release_branch', help='Name for the release branch, default=V/{tag_name}' )
    parser.add_argument( '-m', '--message', help='Tag Message' )
    parser.add_argument( '-rd', '--release_description', help='Tag Release Description' )
    parser.add_argument( '-ns', '--no-ssl', action='store_false', dest='ssl_verify', help='Flag to verify the SSL in requests' )
    parser.add_argument( '-fh', '--force-https', action='store_true', help='Flag to force https Git host' )
    parser.add_argument( '-gt', '--git-terminal', action='store_true', help='Flag to run by Terminal Git' )
    parser.add_argument( '-p', '--project', required=True, help='Project Id (Gitlab) or Project Name (Bitbucket) identifier' )
    parser.add_argument( '-o', '--owner', help='Owner (Bitbucket) identifier' )
    parser.add_argument( '-r', '--host', required=True, help='Repository host' )
    parser.add_argument( '-bs', '--bitbucketServer', type=checkBoolean, default=False, help='Flag to use Bitbucket Server' )


def checkBoolean(value):
    return ( value.lower() == 'true' )
