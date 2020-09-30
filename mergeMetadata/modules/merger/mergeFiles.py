import os
import shutil
from modules.utils import XMLNS, XMLNS_DEF, IDENTATION
from modules.utils.utilities import checkFolder, xmlEncodeText
from modules.parser.parseFiles import parseFile, mergeFileToCommit

def mergeFile(srcPath, srcRetrievedPath, folder, fileName):
	pathScrFolder	= f'{srcPath}/{folder}'
	pathScrFile		= f'{srcPath}/{folder}/{fileName}'

	if os.path.isdir( pathScrFolder ) and os.path.isfile( pathScrFile ):
		handleModifiedFile( srcPath, srcRetrievedPath, folder, fileName )
	else:
		handleNewFile( srcPath, srcRetrievedPath, folder, fileName )


def handleNewFile(srcPath, srcRetrievedPath, folder, fileName):
	print( f'new file : {fileName}' )
	pathSrcFolder			= f'{srcPath}/{folder}'
	pathSrcFile				= f'{pathSrcFolder}/{fileName}'
	pathSrcRetrievedFile	= f'{srcRetrievedPath}/{folder}/{fileName}'
	checkFolder( pathSrcFolder )
	shutil.copy( pathSrcRetrievedFile, pathSrcFile )


def handleModifiedFile(srcPath, srcRetrievedPath, folder, fileName):
	print( f'modified file : {fileName}' )
	mapComponents, mapAttributes = parseFile( f'{srcRetrievedPath}/{folder}/{fileName}' )
	fileTag = mergeFileToCommit( f'{srcPath}/{folder}/{fileName}', mapComponents, mapAttributes )
	generateFile( srcPath, folder, fileName, mapComponents, mapAttributes, fileTag )


def generateFile(srcPath, folder, fileName, mapComponents, mapAttributes, fileTag):
	xmlFile = '<?xml version="1.0" encoding="UTF-8"?>\n'
	xmlFile += f'<{fileTag} xmlns="{XMLNS_DEF}">\n'
	xmlFile += addValuesToFile( mapComponents, mapAttributes )
	xmlFile += f'</{fileTag}>\n'
	with open( f'{srcPath}/{folder}/{fileName}', 'w', encoding='utf-8' ) as fileToWrite:
		fileToWrite.write( xmlFile )


def addValuesToFile(mapComponents, mapAttributes):
	listComponents	= sorted( list( mapComponents.keys() ) + list( mapAttributes.keys() ) )
	printValue		= ''
	
	for componentType in listComponents:
		if componentType in mapAttributes:
			printValue += getValueFromAttributes( componentType, mapAttributes )
		else:
			printValue += getValueFromComponent( componentType, mapComponents )
	return printValue


def getValueFromAttributes(componentType, mapAttributes):
	componentValue = mapAttributes[ componentType ]
	return f'{IDENTATION}<{componentType}>{componentValue}</{componentType}>\n'


def getValueFromComponent(componentType, mapComponents):
	listComponents	= sorted( list( mapComponents[ componentType ].keys() ) )
	printValue		= ''

	for fullName in listComponents:
		xmlElement		= mapComponents[ componentType ][ fullName ]
		componentValue	= ''
		if xmlElement.getchildren():
			for childElement in xmlElement.getchildren():
				tagName = childElement.tag.split( XMLNS )[ 1 ]
				if childElement:
					childValue = iterateChildsToPrint( childElement, 3 )
					componentValue += f'{IDENTATION*2}<{tagName}>\n{childValue}{IDENTATION*2}</{tagName}>\n'
				else:
					componentValue += f'{IDENTATION*2}<{tagName}>{xmlEncodeText(childElement.text)}</{tagName}>\n'
			printValue += f'{IDENTATION}<{componentType}>\n{componentValue}{IDENTATION}</{componentType}>\n'
		else:
			printValue += f'{IDENTATION}<{fullName}/>\n'
	return printValue


def iterateChildsToPrint(childElement, identationMultiplier):
	printValue = ''
	for subChildElement in childElement.getchildren():
		tagName = subChildElement.tag.split( XMLNS )[ 1 ]
		if subChildElement:
			childValue = iterateChildsToPrint( subChildElement, identationMultiplier+1 )
			printValue += f'{IDENTATION*identationMultiplier}<{tagName}>\n{childValue}{IDENTATION*identationMultiplier}</{tagName}>\n'
		else:
			encodedValue = xmlEncodeText(subChildElement.text) if subChildElement.text else ''
			printValue += f'{IDENTATION*identationMultiplier}<{tagName}>{encodedValue}</{tagName}>\n'
	return printValue