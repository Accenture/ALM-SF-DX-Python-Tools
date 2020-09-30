import argparse

def parseArgs():

	parser = argparse.ArgumentParser()
	
	parser.add_argument( '-j', '--jsonBody', required=True, help='JSON Body to create package.xml' )
	parser.add_argument( '-a', '--apiVersion', required=True, help='API Version to retrieve changes' )
	args = parser.parse_args()

	return args
