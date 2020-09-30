''' Utils module, has auxiliar methods '''
import configparser
import datetime
import itertools
import os
import os.path as op
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from enum import Enum

from colorama import Fore, init

init(autoreset=True)
INFO_TAG = f'{Fore.YELLOW}[INFO]{Fore.RESET}'
FATAL_LINE = f'{Fore.RED}[FATAL]'
FATAL_TAG = f'{Fore.RED}[FATAL]{Fore.RESET}'
SUCCESS_LINE = f'{Fore.GREEN}[SUCCESS]'

CREDENTIALS_HOME = os.environ.get('CREDENTIALS_HOME')
BUILD_URL = os.environ.get('BUILD_URL', 'https://jenkins.com/')


def get_credentials(source):
    ''' Gets credentials for the passed source, source must be a .properties
        in $CREDENTIALS_HOME (file can be foldered) '''
    config_file_path = f'{CREDENTIALS_HOME}/{source}.properties'
    config = configparser.ConfigParser()
    with open(config_file_path) as lines:
        lines = itertools.chain(("[top]",), lines)  # This line does the trick.
        config.read_file(lines)
    username = config.get('top', 'username')
    password = config.get('top', 'password')
    replyto = config.get('top', 'replyto')
    return username, password, replyto


def get_salutation():
    ''' Returns salutation based on the current time '''
    current_time = datetime.datetime.now().time()
    if current_time < datetime.time(12):
        return 'Buenos dias'
    elif current_time < datetime.time(21):
        return 'Buenas tardes'
    return 'Buenas noches'


def get_smtp_server(server_address, username, password, tls, no_login):
    ''' Intializes the smtp server '''
    print(f'{INFO_TAG} Loggin in \'{server_address}\'')
    server = smtplib.SMTP(server_address)
    if tls:
        server.starttls()
    if not no_login:
        server.login(username, password)
    print(f'{INFO_TAG} Logged in \'{server_address}\' correctly')
    return server


def print_key_value_list(top_message, items):
    ''' Prints a key value list '''
    message = f'{top_message}'
    for key, value in items:
        message += f'\n{key_value_list(key, value)}'
    print(message)


def key_value_list(key, value):
    ''' Returns a pretty formated list, with key in cyan '''
    return f'\t- {Fore.CYAN}{key}{Fore.RESET}: {value}'


def get_remote_url(remote_url):
    ''' Gets the remote url bassed on the repository in the PWD '''
    if '@' in remote_url:
        ssh_regex = r'git@(.*):(.*)\/(.*)\.git'
        result = re.findall(ssh_regex, remote_url)
        if result and len(result) == 1:
            host, user, project = result[0]
            return f'http://{host}/{user}/{project}'
        else:
            raise MalformedRemoteUrl('SSH', remote_url)
    else:
        http_regex = r'\.git$'
        return re.sub(http_regex, '', remote_url)


def get_mr_url(remote_url, iid):
    remote_url = get_remote_url(remote_url)
    mr_url = f'{remote_url}/merge_requests/{iid}'
    return mr_url


def attach_files(msg, files, folder, pwd, sel_photos):
    ''' Attach files passed by param (& image files little bit hardcoded) '''
    for filename in files:
        part = MIMEBase('application', "octet-stream")
        with open(f"{folder}/{filename}", 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{op.basename(filename)}"')
        msg.attach(part)

    path = f'{pwd}/resources/imgs/'
    for photo in sel_photos:
        photo = path + photo.value
        part = MIMEBase('application', "octet-stream")
        with open(photo, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{op.basename(photo)}"')
        msg.attach(part)


def get_allure_url():
    ''' Returns the allure url for the passed build url '''
    url = BUILD_URL + 'allure'
    return url


class Resources(Enum):
    ''' Resources enumerator for referencing images '''
    CLIENT_LOGO = 'CLIENT.png'
    GIT_BRANCH = 'git_branch.png'
    PULL_REQUEST = 'pull_request.png'
    LS_LOGO = 'liquid_studio.png'
    GITLAB_LOGO = 'gitlabLogo.png'
    JENKINS_LOGO = 'jenkins.png'
    ALLURE_LOGO = 'allure.png'


class MalformedRemoteUrl(Exception):
    ''' Malformed Remote URL exception, launched in get_remote_url() '''
    def __init__(self, remote_type, remote_url):
        super().__init__(f'Remote \'{remote_url}\' interpreted as '
                         f'{remote_type} has invalid format')
