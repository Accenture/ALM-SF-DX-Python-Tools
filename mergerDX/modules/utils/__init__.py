''' Utils module '''
import os
import re
import json
import shutil
import subprocess

from lxml import etree

import __main__
from modules.utils.exceptions import NotCreatedDescribeLog
from modules.utils.models import MetadataType

XMLNS_DEF  = 'http://soap.sforce.com/2006/04/metadata'
XMLNS      = f'{{{XMLNS_DEF}}}'
IDENTATION = '    '

PARSEABLE_METADATA = [
	'labels', 'profiles', 'assignmentRules', 'autoResponseRules', 'escalationRules',
	'matchingRules', 'managedTopics', 'sharingRules', 'workflows'
]

INFO_TAG        = '[INFO]'
ERROR_TAG       = '[ERROR]'
WARNING_TAG     = '[WARNING]'

FATAL_LINE      = '[FATAL]'
SUCCESS_LINE    = '[SUCCESS]'
WARNING_LINE    = '[WARNING]'

DELTA_FOLDER    = 'srcToDeploy'
TEMPLATE_FILE   = "expansionPanels.html"

PWD = os.path.dirname(os.path.realpath(__main__.__file__))

FOLDER_PATTERN = ['│   ', '    ']
FILE_PATTERN = ['├─ ', '└─ ']


def write_file(folder, filename, content, print_log=False):
    ''' Writes into a file, creating the folders if not exists '''
    if print_log:
        print(f'\t- Writting \'{filename}\' in \'{folder}\'')
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(f'{folder}/{filename}', 'w', encoding='utf-8') as output_file:
        output_file.write(content)


def call_subprocess(command, verbose=True):
    ''' Calls subprocess, returns output and return code,
        if verbose flag is active it will print the output '''
    try:
        stdout = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True).decode('utf-8')
        if verbose:
            print_output(f'{stdout}')
        return stdout, 0
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode('utf-8')
        returncode = exc.returncode
        if verbose:
            print(f'{ERROR_TAG} Subprocess returned non-zero exit status {returncode}')
            print_output(output)
        return output, returncode


def print_output(output, color='', tab_level=1):
    ''' Prints output in the color passed '''
    formated = '\t' * tab_level + output.replace('\n', '\n' + '\t' * tab_level)
    print(f'{color}{formated}')


def truncate_string(value, size, fill=False):
    ''' Truncates a tring to passed size '''
    string_value = str(value)
    if len(string_value) > size:
        return string_value[:size].strip() + (string_value[size:] and '...')
    if fill:
        return string_value.ljust(size, ' ')
    return string_value


def getXmlNames(filepath):
    ''' Extracts the xml names from a describe '''

    if not os.path.isfile( filepath ):
        raise NotCreatedDescribeLog( filepath )

    with open( filepath, 'r' ) as filepath:
        lines = filepath.read()

    regex_string = (r'\*+\nXMLName: ([a-zA-Z0-9]+)\nDirName: ([a-zA-Z0-9]+)\nSuffix:'
                    r' ([a-zA-Z0-9]+)\nHasMetaFile: ([a-zA-Z]+)\nInFolder:'
                    r' ([a-zA-Z]+)\nChildObjects: (?:([a-zA-Z,]+),|)\*+')

    xmlNames    = re.findall(regex_string, lines, re.MULTILINE)
    dictionary  = dict()

    for (xmlName, dirName, suffix, hasMetadata, inFolder, childObjects) in xmlNames:
        inFolder    = castToBoolean( inFolder )
        hasMetadata = castToBoolean( hasMetadata )
        dictKey     = dirName

        if 'territory2Models' == dirName and 'territory2Model' != suffix:
            dictKey = suffix
        dictionary[ dictKey ] = MetadataType( xmlName, dirName, suffix, hasMetadata, inFolder, childObjects )

    return dictionary


def getXmlNamesFromJSON(filepath):
    ''' Extracts the xml names from a describe '''

    if not os.path.isfile( filepath ):
        raise NotCreatedDescribeLog( filepath )

    with open( filepath, 'r' ) as file:
        data = json.load( file )

    dictionary = {}

    for metadataInfo in data[ 'metadataObjects' ]:
        inFolder        = metadataInfo[ 'inFolder' ]
        hasMetadata     = metadataInfo[ 'metaFile' ]
        childObjects    = metadataInfo[ 'childXmlNames' ] if 'childXmlNames' in metadataInfo else []
        suffix          = metadataInfo[ 'suffix' ] if 'suffix' in metadataInfo else ''
        xmlName         = metadataInfo[ 'xmlName' ]
        dirName         = metadataInfo[ 'directoryName' ]
        dictKey         = dirName

        if 'territory2Models' == dirName and 'territory2Model' != suffix:
            dictKey = suffix
        dictionary[ dictKey ] = MetadataType( xmlName, dirName, suffix, hasMetadata, inFolder, childObjects )

    return dictionary


def castToBoolean( value ):
    return ( True if 'true' == value else False )
