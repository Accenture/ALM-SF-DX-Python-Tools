''' Send email module of the LS CI/CD Integration toolkit,
    implements the necessary methods to notify of the results
    of the CI/CD process'''
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import traceback

from modules.custom_argparser import parse_args
from modules.utils import (FATAL_LINE, INFO_TAG, SUCCESS_LINE, Resources,
                           attach_files, get_allure_url, get_remote_url,
                           get_salutation, get_smtp_server,
                           print_key_value_list, get_mr_url)

__version__ = "1.2"

# Environment Variables
MR_IID = os.environ.get('gitMergeRequestId', '125')
MR_TITLE = os.environ.get('gitMergeRequestTitle', 'This is a Mock Title')
TARGET_BRANCH = os.environ.get('gitTargetBranch', 'mock')
SOURCE_BRANCH = os.environ.get('gitSourceBranch', 'feature/mock')
MR_STATE = os.environ.get('gitMergeRequestState')
GITLAB_USERNAME = os.environ.get('gitUserName')
GITLAB_EMAIL = os.environ.get('gitUserEmail')
BUILD_ID = os.environ.get('BUILD_ID')
JENKINS_URL = os.environ.get('JENKINS_URL', 'https://jenkins.com/')
JOB_BASE_NAME = os.environ.get('JOB_BASE_NAME')

# Constants
ARTIFACT_FOLDER = "artifacts_folder"
BLUEOCEAN_URL = (f'{JENKINS_URL}blue/organizations/jenkins/{JOB_BASE_NAME}'
                 f'/detail/{JOB_BASE_NAME}/{BUILD_ID}/pipeline')
REMOTE_URL_ROUGH = os.environ.get('gitSourceRepoHttpUrl',
                                  'https://gitlab.com/mock/mock.git')
PWD = os.path.dirname(os.path.abspath(__file__))
ALLURE_URL = get_allure_url()
MR_URL = os.environ.get( 'gitMergeRequestUrl' ) if os.environ.get( 'gitMergeRequestUrl', '' ) else get_mr_url(REMOTE_URL_ROUGH, MR_IID)


def notify_validate(smtp_server, status, recipients,
                    recipients_cc, files, replyto=None):
    ''' Notifies of the result of a validate, requires:
        - Logged in smtp server
        - The result of the validation ['error', 'success']
        - The recipients of the email
        - The Carbon Copy Recipients of the email
        - The files to attach (images not included)
        - The replyto email, if None === the email used to log in'''
    print_key_value_list(f'{INFO_TAG} Sending \'selenium\' email:',
                         [('Status', status), ('Files', files),
                          ('Recipients', recipients),
                          ('Recipients CC', recipients_cc),
                          ('Reply-To', replyto)])
    salutation = get_salutation()

    with open(f'{PWD}/resources/templates/validate/{status}.html',
              encoding='utf8') as template:
        html_file = template.read()

    template = Template(html_file)
    html = template.safe_substitute(SALUTATION=salutation, MR_TITLE=MR_TITLE,
                                    TARGET_BRANCH=TARGET_BRANCH,
                                    MR_URL=MR_URL, status=status,
                                    BUILD_ID=BUILD_ID, MR_IID=MR_IID,
                                    SOURCE_BRANCH=SOURCE_BRANCH,
                                    JOB_LINK=BLUEOCEAN_URL)

    html = html.replace('../../imgs/', 'cid:')

    msg = MIMEMultipart()
    msg["Subject"] = f"[JENKINS][{status.upper()}] #{MR_IID} - {MR_TITLE}"
    msg["From"] = smtp_server.user
    msg["To"] = ", ".join(recipients)
    msg["Cc"] = ", ".join(recipients_cc)
    if replyto:
        msg.add_header('reply-to', replyto)
    body = MIMEText(html, 'html')
    # attach the body with the msg instance
    msg.attach(body)
    sel_photos = [Resources.GIT_BRANCH,
                  Resources.LS_LOGO, Resources.JENKINS_LOGO,
                  Resources.GITLAB_LOGO, Resources.PULL_REQUEST]
    attach_files(msg, files, ARTIFACT_FOLDER, PWD, sel_photos)

    smtp_server.sendmail(msg["From"], recipients + recipients_cc,
                         msg.as_string())


