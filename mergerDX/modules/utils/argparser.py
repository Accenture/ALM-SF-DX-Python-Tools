''' Argparse Module '''

import sys
import argparse
from modules.utils import DELTA_FOLDER

def parseArgs():
    ''' Parse args '''

    description         = ( 'Merger method that helps and automates the creation of deltas and releases for Salesforce Git Bases projects' )
    parser              = argparse.ArgumentParser( description=description )
    subparsers          = parser.add_subparsers( help='commands', dest='option' )
    subparsers.required = True

    subparsers.add_parser( 'version', help='Returns the version of the script' )

    mergerHelp = ( 'Builds delta package, from the diff between source and target branch after merging them' )
    mergeParser( subparsers.add_parser( 'merge_delta', help=mergerHelp ) )

    buildHelp = ( 'Builds delta package, from the diff between two specified references (commit, tag or branch)' )
    buildParser( subparsers.add_parser( 'build_delta', help=buildHelp ) )

    args = parser.parse_args()

    args.remote_specified = ( 'remote' in args and ( '-r' in sys.argv or '--remote' in sys.argv ) )

    if args.option == 'build_delta':
        if 'target' not in args or not args.target:
            args.target = f'{args.source}~1'

    return args


def mergeParser(subparser):
    ''' Adds arguments for merge subparser '''
    
    subparser.add_argument( '-r', '--remote', default='origin', help='Remote name from which to fetch and checkout, default=\'origin\'' )
    subparser.add_argument( '-s', '--source', required=True, help='Merge source ref, with the code to be merged' )
    subparser.add_argument( '-t', '--target', required=True, help='Merge target ref, changes from source will end here' )
    subparser.add_argument( '-d', '--delta-folder', default=DELTA_FOLDER, help=f'Delta folder name, default={DELTA_FOLDER}' )
    subparser.add_argument( '-a', '--api-version', required=True, type=float, help=f'API Version for delta generation' )
    subparser.add_argument( '-nf', '--no-fetch', default=True, action='store_false', dest='fetch', help='Flag to select if it is necessary to fetch before checkout' )
    subparser.add_argument( '-nr', '--no-reset', default=True, action='store_false', dest='reset', help='Flag to select if it is necessary to hard reset the branches before merge' )
    subparser.add_argument( '-sf', '--source-folder', help=f'Source folder name' )
    subparser.add_argument( '-dsc', '--describe', default='describe.log', help='Path to describe log file' )


def buildParser(subparser):
    ''' Adds arguments for merge subparser '''

    subparser.add_argument( '-r', '--remote', default='origin', help='Remote name from which to fetch and checkout, default=origin' )
    subparser.add_argument( '-b', '--branch', default='develop', help='Branch')  # TODO algo
    subparser.add_argument( '-s', '--source', default='HEAD', help='Merge source ref, with the code to be merged' )
    subparser.add_argument( '-t', '--target', help='Merge target ref, changes from source will end here' )
    subparser.add_argument( '-d', '--delta-folder', default=DELTA_FOLDER, help=f'Delta folder name, default={DELTA_FOLDER}' )
    subparser.add_argument( '-a', '--api-version', required=True, type=float, help=f'API Version for delta generation' )
    subparser.add_argument( '-nf', '--no-fetch', default=True, action='store_false', dest='fetch', help='Flag to select if it is necessary to fetch before checkout' )
    subparser.add_argument( '-nr', '--no-reset', default=True, action='store_false', dest='reset', help='Flag to select if it is necessary to hard reset the branches before merge' )
    subparser.add_argument( '-sf', '--source-folder', help=f'Source folder name' )
    subparser.add_argument( '-dsc', '--describe', default='describe.log', help='Path to describe log file' )
