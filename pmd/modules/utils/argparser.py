import argparse
from modules.utils import REPORT_FILE, OUTPUT_FILE, SRC_PATH

def parseArgs():

	parser = argparse.ArgumentParser()
	
	parser.add_argument( '-r', '--reportFile', help='Path where PMD report is stored' )
	parser.add_argument( '-o', '--outputFile', help='Path where report will be saved' )
	parser.add_argument( '-s', '--srcPath', help='Path where src is located' )
	args = parser.parse_args()
	
	checkArgs( args )

	return args

def checkArgs( args ):
	if not args.reportFile:
		args.reportFile = REPORT_FILE
	if not args.outputFile:
		args.outputFile = OUTPUT_FILE
	if not args.srcPath:
		args.srcPath = SRC_PATH