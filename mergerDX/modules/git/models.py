''' Model module for git package '''
from enum import Enum

from modules.git.utils import get_short_sha, get_tag_commit
from modules.utils import (INFO_TAG, WARNING_TAG, call_subprocess,
                           truncate_string)
from modules.utils.exceptions import InvalidCommitLine, NotAcceptedOutputType
from modules.utils.models import OutputType


class Tag:
    ''' Tag Entity '''
    def __init__(self, tag_name, version=None, sha_commit='HEAD'):
        self.tag_name = tag_name
        self.sha_commit = sha_commit
        self.next_version = version

    def get_next_version(self, version_type):
        ''' Returns the next version, based on the version type '''
        if not self.next_version:
            if version_type == Version.FIX:
                self.next_version = ''
            elif version_type == Version.MAJOR:
                self.next_version = ''
            elif version_type == Version.MINOR:
                self.next_version = ''
        return self.next_version

    def get_sha_commit(self, short=False, force=False):
        ''' Returns the sha commit of the tag, default is long version '''
        if force or self.sha_commit:
            self.sha_commit = get_tag_commit(self.tag_name)
        elif self.sha_commit.startswith('HEAD'):
            print(f'{WARNING_TAG} Tag not created still '
                  f'referencing {self.sha_commit}')
        return (self.sha_commit if not short
                else get_short_sha(self.sha_commit))

    def create(self):
        ''' Creates the tag in the repository '''
        command = f'git tag {self.tag_name} {self.sha_commit}'
        call_subprocess(command, verbose=False)
        self.sha_commit = self.get_sha_commit(force=True)
        print(f'{INFO_TAG} Tag {self.tag_name} created '
              f'in commit {self.sha_commit}')

    @staticmethod
    def get_last_tag():
        ''' Returns the last tag name of the current branch '''
        command = 'git describe --abbrev=0 --tags'
        stdout, _ = call_subprocess(command, verbose=False)
        return Tag(stdout)


class MergeRequest:
    ''' Merge Request wrapper class '''
    TRUNCATE_SIZE = 60

    def __init__(self, response_data):
        self.title = response_data['title']
        self.truncated_title = truncate_string(self.title, self.TRUNCATE_SIZE)
        self.iid = response_data['iid']
        self.id_ = response_data['id']
        self.owner_name = response_data['author']['name']
        self.owner_username = response_data['author']['username']
        self.sha = response_data['merge_commit_sha']
        self.ssha = get_short_sha(self.sha)
        self.merge_date = response_data['updated_at']

    def __repr__(self):
        return f'<{self.iid}, {self.truncated_title}>'

    def __str__(self):
        extra = ' ' * (self.TRUNCATE_SIZE + 5 - len(self.truncated_title))
        iid = f'{self.iid}'
        return f'MR[{iid}] {self.truncated_title}{extra}{self.ssha}'


class MergeCommit():
    ''' Model for Merge Commits '''
    SIZES = {}

    def __init__(self, sha=None, author=None, commit_date=None,
                 subject=None, commit_log=None):
        if not commit_log:
            self.sha = sha
            self.author = author
            self.commit_date = commit_date
            self.subject = subject
        else:
            list_data = commit_log.split('$.$')
            list_pretty = list(PrettyFormat)

            if len(list_data) != len(list_pretty):
                raise InvalidCommitLine(commit_log)

            for index, value in enumerate(list_data):
                attribute = list_pretty[index].value['name']
                if attribute not in self.SIZES:
                    self.SIZES[attribute] = len(value)
                else:
                    self.SIZES[attribute] = max(self.SIZES[attribute],
                                                len(value))
                self.__setattr__(attribute, value)
            if self.commit_date:
                self.commit_date = self.commit_date.split(' +')[0]
        # self.ssha = get_short_sha(self.sha)

    def output(self, file_type, columns):
        ''' Returns merge commit for the desired output and columns '''
        if file_type == OutputType.CSV.value:
            return ';'.join([self.__getattribute__(name) for name in columns])
        if file_type == OutputType.SCREEN.value:
            return ' | '.join([truncate_string(self.__getattribute__(name),
                                               self.SIZES[name], fill=True)
                               for name in columns])

    @staticmethod
    def get_header(columns, output_type):
        ''' Returns the header based on the columns/output type '''
        if output_type == OutputType.SCREEN.value:
            return ' | '.join([truncate_string(name, MergeCommit.SIZES[name],
                                               fill=True).upper()
                               for name in columns])
        elif output_type == OutputType.CSV.value:
            return ';'.join([column.upper() for column in columns])
        raise NotAcceptedOutputType(output_type)

    @staticmethod
    def get_merge_commits(source_branch):
        ''' Returns the merge commits of the current branch '''
        filter_string = (f'--first-parent {source_branch}' if source_branch
                         else '')
        pretty = f'--pretty=format:' + '$.$'.join([pretty.value['code']
                                                   for pretty in PrettyFormat])
        list_command = f'git log --merges {pretty} --all {filter_string}'
        output, _ = call_subprocess(list_command, verbose=False)

        return [MergeCommit(commit_log=merge_commit)
                for merge_commit in output.splitlines()]


class Version(Enum):
    ''' Types of versions '''
    FIX = 'fix'
    MINOR = 'minor'
    MAJOR = 'major'


class MergeTypes(Enum):
    ''' Types of versions '''
    MERGE_COMMITS = 'sha'
    MERGE_REQUEST = 'mr'


class PrettyFormat(Enum):
    ''' Types of versions '''
    SHAS = {'name': 'ssha', 'code': '%h'}
    AUTHOR = {'name': 'author', 'code': '%cn'}
    COMMIT_DATE = {'name': 'commit_date', 'code': '%cD'}
    COMMIT_SUBJECT = {'name': 'subject', 'code': '%s'}

    @staticmethod
    def get_name_list():
        ''' Return all the names of the values '''
        return [item.value['name'] for item in PrettyFormat]
