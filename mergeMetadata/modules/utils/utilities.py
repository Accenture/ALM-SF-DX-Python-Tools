import os
from modules.utils import XMLNS
from modules.utils.exceptions import NoFullNameError

MAP_COMPOSED_FULLNAME = {
    'actionOverrides'	: { 'main' : 'actionName', 'secondary' : 'formFactor' },
    'layoutAssignments'	: { 'main' : 'layout', 'secondary' : 'recordType' }
}

MAP_FULLNAME = {
    'applicationVisibilities'       : 'application',
    'categoryGroupVisibilities'     : 'dataCategoryGroup',
    'classAccesses'                 : 'apexClass',
    'customMetadataTypeAccesses'    : 'name',
    'customPermissions'             : 'name',
    'customSettingAccesses'         : 'name',
    'externalDataSourceAccesses'    : 'externalDataSource',
    'fieldPermissions'              : 'field',
    'flowAccesses'                  : 'flow',
    'loginHours'                    : 'weekdayStart',
    'loginIpRanges'                 : 'startAddress',
    'objectPermissions'             : 'object',
    'pageAccesses'                  : 'apexPage',
    'profileActionOverride'         : 'actionName',
    'recordTypeVisibilities'        : 'recordType',
    'sharingRecalculations'         : 'className',
    'tabVisibilities'               : 'tab',
    'userPermissions'               : 'name',
    'picklistValues'				: 'picklist'
}

def checkFolder( folderPath ):
	if not os.path.isdir( folderPath ):
		os.makedirs( folderPath )

def getFullName( tagName, childElement ):
	if tagName in MAP_COMPOSED_FULLNAME:
		fullName = getComposedName( tagName, childElement )
	elif tagName in MAP_FULLNAME:
		fullName = searchFullNameTag( MAP_FULLNAME[ tagName ], childElement )
	else:
		fullName = searchFullNameTag( 'fullName', childElement )
	return fullName

def searchFullNameTag( fullNameTag, childElement ):
	fullName = ''
	for subChildElement in childElement.getchildren():
		tagName = subChildElement.tag.split( XMLNS )[ 1 ]
		if fullNameTag == tagName:
			fullName = subChildElement.text
	if not fullName:
		raise NoFullNameError( childElement.tag )
	return fullName

def getComposedName( tagName, childElement ):
	fullName	= ''
	mainId		= MAP_COMPOSED_FULLNAME[ tagName ][ 'main' ]
	secondId	= MAP_COMPOSED_FULLNAME[ tagName ][ 'secondary' ]
	mainName	= ''
	secondName	= ''

	for subChildElement in childElement.getchildren():
		tagName = subChildElement.tag.split( XMLNS )[ 1 ]
		if mainId == tagName:
			mainName = subChildElement.text
		if secondId == tagName:
			secondName = subChildElement.text
	fullName = mainName + secondName

	if not fullName:
		raise NoFullNameError( childElement.tag )
	return fullName

def xmlEncodeText( textValue ):
	textValue = textValue.replace( "&", "&amp;" );
	textValue = textValue.replace( "<", "&lt;" );
	textValue = textValue.replace( ">", "&gt;" );
	textValue = textValue.replace( "\"", "&quot;" );
	textValue = textValue.replace( "'", "&apos;" );
	return textValue
