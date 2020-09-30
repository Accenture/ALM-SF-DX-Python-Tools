import json
from modules.utils import argparser

XMLNS           = '{http://soap.sforce.com/2006/04/metadata}'
IDENTATION      = '    '
PACKAGE_PATH    = 'package.xml'

def main():
    
    args = argparser.parseArgs()

    request     = str( args.jsonBody ).replace( '\\n', '' )
    packageBody = json.loads( request )
    generatePackage( packageBody, args.apiVersion )


def generatePackage( packageBody, apiVersion ):

    packageString = '<?xml version="1.0" encoding="UTF-8"?>\n<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n'

    listMetadataTypes = sorted( packageBody.keys() )

    for metadataType in listMetadataTypes:
        typeComponent = IDENTATION + '<types>\n'
        listMetadataComponents = sorted( packageBody[ metadataType ] )
        for metatadaComponent in listMetadataComponents:
            typeComponent += IDENTATION*2 + '<members>' + metatadaComponent + '</members>\n'
        typeComponent += IDENTATION*2 + '<name>' + metadataType + '</name>\n'
        typeComponent += IDENTATION + '</types>\n'
        packageString += typeComponent
    packageString += IDENTATION + '<version>' + apiVersion + '</version>\n'
    packageString += '</Package>'

    with open( PACKAGE_PATH, 'w' ) as fileOut:
        fileOut.write( packageString )


if __name__ == "__main__":
    main()
