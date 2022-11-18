''' Delta Builder '''
import os
import re
import glob
import json
import shutil

from modules.git import checkout, fetch, prepare_and_merge
from modules.parser.parse_file import parseFile
from modules.utils import INFO_TAG, call_subprocess, getXmlNamesFromJSON, IDENTATION, PARSEABLE_METADATA
from modules.utils.exceptions import NoDifferencesException
from modules.utils.utilities import generateDestructive, xmlEncodeText

def mergeDelta( source, target, remote, doFetch, reset, deltaFolder, sourceFolder, apiVersion, describePath='describe.log'):
    ''' Builds delta package in the destination folder '''

    print( f'{INFO_TAG} Clean up target folder \'{deltaFolder}\'' )
    shutil.rmtree( deltaFolder, ignore_errors=True, onerror=None )
    os.makedirs( deltaFolder )

    print( f'{INFO_TAG} Extracting metadata types from \'{describePath}\'' )
    xmlNames = getXmlNamesFromJSON( describePath )

    print( f'{INFO_TAG} Preparing to merge \'{source}\' into \'{target}\'' )
    prepare_and_merge( source, target, remote, doFetch, reset )

    mapDiffs = handleMerge( sourceFolder, 'HEAD', 'HEAD~1', deltaFolder, apiVersion, xmlNames )

    generateDestructive( mapDiffs, apiVersion )

    print( f'\n{INFO_TAG} Generated Delta' )


def buildDelta(sourceRef, targetRef, remote, doFetch, deltaFolder, sourceFolder, apiVersion, describePath='describe.log'):
    ''' Builds delta package in the destination folder '''

    print( f'{INFO_TAG} Clean up target folder \'{deltaFolder}\'' )
    shutil.rmtree( deltaFolder, ignore_errors=True, onerror=None )
    os.makedirs( deltaFolder )

    print( f'{INFO_TAG} Extracting metadata types from \'{describePath}\'' )
    xmlNames = getXmlNamesFromJSON( describePath )

    if doFetch:
        print( f'{INFO_TAG} Fetching from \'{remote}\'' )
        fetch( remote )
    else:
        print( f'{INFO_TAG} Not fetching, using current local status' )

    print( f'{INFO_TAG} Checking out source ref \'{sourceRef}\'' )
    checkout( sourceRef, remote, reset=False)

    mapDiffs = handleMerge( sourceFolder, sourceRef, targetRef, deltaFolder, apiVersion, xmlNames )

    generateDestructive( mapDiffs, apiVersion )

    print( f'\n{INFO_TAG} Generated Delta' )


def handleMerge(sourceFolder, sourceRef, targetRef, deltaFolder, apiVersion, xmlNames):

    print( f'{INFO_TAG} Getting differences' )
    differences = getDifferences( sourceFolder, sourceRef, targetRef )

    print( f'{INFO_TAG} Handling a total of {len( differences )} differences' )
    projectNames    = getProjectNames()
    return handleDifferences( differences, projectNames, deltaFolder, apiVersion, xmlNames, sourceFolder, sourceRef, targetRef )


def getDifferences(sourceFolder, source, target):
    ''' Extract the differences between two references '''

    diffCommand = f'git diff --name-status {target} {source}'
    output, _   = call_subprocess( diffCommand)

    if sourceFolder:
        regexString = r'([A-Z0-9]+)\t*({}\/.+)'.format( sourceFolder )
    else:
        regexString = r'([A-Z0-9]+)\t*(.+\/.+)'

    differences = re.findall( regexString, output )

    if not differences:
        raise NoDifferencesException( sourceFolder )
    return differences


def getProjectNames():

    with open( 'sfdx-project.json', 'r' ) as file:
        data = json.load( file )

    projectNames = []
    for pathData in data[ 'packageDirectories' ]:
        projectNames.append( pathData[ 'path' ] )

    return projectNames


