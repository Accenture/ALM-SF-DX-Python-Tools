import os
import re
import json
import shutil
from modules.merger.mergeFiles import mergeFile
from modules.utils import argparser, SET_PARSEABLE_FOLDERS
from modules.utils.utilities import checkFolder
from modules.utils.exceptions import NotCreatedDescribeLog

def main():

    args = argparser.parseArgs()

    setParseableObjects = readDescribe( args.describePath, SET_PARSEABLE_FOLDERS )

    for folder in os.listdir( args.srcRetrievedPath ):
        pathFolder = f'{args.srcRetrievedPath}/{folder}'
        if os.path.isdir( pathFolder ):
            for fileName in os.listdir( pathFolder ):
                if folder in setParseableObjects:
                    mergeFile( args.srcPath, args.srcRetrievedPath, folder, fileName )
                else:
                    copyFiles( args.srcPath, args.srcRetrievedPath, folder, fileName )


def readDescribe(pathDescribe, setParseableObjects):
    ''' Extracts the xml names from a describe '''
    if not os.path.isfile( pathDescribe ):
        raise NotCreatedDescribeLog( pathDescribe )
    
    with open( pathDescribe, 'r' ) as file:
        data = json.load( file )

    for metadataInfo in data[ 'metadataObjects' ]:
        dirName         = metadataInfo[ 'directoryName' ]
        childObjects    = metadataInfo[ 'childXmlNames' ] if 'childXmlNames' in metadataInfo else []
        if dirName != 'objects' and len( childObjects ) > 0:
            setParseableObjects.add( dirName )

    return setParseableObjects


def copyFiles(srcPath, srcRetrievedPath, folder, fileName):
    pathSrcRetrieved    = f'{srcRetrievedPath}/{folder}/{fileName}'
    pathSrcFolder       = f'{srcPath}/{folder}'

    if os.path.isdir( pathSrcRetrieved ):
        pathSrcSubFolder = f'{pathSrcFolder}/{fileName}'
        checkFolder( pathSrcFolder )
        checkFolder( pathSrcSubFolder )
        if fileName != 'recordTypes':
            for file in os.listdir( pathSrcRetrieved ):
                copyFiles( srcPath, srcRetrievedPath, f'{folder}/{fileName}', file )
        else:
            for file in os.listdir( pathSrcRetrieved ):
                mergeFile( f'{srcPath}/{folder}', f'{srcRetrievedPath}/{folder}', fileName, file )
    else:
        checkFolder( pathSrcFolder )
        shutil.copy( f'{pathSrcRetrieved}', f'{pathSrcFolder}/{fileName}' )


if __name__ == "__main__":
    main()