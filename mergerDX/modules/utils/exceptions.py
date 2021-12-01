''' Exceptions module '''
# Base Exceptions


class MergerException(Exception):
    ''' Base Exception For Merger App '''
    ERROR_CODE = 127


class MergerExceptionWarning(MergerException):
    ''' Base Exception For Merger App '''
    ERROR_CODE = 10


# Merger Exceptions

class BranchesUpToDateException(MergerException):
    ''' Exception to handle when the source branch is up to date
        with the target date '''
    ERROR_CODE = 2

    def __init__(self, source_branch, target_branch):
        '''  '''
        super().__init__(f'Branches are up to date source '
                         f'\'{source_branch}\', target \'{target_branch}\'')


class MergeConflictsException(MergerException):
    ''' Exception to handle Merge Conflicts (ERROR CODE 3) '''
    ERROR_CODE = 3

    def __init__(self, source_branch, target_branch, conflict_number):
        ''' Initializes the excetion, must pass the branches involved in the
            merge and the merge conflicts that occured '''
        super().__init__(f'Found {conflict_number} conflict(s) while trying '
                         f'to merge \'{source_branch}\' into '
                         f'\'{target_branch}\'')


class NoDifferencesException(MergerException):
    ''' Exception launched when no differences has been found in
        the src folder '''
    ERROR_CODE = 4

    def __init__(self, folder):
        if folder:
            super().__init__(f'No changes detected in the \'{folder}\' folder')
        else:
            super().__init__(f'No changes detected in the source folder')


class NotControlledFolder(MergerException):
    '''Exception launched when describe.log didn´t exist on the
       specific folder'''
    ERROR_CODE = -1

    def __init__(self, folder_name):
        super().__init__(f'Could not find folder \'{folder_name}\' in the '
                         f'list of controlled folders')


class NotControlledFoldersFound(MergerExceptionWarning):
    '''Exception launched when describe.log didn´t exist on the
       specific folder'''
    ERROR_CODE = 11

    def __init__(self, folders):
        super().__init__(f'Found folders that aren\'t controlled {folders}')


class TooManyParams(MergerException):
    '''Exception launched when describe.log didn´t exist on the
       specific folder'''
    ERROR_CODE = 12

    def __init__(self):
        super().__init__(f'Cannot specify filestring and filepath')


class NotAGitRepository(MergerException):
    '''Exception launched when the current directory is not a git
       repository'''
    ERROR_CODE = 13

    def __init__(self):
        super().__init__(f'Current folder is not in a git repository')


class InvalidRemoteSpecified(MergerException):
    '''Exception launched when the current directory is not a remote
       repository'''
    ERROR_CODE = 14

    def __init__(self, remote):
        super().__init__(f'Remote \'{remote}\' does not exists '
                         'or could not connect to it')


class CommitUserNotConfigured(MergerException):
    '''Exception launched when the current directory is not a remote
       repository'''
    ERROR_CODE = 15

    def __init__(self):
        super().__init__('Both \'user.name\' and \'user.email\' '
                         'configuration keys must be set up')


class MergeException(MergerException):
    '''Unhandled exception when trying to merge'''
    ERROR_CODE = 16

    def __init__(self):
            super().__init__('Unhandled exception when trying to merge '
                             'check output')


# Release Exceptions


class NotCreatedDescribeLog(MergerException):
    '''Exception launched when describe.log didn´t exist on the
       specific folder'''
    ERROR_CODE = 117

    def __init__(self, filepath):
        super().__init__('Describe log didnt exist, \n\tPlease place '
                         f'it on {filepath}')


class NotAcceptedOutputType(MergerException):
    ''' Exception launched when the output type is not accepted
        for the requested output '''
    ERROR_CODE = 118

    def __init__(self, output_type):
        super().__init__(f'Invalid output format \'{output_type}\'')


class InvalidCommitLine(MergerException):
    ''' Exception launched when the log line did not follow
        the expected format '''
    ERROR_CODE = 119

    def __init__(self, commit_line):
        super().__init__(f'Invalid Commit line\n{commit_line}')


class CouldNotCherryPick(MergerException):
    ''' Exception to handle problems at cherry picking '''
    ERROR_CODE = 120

    def __init__(self, sha_commit, output):
        super().__init__(f'Couldn not create branch \'{sha_commit}\'\n'
                         f'{output.strip()}')


class CouldNotCreateBranch(MergerException):
    ''' Exception to handle problems at creating branch '''
    ERROR_CODE = 121

    def __init__(self, branch_name, output):
        super().__init__(f'Couldn not create branch \'{branch_name}\'\n'
                         f'{output.strip()}')


class CouldNotFetchException(MergerException):
    ''' Exception to handle problems at fetching '''
    ERROR_CODE = 122

    def __init__(self, remote_name):
        super().__init__(f'Couldn not fetch from remote \'{remote_name}\'')


class BranchNotFoundException(MergerException):
    ''' Exception to handle when the branch is not found (ERROR CODE 3) '''
    ERROR_CODE = 123

    def __init__(self, branch_name):
        ''' Initializes Exception, must pass the name of the branch '''
        super().__init__(f'Couldn\'t find branch \'{branch_name}\'')


class TooManyProjectsFound(MergerException):
    ''' Exception launched when more than one project is found '''
    ERROR_CODE = 124

    def __init__(self, project_name, owner):
        super().__init__(f'Too many projects found by name \'{project_name}\''
                         f' and username \'{owner}\'')


class ProjectNotFound(MergerException):
    ''' Exception launched when no project is found with the criteria
        specified '''
    ERROR_CODE = 125

    def __init__(self, project):
        ''' Must pass the project name '''
        super().__init__(f'Project \'{project}\' could not be found')


class MalformedRemoteUrl(MergerException):
    ''' Exception for malformed URLs '''
    ERROR_CODE = 126

    def __init__(self, remote_type, remote_url):
        '''  '''
        super().__init__(f'Remote \'{remote_url}\' interpreted as '
                         f'{remote_type} has invalid format')


# Parser Exceptions


class MissingRequiredAttribute(MergerException):
    ''' Exception for malformed URLs '''
    ERROR_CODE = 110

    def __init__(self, meta_type, attribute):
        '''  '''
        error_message = f'Object {meta_type} missing attribute {attribute}'
        super().__init__(error_message)


class NotEnoughParams(MergerException):
    ''' Exception for Not Enough paramas at creating meta types '''
    ERROR_CODE = 111

    def __init__(self):
        '''  '''
        error_message = (f'Must provide either a path to an xml, '
                         f'an xml or values')
        super().__init__(error_message)


class InvalidPath(MergerException):
    ''' Exception launched when the path given is invalid '''
    ERROR_CODE = 112

    def __init__(self, path_err):
        error_message = (f'The following path is invalid: {path_err}')
        super().__init__(error_message)


class NoFullNameError(MergerException):

    def __init__(self, tagName):
        super().__init__( f'No tag found for {tagName}' )


class DuplicatedTags(MergerException):
    ''' Exception raised when duplicated tags are found '''
    ERROR_CODE = 113

    def __init__(self, filename):
        super().__init__( f'Duplicated Tags found in file {filename}' )