def addChildMetadataToMapDiffs(splittedApiName, mapDiffs, status):
    mapChildMetadata = {
        'indexes'           : 'Index',
        'businessProcesses' : 'BusinessProcess',
        'recordTypes'       : 'RecordType',
        'compactLayouts'    : 'CompactLayout',
        'webLinks'          : 'WebLink',
        'validationRules'   : 'ValidationRule',
        'sharingReasons'    : 'SharingReason',
        'listViews'         : 'ListView',
        'fieldSets'         : 'FieldSet',
        'fields'            : 'CustomField'
    }
    apiname = splittedApiName[ 0 ] + '.' + splittedApiName[ 2 ]
    xmlName = mapChildMetadata[ splittedApiName[ 1 ] ]
    addValueToMapDiffs( xmlName, status, apiname, mapDiffs )


def addFileToDiffs(mapDiffs, xmlName, status, apiname):
    apiname         = renameApiName( apiname )
    splittedApiName = apiname.split('/')
    if xmlName == 'AuraDefinitionBundle' or xmlName == 'LightningComponentBundle':
        addValueToMapDiffs( xmlName, status, splittedApiName[ 0 ], mapDiffs )
    elif xmlName == 'CustomObject':
        numFolders = len( splittedApiName )
        if numFolders == 2:
            addValueToMapDiffs( xmlName, status, splittedApiName[ 1 ], mapDiffs )
        elif numFolders == 3:
            addChildMetadataToMapDiffs( splittedApiName, mapDiffs, status )
    else:
        addValueToMapDiffs( xmlName, status, apiname, mapDiffs )
    return mapDiffs


def renameApiName(apiname):
    apiname         = apiname.replace( '-meta.xml', '' )
    splittedApiName = apiname.split( '.' )
    return ( '.'.join( splittedApiName[ 0 : -1 ] ) )


def addValueToMapDiffs(xmlName, status, apiname, mapDiffs):
    if not xmlName in mapDiffs:
        mapDiffs[ xmlName ] = {}
    if not status in mapDiffs[xmlName]:
        mapDiffs[ xmlName ][ status ] = set()
    listElements = mapDiffs[ xmlName ][ status ]
    mapDiffs[ xmlName ][ status ].add( apiname )


def handleDifferences(differences, projectNames, deltaFolder, apiVersion, xmlNames, sourceFolder, sourceRef, targetRef):
    ''' Handles a list of differences copying the files into the delta folder '''

    mapDiffs = {}

    for status, filename in differences:

        isMetadataFile = False
        for projectName in projectNames:
            if projectName in filename:
                isMetadataFile = True
                break
        if not isMetadataFile:
            continue

        if status.startswith('R'):
            handleRename( sourceFolder, filename, deltaFolder, xmlNames, mapDiffs )
        else:
            folder, apiname, srcFolder  = splitFolderApiname( sourceFolder, filename )
            xmlDefinition               = xmlNames.get( folder, None )

            if not xmlDefinition:
                print( f'Warning : {folder} not in describe' )
                continue

            hasMetaFile         = getattr( xmlDefinition, "hasMetadata" )
            listChildObjects    = getattr( xmlDefinition, "childObjects" )
            xmlName             = getattr( xmlDefinition, "xmlName" )

            if status == 'A':
                handleCreation( srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs, xmlName, status )
            elif status == 'M':
                handleModification( srcFolder, folder, apiname, filename, deltaFolder, sourceRef, targetRef, hasMetaFile, listChildObjects, mapDiffs, xmlName, status )
            elif status == 'D':
                handleDeletion( mapDiffs, xmlName, status, apiname )

    return mapDiffs


