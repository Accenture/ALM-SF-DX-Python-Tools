''' Utils module of git package '''
import re

from modules.utils import call_subprocess
from modules.utils.exceptions import MalformedRemoteUrl


def get_short_sha(long_sha):
    ''' Returns the short (5 chars version) of the commit '''
    command = f'git rev-parse --short {long_sha}'
    short_sha, _ = call_subprocess(command, verbose=False)
    return short_sha.strip()


def get_tag_commit(tag_name):
    ''' Returns the tag commit associated to the tag name '''
    command = f'git rev-list -n 1 {tag_name}'
    stdout, _ = call_subprocess(command)
    return stdout.strip()


def get_branch_list(all_branches=False):
    ''' Returns a list of the branches in the current repository '''
    all_parameter = '-a' if all_branches else ''
    branches, _ = call_subprocess(f'git branch --list {all_parameter}',
                                  verbose=False)
    branches = [branch.replace('* ', '').strip()
                for branch in branches.split('\n') if branch]
    return branches


def get_repository_info(remote_url):
    ''' Extracts owner and project from a remote url '''
    if '@' in remote_url:
        ssh_regex = r'git@(.*):(.*)\/(.*)\.git'
        result = re.findall(ssh_regex, remote_url)
        if result and len(result) == 1:
            host, owner, project = result[0]
            if not host.startswith('http://'):
                host = f'http://{host}'
            return host, owner, project
        raise MalformedRemoteUrl('SSH', remote_url)
    else:
        http_regex = r'(http[s]:\/\/.*)\/(.*)\/(.*)\.git'
        result = re.findall(http_regex, remote_url)
        if result and len(result) == 1:
            return result[0]
        raise MalformedRemoteUrl('HTTP', remote_url)


def get_remote_url(remote, verbose=True):
    ''' Extracts the remote url of the rmeote passed '''
    remotes, _ = call_subprocess('git remote -v', verbose)
    remote = [remote_line.replace(' ', '\t').split('\t')[1]
              for remote_line in remotes.split('\n')
              if 'fetch' in remote_line and remote in remote_line]
    return remote[0] if remote else None


def parse_conflicts(stdout):
    ''' Gets the number of conflicts from the output of a merge '''
    return stdout.count('Merge conflict in')


def get_file(filepath, revision):
    ''' Prints the file from the passed revision '''
    output, _ = call_subprocess(f'git show {revision}:"{filepath}"', False)
    return output.encode( 'utf-8' )


def is_git_repository():
    validate_repo = 'git rev-parse --is-inside-work-tree'
    _, returncode = call_subprocess(validate_repo, False)
    return returncode == 0


def is_valid_remote(remote):
    validate_remote = f'git ls-remote --exit-code {remote}'
    _, returncode = call_subprocess(validate_remote, False)
    return returncode == 0


def is_commit_user_configured():
    get_name = 'git config user.name'
    get_email = 'git config user.email'
    name, _ = call_subprocess(get_name, False)
    email, _ = call_subprocess(get_email, False)

    return bool(name.strip()) and bool(email.strip())
