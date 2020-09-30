''' Prepare branches module '''
from modules.utils import INFO_TAG, WARNING_LINE, call_subprocess
from modules.utils.exceptions import (BranchesUpToDateException,
                                      BranchNotFoundException,
                                      CouldNotFetchException,
                                      MergeConflictsException,
                                      MergeException,
                                      CouldNotCreateBranch,
                                      CouldNotCherryPick)
from modules.git.utils import get_branch_list, get_remote_url, parse_conflicts


def prepare_and_merge(source, target, remote, fetch_, reset):
    ''' Prepares source and target branches '''
    if fetch_:
        fetch(remote)

    validate_branches(source, target, remote)

    checkout(source, remote, reset=reset)
    checkout(target, remote, reset=reset)

    merge(source, target)


def fetch(remote, remote_url=None, count=0, verbose=True):
    ''' Fetchs from the remote '''
    remote_url = get_remote_url(remote, verbose=verbose)
    if not remote_url:
        print(f'{WARNING_LINE} Remote not found, omiting fetch')
    print(f'{INFO_TAG} Fetching from {remote} ({remote_url}) ...')
    _, errcode = call_subprocess(f'git fetch {remote}', verbose=verbose)
    if errcode > 0 and count > 3:
        raise CouldNotFetchException(remote)
    if errcode > 0:
        fetch(remote, remote_url=remote_url, count=count + 1, verbose=verbose)


def checkout(branch_name, remote, reset=False):
    ''' Checkots to passed branch, if reset flag is activated, resets
        to the branch in the remote '''
    print(f'{INFO_TAG} Checking out \'{branch_name}\'')
    get_actual_branch_command = 'git rev-parse --abbrev-ref HEAD | tr -d "\n"'
    actual_branch, _ = call_subprocess(get_actual_branch_command,
                                       verbose=False)

    if actual_branch != branch_name:
        print(f'\t- Checking out {branch_name}')
        call_subprocess(f'git checkout -f {branch_name}', verbose=True)
    else:
        print(f'\t- Currently on target branch')
    if reset:
        print(f'\t- Reseting local branch \'{branch_name}\' to remote branch '
              f'\'{remote}/{branch_name}\'')
        call_subprocess(f'git reset --hard {remote}/{branch_name}',
                        verbose=False)
    print()


def create_branch(branch_name, do_checkout=True):
    ''' Creates a branch, can select to checkout on it or not '''
    print(f'{INFO_TAG} Creating branch \'{branch_name}\'')
    create_command = (f'git checkout -b {branch_name}' if do_checkout
                      else f'git branch {branch_name}')
    output, status_code = call_subprocess(create_command, verbose=False)
    if status_code:
        raise CouldNotCreateBranch(branch_name, output)


def cherry_pick(commit_sha):
    ''' Cherry picks into current branch '''
    print(f'{INFO_TAG} Cherry picking \'{commit_sha}\'')
    create_command = (f'git cherry-pick {commit_sha} -m 1')  # TODO check this
    output, status_code = call_subprocess(create_command, verbose=False)
    if status_code:
        raise CouldNotCherryPick(commit_sha, output)


def validate_branches(source_branch, target_branch, remote):
    ''' Validate branches checking if exits in the current repo '''
    branches = get_branch_list(all_branches=True)

    print(f'{INFO_TAG} Validating branches source and target '
          f'branches in remote ({remote})')

    remote_source_branch = f'remotes/{remote}/{source_branch}'
    if not (source_branch in branches or remote_source_branch in branches):
        raise BranchNotFoundException(source_branch)

    remote_target_branch = f'remotes/{remote}/{target_branch}'
    if not (target_branch in branches or remote_target_branch in branches):
        raise BranchNotFoundException(target_branch)


def merge(source_branch, target_branch):
    ''' Merge branches '''
    print(f'{INFO_TAG} Merging {source_branch} into {target_branch}')
    command = (f'git merge --no-ff {source_branch} '
               f'-m "Merge branch {source_branch} into {target_branch}"')
    stdout, errcode = call_subprocess(command)
    if 'Already up to date.' in stdout:
        raise BranchesUpToDateException(source_branch, target_branch)
    if errcode != 0:
        if 'Merge conflict in' in stdout:
            raise MergeConflictsException(source_branch, target_branch,
                                          parse_conflicts(stdout))
        raise MergeException()