def handleRename(sourceFolder, filename, deltaFolder, xmlNames, mapDiffs):

    deletedFile, addedFile      = filename.split( '\t' )

    folder, apiname, srcFolder  = splitFolderApiname( sourceFolder, addedFile )
    xmlDefinition               = xmlNames.get( folder, None )
    xmlName                     = getattr( xmlDefinition, "xmlName" )
    if not xmlDefinition:
        print( f'Warning : {folder} not in describe' )
    else:
        hasMetaFile = getattr( xmlDefinition, "hasMetadata" )
        handleCreation(srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs, xmlName, 'A')

    folder, apiname, srcFolder  = splitFolderApiname( sourceFolder, deletedFile )
    xmlDefinition               = xmlNames.get( folder, None )
    xmlName                     = getattr( xmlDefinition, "xmlName" )
    if not xmlDefinition:
        print( f'Warning : {folder} not in describe' )
    else:
        handleDeletion( mapDiffs, xmlName, 'D', apiname )


def handleCreation(srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs, xmlName, status):
    addFileToDiffs( mapDiffs, xmlName, status, apiname )
    copyFiles( srcFolder, folder, apiname, deltaFolder, hasMetaFile )


def handleModification(srcFolder, folder, apiname, filename, deltaFolder, sourceRef, targetRef, hasMetaFile, listChildObjects, mapDiffs, xmlName, status):

    if folder in PARSEABLE_METADATA:
        print( f'parse file - {filename}')
        rootTag, mapComponentsNew = parseFile( f'{filename}', sourceRef )
        rootTag, mapComponentsOld = parseFile( f'{filename}', targetRef )
        mapResult = compareFiles( mapComponentsNew, mapComponentsOld, mapDiffs, apiname, xmlName )
        if mapResult.keys():
            generateMergedFile( rootTag, folder, apiname, deltaFolder, mapResult )
            if folder == 'profiles':
                addFileToDiffs( mapDiffs, xmlName, status, apiname )
    else:
        addFileToDiffs( mapDiffs, xmlName, status, apiname )
        copyFiles( srcFolder, folder, apiname, deltaFolder, hasMetaFile )


def compareFiles(mapComponentsNew, mapComponentsOld, mapDiffs, apiname, xmlName):
    mapResult = {}
    objectName = apiname.split( '.' )[ 0 ]
    for tagName in mapComponentsNew:
        if tagName in mapComponentsOld:
            if mapComponentsNew[ tagName ] != mapComponentsOld[ tagName ]:
                if isinstance( mapComponentsNew[ tagName ], str ):
                    mapResult[ tagName ] = mapComponentsNew[ tagName ]
                else:
                    for elementName in mapComponentsNew[ tagName ]:
                        if elementName in mapComponentsOld[ tagName ]:
                            if mapComponentsNew[ tagName ][ elementName ] != mapComponentsOld[ tagName ][ elementName ]:
                                if xmlName != 'Profile':
                                    addFileToDiffs( mapDiffs, xmlName, 'M', f'{objectName}.{elementName}.{tagName}' )
                                if not tagName in mapResult:
                                    mapResult[ tagName ] = {}
                                if not elementName in mapResult[ tagName ]:
                                    mapResult[ tagName ][ elementName ] = {}
                                mapResult[ tagName ][ elementName ] = mapComponentsNew[ tagName ][ elementName ]
                        else:
                            if xmlName != 'Profile':
                                addFileToDiffs( mapDiffs, xmlName, 'A', f'{objectName}.{elementName}.{tagName}' )
                            if not tagName in mapResult:
                                mapResult[ tagName ] = {}
                            if not elementName in mapResult[ tagName ]:
                                mapResult[ tagName ][ elementName ] = {}
                            mapResult[ tagName ][ elementName ] = mapComponentsNew[ tagName ][ elementName ]
        else:
            mapResult[ tagName ] = mapComponentsNew[ tagName ]
            if xmlName != 'Profile':
                for elementName in mapComponentsNew[ tagName ]:
                    addFileToDiffs( mapDiffs, xmlName, 'A', f'{objectName}.{elementName}.{tagName}' )

        if xmlName != 'Profile':
            oldTagKeys = mapComponentsOld[ tagName ].keys() if tagName in mapComponentsOld else set()
            newTagKeys = mapComponentsNew[ tagName ].keys() if tagName in mapComponentsNew else set()
            for elementName in list( oldTagKeys - newTagKeys ):
                handleDeletion( mapDiffs, xmlName, 'D', f'{objectName}.{elementName}.{tagName}' )

    return mapResult


