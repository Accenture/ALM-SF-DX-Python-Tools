import xml.etree.ElementTree as elTree
from modules.utils import XMLNS, STANDARD_ATTRIBUTES
from modules.utils.utilities import getFullName

def parseFile( filePath ):
	parser = elTree.XMLParser( encoding="utf-8" )
	xmlData = elTree.parse( filePath, parser ).getroot()

	mapComponents	= {}
	mapAttributes	= {}

	for childElement in xmlData.getchildren():
		tagName = childElement.tag.split( XMLNS )[ 1 ]
		if childElement and tagName in STANDARD_ATTRIBUTES:
			addValueToMap( tagName, childElement, mapComponents, fullName=tagName )
		elif childElement:
			addValueToMap( tagName, childElement, mapComponents )
		else:
			mapAttributes[ tagName ] = childElement.text
	return mapComponents, mapAttributes

def addValueToMap( tagName, childElement, mapComponents, fullName=None ): 
	if not fullName:
		fullName = getFullName( tagName, childElement )
	if not tagName in mapComponents:
		mapComponents[ tagName ] = {}
	mapComponents[ tagName ][ fullName ] = childElement

def mergeFileToCommit( filePath, mapComponents, mapAttributes ):
	xmlData = elTree.parse( filePath ).getroot()
	fileTag = xmlData.tag.split( XMLNS )[ 1 ]
	for childElement in xmlData.getchildren():
		tagName = childElement.tag.split( XMLNS )[ 1 ]
		if tagName in STANDARD_ATTRIBUTES:
			checkElement( tagName, childElement, mapComponents, fullName=tagName )
		elif childElement:
			checkElement( tagName, childElement, mapComponents )
		else:
			checkAttribute( tagName, childElement.text, mapAttributes )
	return fileTag

def checkElement( tagName, childElement, mapComponents, fullName=None ):
	if not fullName:
		fullName = getFullName( tagName, childElement )
	if not tagName in mapComponents:
		mapComponents[ tagName ] = {}
	if not fullName in mapComponents[ tagName ]:
		mapComponents[ tagName ][ fullName ] = childElement

def checkAttribute( tagName, value, mapAttributes ):
	if not tagName in mapAttributes:
		mapAttributes[ tagName ] = value