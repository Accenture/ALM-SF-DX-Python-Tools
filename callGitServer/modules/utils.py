''' Utils module '''
import subprocess

from colorama import init as colorama_init
from colorama import Fore, Style

colorama_init(autoreset=True)

FILE_TAG            = f'{Fore.YELLOW}[FILE]{Fore.RESET}'
DATA_TAG            = f'{Fore.MAGENTA}[DATA]{Fore.RESET}'
INFO_TAG            = f'{Fore.YELLOW}[INFO]{Fore.RESET}'
INFO_LINE           = f'{Fore.YELLOW}[INFO]'
ERROR_TAG           = f'{Fore.RED}[ERROR]{Fore.RESET}'
ERROR_LINE          = f'{Fore.RED}[ERROR]'
SUCCESS_TAG         = f'{Fore.GREEN}[SUCCESS]{Fore.RESET}'
SUCCESS_LINE        = f'{Fore.GREEN}[SUCCESS]'
WARNING_TAG         = f'{Fore.MAGENTA}[WARNING]{Fore.RESET}'
WARNING_LINE        = f'{Fore.MAGENTA}[WARNING]'

ENV_BUILD_URL       = 'RUN_DISPLAY_URL'
ENV_BUILD_ID        = 'BUILD_DISPLAY_NAME'
ENV_JOB_NAME        = 'JOB_NAME'
ENV_TARGET_BRANCH   = 'gitTargetBranch'
ENV_WORKSPACE       = 'WORKSPACE'

MARKDOWN_BULLETS    = ['+ ', '- ', '* ']


def call_subprocess(command, verbose=True):
    ''' Calls subprocess, returns output and return code,
        if verbose flag is active it will print the output '''
    try:
        stdout = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                         shell=True).decode('utf-8')
        if verbose:
            print_output(f'{Style.DIM}{stdout}{Style.NORMAL}')
        return stdout, 0
    except subprocess.CalledProcessError as exc:
        output = exc.output.decode('utf-8')
        returncode = exc.returncode
        if verbose:
            print(f'{ERROR_TAG} Subprocess returned non-zero exit '
                  f'status {returncode}')
            print_output(output, color=Fore.RED)
        return output, returncode


def print_key_value_list(top_message, items):
    ''' Prints a key value list '''
    message = f'{top_message}'
    for key, value in items:
        message += f'\n{key_value_list(key, value)}'
    print(message)


def print_output(output, color='', tab_level=1):
    ''' Prints output in the color passed '''
    formated = '\t' * tab_level + output.replace('\n', '\n' + '\t' * tab_level)
    print(f'{color}{formated}{Fore.RESET}')


def key_value_list(key, value):
    ''' Returns a pretty formated list, with key in cyan '''
    return f'\t- {Fore.CYAN}{key}{Fore.RESET}: {value}'