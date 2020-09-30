import argparse
from modules.utils import PATH_SRC, PATH_SRC_RETRIEVED, PATH_DESCRIBE

def parseArgs():

	parser = argparse.ArgumentParser()
	
	parser.add_argument( '-s', '--srcPath', help='Path where src is located' )
	parser.add_argument( '-r', '--srcRetrievedPath', help='Path where retrieved package is located' )
	parser.add_argument( '-d', '--describePath', help='Path where describe.log is located' )
	args = parser.parse_args()
	
	checkArgs( args )

	return args

def checkArgs( args ):
	if not args.srcPath:
		args.srcPath = PATH_SRC
	if not args.srcRetrievedPath:
		args.srcRetrievedPath = PATH_SRC_RETRIEVED
	if not args.describePath:
		args.describePath = PATH_DESCRIBE