def selenium(smtp_server, recipients, recipients_cc, replyto=None):
    ''' Notifies selenium errors '''
    print_key_value_list(f'{INFO_TAG} Sending \'selenium\' email:',
                         [('Recipients', recipients),
                          ('Recipients CC', recipients_cc),
                          ('Reply-To', replyto)])
    salutation = get_salutation()

    with open(f'{PWD}/resources/templates/errors/selenium_error.html',
              encoding='utf8') as template:
        html_file = template.read()

    template = Template(html_file)
    html = template.safe_substitute(SALUTATION=salutation, MR_TITLE=MR_TITLE,
                                    ALLURE_URL=ALLURE_URL, BUILD_ID=BUILD_ID,
                                    SOURCE_BRANCH=SOURCE_BRANCH,
                                    JOB_LINK=BLUEOCEAN_URL)

    html = html.replace('../../imgs/', 'cid:')

    msg = MIMEMultipart()
    msg["Subject"] = f"[JENKINS][SELENIUM-ERROR] #{MR_IID} - {MR_TITLE}"
    msg["From"] = smtp_server.user  # TODO peta aqui
    msg["To"] = ", ".join(recipients)
    msg["Cc"] = ", ".join(recipients_cc)
    msg.add_header('reply-to', replyto)
    body = MIMEText(html, 'html')
    # attach the body with the msg instance
    msg.attach(body)
    sel_photos = [Resources.GIT_BRANCH, Resources.CLIENT_LOGO,
                  Resources.LS_LOGO, Resources.JENKINS_LOGO,
                  Resources.ALLURE_LOGO]
    attach_files(msg, [], None, PWD, sel_photos)

    smtp_server.sendmail(msg["From"], recipients + recipients_cc,
                         msg.as_string())


def __handle_options(smtp_server, args):
    ''' Switcher for different options '''
    if args.option == 'validate':
        notify_validate(smtp_server, args.status, args.recipients,
                        args.recipientsCC, args.file, args.reply_to)
    elif args.option == 'selenium':
        selenium(smtp_server, args.recipients,
                 args.recipientsCC, args.reply_to)
    else:
        raise NotImplementedError(f'Option \'{args.option}\' is not yet '
                                  'implemented, btw how did you get here?')


def main():
    ''' Main methods, parse args and redirects based on the option selected '''
    smtp_server = None
    args = parse_args()
    if args.option == 'version':
        print(__version__)
        sys.exit(0)
    try:
        smtp_server = get_smtp_server(args.server_address, args.username,
                                      args.password, args.tls, args.no_login)
        if not args.reply_to and not args.no_login:
            args.reply_to = smtp_server.user
        __handle_options(smtp_server, args)
        print(f"{SUCCESS_LINE} Email has been sent successfully")
    except smtplib.SMTPAuthenticationError as excep:
        print(f'{FATAL_LINE} Password for \'{args.username}\' is not valid '
              f'{excep.__class__.__name__}')
        print(excep)
        sys.exit(1)
    except smtplib.SMTPServerDisconnected as excep:
        print(f'{FATAL_LINE} Did you just cut the cable? '
              f'{excep.__class__.__name__}')
        sys.exit(2)
    except Exception as excep:  # pylint: disable=W0703,W0612
        print(f'{FATAL_LINE} Unhandled exception\n{traceback.format_exc()}')
        sys.exit(3)
    finally:
        quit_server(smtp_server)


def quit_server(smtp_server):
    ''' Quit Server handling errors '''
    try:
        if smtp_server:
            smtp_server.quit()
    except:  #noqa # pylint: disable=W0702
        print(f'{INFO_TAG} Could not quit server')


if __name__ == '__main__':
    main()
