''' Module for remote-related methods '''
import json
import urllib
import urllib.parse
import urllib.request
import ssl

from modules.git.models import MergeRequest
from modules.git.utils import get_remote_url, get_repository_info
from modules.utils.exceptions import ProjectNotFound, TooManyProjectsFound


# Create context to avoid SSL verifications
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_project_id(private_token, ssl_verify):
    ''' Get project id from the gitlab host passed '''
    remote_url = get_remote_url('origin', verbose=False)
    gitlab_url, owner, project_name = get_repository_info(remote_url)

    querystring = {'search': project_name, 'membership': 'true'}
    url = f'{gitlab_url}/api/v4/projects?{urllib.parse.urlencode(querystring)}'
    headers = {'Private-Token': private_token}

    request = urllib.request.Request(url=url, headers=headers, method='GET')
    if ssl_verify:
        with urllib.request.urlopen(request) as response:
            projects = json.load(response)
    else:
        with urllib.request.urlopen(request, context=CTX) as response:
            projects = json.load(response)

    if not projects:
        raise ProjectNotFound(project_name)
    elif len(projects) != 1:
        projects = [project for project in projects
                    if project['owner']['username'] == owner
                    and project['name'] == project_name]
        if len(projects) != 1:
            raise TooManyProjectsFound(project_name, owner)

    return projects[0]['id']


def get_merge_requests(project_id, private_token, target_branch='',
                       page=0, per_page=25, ssl_verify=False):
    ''' Gets merge request from the gitlab host specified into the target
        branch passed as param at the project passed '''

    remote_url = get_remote_url('origin', verbose=False)
    gitlab_url, _, _ = get_repository_info(remote_url)
    querystring = {'state': 'merged', 'target_branch': target_branch,
                   'per_page': per_page, 'page': page}
    url = (f'{gitlab_url}/api/v4/projects/{project_id}/merge_requests?'
           f'{urllib.parse.urlencode(querystring)}')

    headers = {'Private-Token': private_token}

    request = urllib.request.Request(url=url, headers=headers, method='GET')

    if ssl_verify:
        with urllib.request.urlopen(request) as response:
            merge_requests_dict = json.load(response)
    else:
        with urllib.request.urlopen(request, context=CTX) as response:
            merge_requests_dict = json.load(response)

    merge_requests = {merge_request['iid']: MergeRequest(merge_request)
                      for merge_request in merge_requests_dict}
    return merge_requests