def generateMergedFile(rootTag, folder, apiname, deltaFolder, mapResult):

    mergedFile = '<?xml version="1.0" encoding="UTF-8"?>\n'
    mergedFile += f'<{rootTag} xmlns="http://soap.sforce.com/2006/04/metadata">\n'
    for tagName in mapResult:
        if isinstance( mapResult[ tagName ], str ):
            mergedFile += f'{IDENTATION}<{tagName}>{xmlEncodeText(mapResult[ tagName ])}</{tagName}>\n'
        else:
            for fullNameElement in mapResult[ tagName ]:
                mergedFile += f'{IDENTATION}<{tagName}>\n'
                for elementTag in mapResult[ tagName ][ fullNameElement ]:
                    elementValue = mapResult[ tagName ][ fullNameElement ][ elementTag ]
                    mergedFile += iterateElement( elementValue, elementTag, 2 )
                mergedFile += f'{IDENTATION}</{tagName}>\n'
    mergedFile += f'</{rootTag}>'

    makeDirs( f'{deltaFolder}/{folder}' )
    with open( f'{deltaFolder}/{folder}/{apiname}', 'w', encoding='utf-8' ) as resultFile:
        resultFile.write( mergedFile )


def iterateElement( elementValue, elementTag, identationLevel ):

    textValue = ''
    if type( elementValue ) is str:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}>{xmlEncodeText(elementValue)}</{elementTag}>\n'
    elif type( elementValue ) is dict:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}>\n'
        for keyTag in sorted( elementValue.keys() ):
            textValue += iterateElement( elementValue[ keyTag ], keyTag, identationLevel + 1 )
        textValue += f'{IDENTATION*identationLevel}</{elementTag}>\n'
    elif type( elementValue ) is list:
        for elementListValue in elementValue:
            textValue += f'{IDENTATION*identationLevel}<{elementTag}>\n'
            for keyTag in sorted( elementListValue.keys() ):
                textValue += iterateElement( elementListValue[ keyTag ], keyTag, identationLevel + 1 )
            textValue += f'{IDENTATION*identationLevel}</{elementTag}>\n'
    else:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}/>\n'
    return textValue


def handleDeletion(mapDiffs, xmlName, status, apiname):
    addFileToDiffs( mapDiffs, xmlName, status, apiname )


