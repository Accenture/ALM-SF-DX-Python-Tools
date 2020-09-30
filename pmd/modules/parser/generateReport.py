import json
import jinja2
from modules.utils import PWD, DEFAUL_VALUE

TEMPLATE_FILE = 'reportTemplate.html'

def createReport( mapAlerts, mapIssuesByLevel, outputFile ):

	loader				= jinja2.FileSystemLoader( searchpath=( f'{PWD}/resources/' ) )
	template_env		= jinja2.Environment( loader=loader )
	template			= template_env.get_template( TEMPLATE_FILE )
	print( mapIssuesByLevel )
	maxIssues, stepSize	= getChartValues( mapIssuesByLevel )
	report_file			= template.render( 
		mapAlerts=mapAlerts, mapIssuesByLevel=mapIssuesByLevel, maxIssues=maxIssues, 
		stepSize=stepSize, defaultSectionKey=DEFAUL_VALUE 
	)

	with open( outputFile, 'w', encoding="UTF8" ) as file:
		file.write( report_file )

def getChartValues( mapIssuesByLevel ):

	listNumIssues = []
	for level in mapIssuesByLevel:
		listNumIssues.append( mapIssuesByLevel[ level ] )

	maxIssues	= max( listNumIssues )
	minIssues	= min( listNumIssues )
	stepSize	= round( ( maxIssues - minIssues )/maxIssues )

	return maxIssues, stepSize