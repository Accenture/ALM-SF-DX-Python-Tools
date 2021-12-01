import xml.etree.ElementTree as elTree

from modules.git.utils import get_file
from modules.utils import XMLNS
from modules.utils.utilities import getFullName
from modules.utils.exceptions import DuplicatedTags

def parseFile(filename, reference):

	fileString	= get_file( filename, reference )
	xmlData		= elTree.fromstring( fileString )
	rootTag		= xmlData.tag.split( XMLNS )[ 1 ]

	setDuplicatedFullNames = set()
	mapComponents = {}

	for childElement in xmlData.getchildren():
		tagName = childElement.tag.split( XMLNS )[ 1 ]
		if childElement:
			addValueToMap( tagName, childElement, mapComponents, setDuplicatedFullNames )
		else:
			mapComponents[ tagName ] = childElement.text

	if len( setDuplicatedFullNames ) > 0:
		print( f'##[error] Duplicated Tags found in file {filename}' )
		print( setDuplicatedFullNames )
		raise DuplicatedTags( filename )
	return rootTag, mapComponents


def addValueToMap(tagName, childElement, mapComponents, setDuplicatedFullNames, fullName=None):
	if not fullName:
		fullName = getFullName( tagName, childElement )
	if not tagName in mapComponents:
		mapComponents[ tagName ] = {}
	if fullName in mapComponents[ tagName ]:
		setDuplicatedFullNames.add( f'{tagName}-{fullName}' )
	mapComponents[ tagName ][ fullName ] = getChildData( childElement )


def getChildData(xmlElement):
	mapData = {}
	for childElement in xmlElement.getchildren():
		tagName = childElement.tag.split( XMLNS )[ 1 ]
		if childElement:
			mapData[ tagName ] = getChildData( childElement )
		else:
			mapData[ tagName ] = childElement.text
	return mapData

def mergeFileToCommit(filePath, mapComponents, mapAttributes):
	xmlData = elTree.parse( filePath ).getroot()
	fileTag = xmlData.tag.split( XMLNS )[ 1 ]
	for childElement in xmlData.getchildren():
		tagName = childElement.tag.split( XMLNS )[ 1 ]
		if childElement:
			checkElement( tagName, childElement, mapComponents )
		else:
			checkAttribute( tagName, childElement.text, mapAttributes )
	return fileTag


def checkElement(tagName, childElement, mapComponents, fullName=None):
	if not fullName:
		fullName = getFullName( tagName, childElement )
	if not tagName in mapComponents:
		mapComponents[ tagName ] = {}
	if not fullName in mapComponents[ tagName ]:
		mapComponents[ tagName ][ fullName ] = childElement


def checkAttribute(tagName, value, mapAttributes):
	if not tagName in mapAttributes:
		mapAttributes[ tagName ] = value
