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

def mergeDelta( source, target, remote, doFetch, reset, deltaFolder, sourceFolder, apiVersion, describePath='describe.log'):
    ''' Builds delta package in the destination folder '''

    print( f'{INFO_TAG} Clean up target folder \'{deltaFolder}\'' )
    shutil.rmtree( deltaFolder, ignore_errors=True, onerror=None )
    os.makedirs( deltaFolder )

    print( f'{INFO_TAG} Extracting metadata types from \'{describePath}\'' )
    xmlNames = getXmlNamesFromJSON( describePath )

    print( f'{INFO_TAG} Preparing to merge \'{source}\' into \'{target}\'' )
    prepare_and_merge( source, target, remote, doFetch, reset )

    handleMerge( sourceFolder, 'HEAD', 'HEAD~1', deltaFolder, apiVersion, xmlNames )


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

    handleMerge( sourceFolder, sourceRef, targetRef, deltaFolder, apiVersion, xmlNames )


def handleMerge(sourceFolder, sourceRef, targetRef, deltaFolder, apiVersion, xmlNames):

    print( f'{INFO_TAG} Getting differences' )
    differences = getDifferences( sourceFolder, sourceRef, targetRef )

    print( f'{INFO_TAG} Handling a total of {len( differences )} differences' )
    projectNames    = getProjectNames()
    mapDiffs        = handleDifferences( differences, projectNames, deltaFolder, apiVersion, xmlNames, sourceFolder, sourceRef, targetRef )

    print(f'\n{INFO_TAG} Generated Delta')


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


def handleDifferences(differences, projectNames, deltaFolder, apiVersion, xmlNames, sourceFolder, sourceRef, targetRef):
    ''' Handles a list of differences copying the files into the delta folder '''

    mapDiffs = {}

    for status, filename in differences:

        isMetadataFile = True
        for projectName in projectNames:
            if projectName not in filename:
                isMetadataFile = False
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

            if status == 'A':
                handleCreation( srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs )
            elif status == 'M':
                handleModification( srcFolder, folder, apiname, filename, deltaFolder, sourceRef, targetRef, hasMetaFile, listChildObjects, mapDiffs )
            elif status == 'D':
                handleDeletion( srcFolder, folder, apiname )

    return mapDiffs


def handleRename(sourceFolder, filename, deltaFolder, xmlNames, mapDiffs):

    deletedFile, addedFile      = filename.split( '\t' )

    folder, apiname, srcFolder  = splitFolderApiname( sourceFolder, addedFile )
    xmlDefinition               = xmlNames.get( folder, None )
    if not xmlDefinition:
        print( f'Warning : {folder} not in describe' )
    else:
        hasMetaFile = getattr( xmlDefinition, "hasMetadata" )
        handleCreation(srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs)

    folder, apiname, srcFolder  = splitFolderApiname( sourceFolder, deletedFile )
    xmlDefinition               = xmlNames.get( folder, None )
    if not xmlDefinition:
        print( f'Warning : {folder} not in describe' )
    else:
        handleDeletion(srcFolder, folder, apiname)


def handleCreation(srcFolder, folder, apiname, deltaFolder, hasMetaFile, mapDiffs):

    copyFiles( srcFolder, folder, apiname, deltaFolder, hasMetaFile )


def handleModification(srcFolder, folder, apiname, filename, deltaFolder, sourceRef, targetRef, hasMetaFile, listChildObjects, mapDiffs):

    if folder in PARSEABLE_METADATA:
        print( f'parse file - {filename}')
        rootTag, mapComponentsNew = parseFile( f'{filename}', sourceRef )
        rootTag, mapComponentsOld = parseFile( f'{filename}', targetRef )
        mapResult = compareFiles( mapComponentsNew, mapComponentsOld )
        if mapResult.keys():
	        generateMergedFile( rootTag, folder, apiname, deltaFolder, mapResult )
    else:
        copyFiles( srcFolder, folder, apiname, deltaFolder, hasMetaFile )


