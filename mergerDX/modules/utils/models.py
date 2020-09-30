''' General models module '''
import enum


class OutputType(enum.Enum):
    ''' Describe the output types avaliable for reporting '''
    CSV = 'csv'
    XML = 'xml'
    SCREEN = 'screen'

    @staticmethod
    def get_name_list():
        ''' Return all the names of the values '''
        return [item.value for item in OutputType]


class MetadataType:
    ''' Metadata Type Implementation for wrapping the describe log info '''

    def __init__(self, xmlName, dirName, suffix, hasMetadata, inFolder, childObjects):
        self.xmlName        = xmlName
        self.dirName        = dirName
        self.suffix         = suffix
        self.hasMetadata    = hasMetadata
        self.inFolder       = inFolder
        self.childObjects   = childObjects

    def __repr__(self):
        return f'<{self.xmlName}>'


class ChangeType(enum.Enum):
    ''' Type of changes, git like '''

    CREATION        = 'A'
    MODIFICATION    = 'M'
    DELETION        = 'D'
    RENAME          = 'R'
