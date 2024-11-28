import os
from modules.utils import XMLNS, IDENTATION
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
    'loginHours'                    : 'mondayStart',
    'loginIpRanges'                 : 'startAddress',
    'objectPermissions'             : 'object',
    'pageAccesses'                  : 'apexPage',
    'profileActionOverride'         : 'actionName',
    'recordTypeVisibilities'        : 'recordType',
    'sharingRecalculations'         : 'className',
    'tabVisibilities'               : 'tab',
    'userPermissions'               : 'name'
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
    fullName   = ''
    mainId     = MAP_COMPOSED_FULLNAME[ tagName ][ 'main' ]
    secondId   = MAP_COMPOSED_FULLNAME[ tagName ][ 'secondary' ]
    mainName   = ''
    secondName = ''

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
    textValue = textValue.replace( "&", "&amp;" )
    textValue = textValue.replace( "<", "&lt;" )
    textValue = textValue.replace( ">", "&gt;" )
    textValue = textValue.replace( "\"", "&quot;" )
    textValue = textValue.replace( "'", "&apos;" )
    return textValue


def generateDestructive(mapMetadata, apiVersion):
    elementsData = ''
    for metadataType in sorted( mapMetadata ):
        if 'D' in mapMetadata[ metadataType ]:
            elementsData += f'{IDENTATION}<types>\n'
            for apiName in sorted( mapMetadata[ metadataType ][ 'D' ] ):
                elementsData += f'{IDENTATION}{IDENTATION}<members>{apiName}</members>\n'
            elementsData += f'{IDENTATION}{IDENTATION}<name>{metadataType}</name>\n'
            elementsData += f'{IDENTATION}</types>\n'

    if elementsData:
        packageData = '<?xml version="1.0" encoding="UTF-8"?>\n<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n'
        packageData += elementsData
        packageData += f'{IDENTATION}<version>{apiVersion}</version>\n</Package>'

        with open( 'destructiveChangesPost.xml', 'w' ) as packageFile:
            packageFile.write( packageData )