def copyFiles(srcFolder, folder, apiname, deltaFolder, hasMetaFile):

    if folder in [ 'aura', 'lwc' ]:
        rootFolder = apiname.split( '/' )[ 0 ]
        copyTree( f'{srcFolder}/{folder}/{rootFolder}', f'{deltaFolder}/{folder}/{rootFolder}' )

    elif folder == 'staticresources':
        if '/' in apiname:
            rootFolder = apiname.split( '/' )[ 0 ]
            pathFolder = f'{folder}/{rootFolder}'
            copyTree( f'{srcFolder}/{pathFolder}', f'{deltaFolder}/{pathFolder}' )
            copyFile( f'{srcFolder}/{pathFolder}.resource-meta.xml', f'{deltaFolder}/{pathFolder}.resource-meta.xml' )
        else:
            makeDirs( f'{deltaFolder}/{folder}' )
            copyFile( f'{srcFolder}/{folder}/{apiname}', f'{deltaFolder}/{folder}/{apiname}' )
            apiname = apiname.split( '.' )[ 0 ]
            copyFile( f'{srcFolder}/{folder}/{apiname}.resource-meta.xml', f'{deltaFolder}/{folder}/{apiname}.resource-meta.xml' )
    elif folder == 'experiences':
        if '/' in apiname:
            rootFolder = apiname.split( '/' )[ 0 ]
            pathFolder = f'{folder}/{rootFolder}'
            copyTree( f'{srcFolder}/{pathFolder}', f'{deltaFolder}/{pathFolder}' )
            copyFile( f'{srcFolder}/{pathFolder}.site-meta.xml', f'{deltaFolder}/{pathFolder}.site-meta.xml' )
        else:
            makeDirs( f'{deltaFolder}/{folder}' )
            copyFile( f'{srcFolder}/{folder}/{apiname}', f'{deltaFolder}/{folder}/{apiname}' )
            apiname = apiname.split( '.' )[ 0 ]
            copyFile( f'{srcFolder}/{folder}/{apiname}.site-meta.xml', f'{deltaFolder}/{folder}/{apiname}.site-meta.xml' )
    elif folder == 'objectTranslations':
        objectTranslationName = apiname.split('/')[0]
        objectTranslationFile = f'{objectTranslationName}/{objectTranslationName}.objectTranslation-meta.xml'
        copyTree(f'{srcFolder}/{folder}/{objectTranslationName}',f'{deltaFolder}/{folder}/{objectTranslationName}')
        copyFile( f'{srcFolder}/{folder}/{apiname}', f'{deltaFolder}/{folder}/{apiname}' )
        if not os.path.isfile( f'{deltaFolder}/{folder}/{objectTranslationFile}'):
            copyFile( f'{srcFolder}/{folder}/{objectTranslationFile}', f'{deltaFolder}/{folder}/{objectTranslationFile}' )
    else:
        if '/' in apiname:
            subFolders      = apiname.split( '/' )
            listSubFolders  = subFolders[ :-1 ]
            pathFolders     = '/'.join( listSubFolders )
            makeDirs( f'{deltaFolder}/{folder}/{pathFolders}' )
        else:
            makeDirs( f'{deltaFolder}/{folder}' )

        if hasMetaFile and not 'documentFolder-meta.xml' in apiname and not 'emailFolder-meta.xml' in apiname:
            if folder == 'documents':
                if 'document-meta.xml' in apiname:
                    rootFilename    = apiname[ : -len( 'document-meta.xml' ) ]
                    listFiles       = glob.glob( f'{srcFolder}/{folder}/{rootFilename}*' )
                    pathFile        = [ file for file in listFiles if 'document-meta.xml' not in file ][ 0 ].split( '/' )
                    relatedFile     = pathFile[ len( pathFile ) - 1 ]
                else:
                    relatedFile = apiname.split( '.' )[ 0 ]
                    relatedFile = f'{relatedFile}.document-meta.xml'
                copyFile( f'{srcFolder}/{folder}/{relatedFile}', f'{deltaFolder}/{folder}/{relatedFile}' )
            else:
                if '-meta.xml' in apiname:
                    relatedFile = apiname[ : -len( '-meta.xml' ) ]
                else:
                    relatedFile = f'{apiname}-meta.xml'
                copyFile( f'{srcFolder}/{folder}/{apiname}', f'{deltaFolder}/{folder}/{apiname}' )
                if os.path.isfile( f'{srcFolder}/{folder}/{relatedFile}' ):
                    copyFile( f'{srcFolder}/{folder}/{relatedFile}', f'{deltaFolder}/{folder}/{relatedFile}' )

        copyFile( f'{srcFolder}/{folder}/{apiname}', f'{deltaFolder}/{folder}/{apiname}' )


def copyFile(origin, destination):
    shutil.copy( origin, destination )


def copyTree(origin, destination):
    if not os.path.exists( destination ):
        shutil.copytree( origin, destination )


def makeDirs( dirPath ):
    os.makedirs( dirPath, exist_ok=True )


def splitFolderApiname(sourceFolder, filename):

    if sourceFolder:
        filenameSplit = filename[ len( sourceFolder ) + 1: ].split( '/' )
    else:
        filenameSplit = filename.split( '/' )

    folder    = filenameSplit[ 3 ]
    apiname   = '/'.join( filenameSplit[ 4: ] )
    srcFolder = '/'.join( filenameSplit[ :3 ] )

    return folder, apiname, srcFolder
