''' Argparse module '''
import argparse
import sys
from modules.utils import get_credentials


def parse_args():
    ''' Arg parser method, initializes the possible subparsers '''
    parser = argparse.ArgumentParser()

    # Global arguments
    # Credentials Specification
    credentials_arguments(parser)

    parser.add_argument('-rto', '--reply-to',
                        help='ReplyTo address of the email')

    subparsers = parser.add_subparsers(help='commands', dest='option')
    subparsers.required = True

    # Version
    subparsers.add_parser('version', help='Returns script version')

    # Notify Validate Subparser
    validate_parser(subparsers.add_parser('validate', help='Notifies the '
                                          'result of a validate'))

    # Notify Selenium Tests Error
    selenium_parser(subparsers.add_parser('selenium', help='Notifies errors '
                                          'in selenium tests'))

    args = parser.parse_args()

    # Custom Validations and inits that cannot be acomplished using argparse
    args = custom_postvalidations(parser, args)

    return args


def credentials_arguments(parser):
    ''' Adds general credentials arguments to passed parser '''
    parser.add_argument('-nl', '--no-login', action='store_true',
                        default=False, help='Donnot login in the SMTP server')
    parser.add_argument('-c', '--credentials',
                        default='email/notification',
                        help='Specify custom credentials')
    parser.add_argument('-notls', '--no-tls', action='store_false',
                        dest='tls', default=True,
                        help='Toggle Login without TLS')
    parser.add_argument('-sa', '--server-address',
                        default="smtp.gmail.com:587",
                        help='SMTP Server address with port')
    parser.add_argument('-u', '--username',
                        help='SMTP Server username')
    parser.add_argument('-p', '--password',
                        help='SMTP Server password')


def validate_parser(subparser):
    ''' Adds validate notification arguments to passed subparser '''
    subparser.add_argument('--status', '-s', required=True,
                           choices=['success', 'error'],
                           help='Status of the email (Success/Error)')
    subparser.add_argument('--recipients', '-r', required=True, nargs='+',
                           help='Recipients of the email')
    subparser.add_argument('--recipientsCC', '-rCC', default=[], nargs='+',
                           help='Carbon Copy recipients of the email')
    subparser.add_argument('--file', '-f', default=[], nargs='+',
                           help='Recipients_cc of the email')


def selenium_parser(subparser):
    ''' Adds selenium notification arguments to passed subparser '''
    subparser.add_argument('--recipients', '-r', required=True, nargs='+',
                           help='Recipients of the email')
    subparser.add_argument('--recipientsCC', '-rCC', default=[], nargs='+',
                           help='Carbon Copy recipients of the email')


def custom_postvalidations(parser, args):
    ''' Adds extra validations to passed parser '''
    credentials_specified = '-c' in sys.argv or '--credentials' in sys.argv
    usn_pwd_specified = args.username or args.password
    if args.no_login and (credentials_specified or usn_pwd_specified):
        parser.error('Cannot specify no-login and login...')
    if credentials_specified and usn_pwd_specified:
        parser.error('Cannot provide credentials and username|password')

    # Custom explicit inclusion
    if bool(args.username) != bool(args.password):  # xor operator
        parser.error('Username and password are mutually inclusive')

    # Populate username and password with credentials file
    if not usn_pwd_specified and args.credentials:
        # Populate login values based on credentials file
        username, password, replyto = get_credentials('email/notification')
        if bool(args.username) != bool(args.password):
            parser.error('Username and password are mutually inclusive')
        parser.set_defaults(username=username, password=password,
                            reply_to=replyto)
        return parser.parse_args()
    return args
