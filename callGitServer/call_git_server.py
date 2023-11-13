''' Call Git Server Method '''
import sys

from models.exceptions import CallGitServerException
from modules.custom_argparser import parse_args
from modules.commit_status import update_commit_status
from modules.mergerequest_comment import add_comment, edit_comment
from modules.create_release import create_release
from modules.utils import ERROR_LINE
from modules.mergerequest_approve import approve

__version__ = '1.4.5'

def handle_options( args ):
    ''' Switcher for different options '''
    if args.option == 'version':
        print( __version__ )
        sys.exit( 0 )
    elif args.option == 'comment':
        if args.edit:
            edit_comment( args.host, args.token, args.merge_request_iid, args.message,
                             args.build_id, args.workspace, args.ssl_verify,region=args.region, before_commit_id=args.before_commit_id,
                             after_commit_id= args.after_commit_id, projectId=args.project,
                             owner=args.owner, projectName=args.project, isBitbucketServer=args.bitbucketServer,
                             threadId=args.threadId, threadStatus=args.threadStatus,  repositoryId=args.repositoryId)
        else:
            add_comment( args.host, args.token, args.merge_request_iid, args.message,
                             args.build_id, args.workspace, args.ssl_verify, region=args.region, before_commit_id=args.before_commit_id,
                             after_commit_id= args.after_commit_id, projectId=args.project, 
                             threadStatus=args.threadStatus,owner=args.owner, projectName=args.project, isBitbucketServer=args.bitbucketServer,  repositoryId=args.repositoryId)
    elif args.option == 'status':
        update_commit_status( args.host, args.token, args.commit, args.status, args.build_url,
                                args.ssl_verify, projectId=args.project, projectName=args.project,
                                owner=args.owner, buildId=args.build_id, description=args.description,
                                jobName=args.job_name, isBitbucketServer=args.bitbucketServer )
    elif args.option == 'release':
        create_release( args.host, args.token, args.tag_name, args.release_branch, args.target_branch, args.ssl_verify,
                        projectId=args.project, projectName=args.project, owner=args.owner,
                        message=args.message, releaseDescription=args.release_description, gitTerminal=args.git_terminal,
                        isBitbucketServer=args.bitbucketServer )
    elif args.option == 'approve':
        approve(args.host, args.token, args.merge_request_iid,
                    args.userSlug, args.ssl_verify,region=args.region, projectId=args.project, 
                    owner=args.owner, projectName=args.project, isBitbucketServer=args.bitbucketServer
                    )

def main():
    ''' Main Method '''
    try:
        args = parse_args()
        handle_options( args )
    except CallGitServerException as gitException:
        print( f'{ERROR_LINE} {gitException}' )
        sys.exit( gitException.STATUS_CODE )

if __name__ == '__main__':
    main()
