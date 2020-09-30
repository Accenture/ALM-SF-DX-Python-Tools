import json
from lxml import etree
from modules.utils import PWD, KEY_LEVEL, KEY_SECTION, KEY_SUBSECTION, KEY_CLASSIFICATION, DEFAUL_VALUE

def getAlertsFromReport( reportPath, srcPath ):

	mapAlerts			= {}
	mapIssuesByLevel	= {}

	tree				= etree.parse( reportPath ).getroot()
	trElements			= tree.findall( './/tr' )

	mapSections, mapSubSections = getAlersClassification()

	for trElement in trElements:
		if len( trElement.findall( 'td' ) ) > 0:
			alertData, level, section, subSection, classification = extractAlertData( trElement, srcPath, mapSections, mapSubSections )
			addValuesToMap( mapAlerts, alertData, level, section, subSection, classification )
			countIssues( mapIssuesByLevel, level )

	return mapAlerts, mapIssuesByLevel

def getAlersClassification():
	with open( f'{PWD}/resources/sections.json', 'r' ) as sectionsFile:
		mapSections = json.loads( sectionsFile.read() )
	with open( f'{PWD}/resources/subSections.json', 'r' ) as subSectionsFile:
		mapSubSections = json.loads( subSectionsFile.read() )
	return mapSections, mapSubSections

def addValuesToMap( mapAlerts, alertData, level, section, subSection, classification ):
	if level not in mapAlerts:
		mapAlerts[ level ] = {}

	if section not in mapAlerts[ level ]:
		mapAlerts[ level ][ section ] = {}

	if subSection != DEFAUL_VALUE:
		if subSection not in mapAlerts[ level ][ section ]:
			mapAlerts[ level ][ section ][ subSection ] = {}
		if classification not in mapAlerts[ level ][ section ][ subSection ]:
			mapAlerts[ level ][ section ][ subSection ][ classification ] = []
		mapAlerts[ level ][ section ][ subSection ][ classification ].append( alertData )
	else:
		if subSection not in mapAlerts[ level ][ section ]:
			mapAlerts[ level ][ section ][ subSection ] = []
		mapAlerts[ level ][ section ][ subSection ].append( alertData )

def countIssues( mapIssuesByLevel, level ):
	if level not in mapIssuesByLevel:
		mapIssuesByLevel[ level ] = 0
	mapIssuesByLevel[ level ] = mapIssuesByLevel[ level ] + 1

def extractAlertData( alertRow, srcPath, mapSections, mapSubSections ):

	alertData	= alertRow.getchildren()
	filePath	= alertData[ 1 ].text.split( srcPath )[ 1 ]
	fileFolder	= filePath.split( '/' )[ 0 ]
	fileName	= filePath.split( '/' )[ 1 ].split( '.' )[ 0 ]
	lineNumber	= alertData[ 2 ].text
	alertMsg	= alertData[ 3 ]

	if len( alertMsg ):
		alertMsg = alertMsg.getchildren()[ 0 ].text
	else:
		alertMsg = alertMsg.text

	
	if alertMsg in mapSections:
		section			= mapSections[ alertMsg ][ KEY_SECTION ]
		level			= getMapValue( mapSections[ alertMsg ], KEY_LEVEL )
		subSection		= getMapValue( mapSections[ alertMsg ], KEY_SUBSECTION )
		classification	= getMapValue( mapSections[ alertMsg ], KEY_CLASSIFICATION )
	else:
		section			= DEFAUL_VALUE
		level			= DEFAUL_VALUE
		subSection		= DEFAUL_VALUE
		classification	= DEFAUL_VALUE

		for key in mapSubSections:
			if key in alertMsg:
				for subKey in mapSubSections[ key ]:
					if subKey in alertMsg:
						mapValues		= mapSubSections[ key ][ subKey ]
						section			= mapValues[ KEY_SECTION ]
						level			= mapValues[ KEY_LEVEL ]
						subSection		= mapValues[ KEY_SUBSECTION ]
						classification	= getMapValue( mapValues, KEY_CLASSIFICATION )

	mapAlert = { 
		"fileName"		: fileName,
		"fileType"		: fileFolder,
		"lineNumber"	: lineNumber,
		"alertMsg"		: alertMsg
	}
	return mapAlert, level, section, subSection, classification

def getMapValue( sectionValues, key ):
	return ( sectionValues[ key ] if key in sectionValues else DEFAUL_VALUE )