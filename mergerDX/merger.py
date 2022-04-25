''' Merger module '''
import sys

from modules.delta_builder import buildDelta, mergeDelta
from modules.git.utils import is_commit_user_configured, is_git_repository, is_valid_remote
from modules.utils import FATAL_LINE, SUCCESS_LINE, WARNING_LINE
from modules.utils.argparser import parseArgs
from modules.utils.exceptions import ( CommitUserNotConfigured, InvalidRemoteSpecified, MergerException, 
                                        MergerExceptionWarning, NotAGitRepository )

__version__ = "3.3.1"


def prevalidations(args):

    if not is_git_repository():
        raise NotAGitRepository()

    if args.fetch and not is_valid_remote( args.remote ):
        if args.remote_specified:
            raise InvalidRemoteSpecified( args.remote )
        print( f'{WARNING_LINE} Default remote \'{args.remote}\' does not exist, forcing no fetch' )
        args.fetch = False

    if args.option == 'merge_delta' and not is_commit_user_configured():
        raise CommitUserNotConfigured()


def main():
    ''' Main method '''

    args = parseArgs()
    if args.option == 'version':
        print( __version__ )
        sys.exit( 0 )
    try:
        prevalidations( args )
        if args.option == 'merge_delta':
            mergeDelta( args.source, args.target, args.remote, args.fetch, args.reset, args.delta_folder,
                        args.source_folder, args.api_version, args.describe )
            print( f'{SUCCESS_LINE} Build Delta Package Finished correctly' )

        elif args.option == 'build_delta':
            buildDelta( args.source, args.target, args.remote, args.fetch, args.delta_folder, args.source_folder,
                        args.api_version, args.describe )

    except MergerExceptionWarning as exception:
        print( f'{WARNING_LINE} {exception}, finished with warnings...' )
        print( f'##vso[task.logissue type=warning;]{exception}' )
        sys.exit( exception.ERROR_CODE )
    except MergerException as exception:
        print( f'{FATAL_LINE} {exception}, exiting...' )
        print( f'##vso[task.logissue type=error;]{exception}' )
        sys.exit( exception.ERROR_CODE )


if __name__ == '__main__':
    main()
