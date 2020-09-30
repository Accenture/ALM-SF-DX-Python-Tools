from modules.utils import argparser
from modules.parser.parseReport import getAlertsFromReport
from modules.parser.generateReport import createReport

def main():
	
	args = argparser.parseArgs()

	mapAlerts, mapIssuesByLevel = getAlertsFromReport( args.reportFile, args.srcPath )

	if len( mapAlerts ) > 0:
		createReport( mapAlerts, mapIssuesByLevel, args.outputFile )

if __name__ == "__main__":
	main()