def compareFiles(mapComponentsNew, mapComponentsOld):
    mapResult = {}

    for sectionKey in mapComponentsNew:
        if sectionKey in mapComponentsOld:
            if mapComponentsNew[ sectionKey ] != mapComponentsOld[ sectionKey ]:
                if isinstance( mapComponentsNew[ sectionKey ], str ):
                    mapResult[ sectionKey ] = mapComponentsNew[ sectionKey ]
                else:
                    for elementName in mapComponentsNew[ sectionKey ]:
                        if elementName in mapComponentsOld[ sectionKey ]:
                            if mapComponentsNew[ sectionKey ][ elementName ] != mapComponentsOld[ sectionKey ][ elementName ]:
                                if not sectionKey in mapResult:
                                    mapResult[ sectionKey ] = {}
                                if not elementName in mapResult[ sectionKey ]:
                                    mapResult[ sectionKey ][ elementName ] = {}
                                mapResult[ sectionKey ][ elementName ] = mapComponentsNew[ sectionKey ][ elementName ]
                        else:
                            if not sectionKey in mapResult:
                                mapResult[ sectionKey ] = {}
                            if not elementName in mapResult[ sectionKey ]:
                                mapResult[ sectionKey ][ elementName ] = {}
                            mapResult[ sectionKey ][ elementName ] = mapComponentsNew[ sectionKey ][ elementName ]
        else:
            mapResult[ sectionKey ] = mapComponentsNew[ sectionKey ]

    return mapResult


def generateMergedFile(rootTag, folder, apiname, deltaFolder, mapResult):

    mergedFile = '<?xml version="1.0" encoding="UTF-8"?>\n'
    mergedFile += f'<{rootTag} xmlns="http://soap.sforce.com/2006/04/metadata">\n'
    for sectionKey in mapResult:
        if isinstance( mapResult[ sectionKey ], str ):
            mergedFile += f'{IDENTATION}<{sectionKey}>{mapResult[ sectionKey ]}</{sectionKey}>\n'
        else:
            for fullNameElement in mapResult[ sectionKey ]:
                mergedFile += f'{IDENTATION}<{sectionKey}>\n'
                for elementTag in mapResult[ sectionKey ][ fullNameElement ]:
                    elementValue = mapResult[ sectionKey ][ fullNameElement ][ elementTag ]
                    mergedFile += iterateElement( elementValue, elementTag, 2 )
                mergedFile += f'{IDENTATION}</{sectionKey}>\n'
    mergedFile += f'</{rootTag}>'

    makeDirs( f'{deltaFolder}/{folder}' )
    with open( f'{deltaFolder}/{folder}/{apiname}', 'w', encoding='utf-8' ) as resultFile:
        resultFile.write( mergedFile )


def iterateElement( elementValue, elementTag, identationLevel,  ):

    textValue = ''
    if type( elementValue ) is str:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}>{elementValue}</{elementTag}>\n'
    elif type( elementValue ) is dict:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}>\n'
        for keyTag in sorted( elementValue.keys() ):
            textValue += iterateElement( elementValue[ keyTag ], keyTag, identationLevel + 1 )
        textValue += f'{IDENTATION*identationLevel}</{elementTag}>\n'
    else:
        textValue += f'{IDENTATION*identationLevel}<{elementTag}/>\n'
    return textValue


def handleDeletion(srcFolder, folder, apiname):
    pass


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
                    relatedFile     = [ file for file in listFiles if 'document-meta.xml' not in file ][ 0 ].split( '/documents/' )[ 1 ]
                else:
                    relatedFile = apiname.split( '.' )[ 0 ]
                    relatedFile = f'{relatedFile}.document-meta.xml'
                copyFile( f'{srcFolder}/{folder}/{relatedFile}', f'{deltaFolder}/{folder}/{relatedFile}' )
            else:
                if '-meta.xml' in apiname:
                    relatedFile = apiname[ : -len( '-meta.xml' ) ]
                else:
                    relatedFile = f'{apiname}-meta.xml'
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
