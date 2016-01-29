#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import argparse
import sys
import os

from novaclient import utils as novaclient_utils
from tukey_middleware.modules.ids import Client

class TokenFileClient(object):
    ''' Handles saving the id_service_auth_token from the id client and
    providing with statement functionality. '''

    def __init__(self, args, path='~/.id_service_auth_token'):
        self.path = path
        self.args = args
        self.client = None

    def __enter__(self):
        try:
            if self.path is None:
                raise IOError
            with open(os.path.expanduser(self.path)) as id_file:
                id_service_auth_token = id_file.read()
        except IOError:
            id_service_auth_token = None
        self.client = client_from_args(self.args, id_service_auth_token)
        return self.client

    def __exit__(self, exit_type, value, traceback):
        try:
            if self.client.id_auth_token:
                with open(os.path.expanduser(self.path),
                        'w+') as id_file:
                    id_file.write(self.client.id_auth_token)
        except KeyError:
            pass

def err(msg):
    print >> sys.stderr, msg

def client_from_args(args, id_service_auth_token=None):
    ''' From args as returned by argparse.ArgumentParser.parse_args()
    format arguments to tukey_middleware.moduels.ids.Client and return new
    object '''
    return Client(args.id_service, os_username=args.os_username,
            os_tenant_name=args.os_tenant_name, os_password=args.os_password,
            os_auth_url=args.os_auth_url, os_auth_token=args.os_auth_token,
            interface=args.interface,
            id_service_auth_token=id_service_auth_token,
            swift_auth_url=args.swift_auth_url,
            swift_tenant=args.swift_tenant,
            swift_username=args.swift_username,
            swift_password=args.swift_password)


def add_openstack_env(arg_parser):
    ''' Add OS_ environment variables to and argparse.ArgumentParser.'''

    arg_parser.add_argument('--os-username', metavar='<auth-user-name>',
        default=novaclient_utils.env('OS_USERNAME', 'NOVA_USERNAME'),
        help='Defaults to env[OS_USERNAME].')
    arg_parser.add_argument('--os_username', help=argparse.SUPPRESS)

    arg_parser.add_argument('--os-password', metavar='<auth-password>',
        default=novaclient_utils.env('OS_PASSWORD', 'NOVA_PASSWORD'),
        help='Defaults to env[OS_PASSWORD].')
    arg_parser.add_argument('--os_password', help=argparse.SUPPRESS)

    arg_parser.add_argument('--os-tenant-name', metavar='<auth-tenant-name>',
        default=novaclient_utils.env('OS_TENANT_NAME', 'NOVA_PROJECT_ID'),
        help='Defaults to env[OS_TENANT_NAME].')
    arg_parser.add_argument('--os_tenant_name', help=argparse.SUPPRESS)

    arg_parser.add_argument('--os-auth-url', metavar='<auth-url>',
        default=novaclient_utils.env('OS_AUTH_URL', 'NOVA_URL'),
        help='Defaults to env[OS_AUTH_URL].')
    arg_parser.add_argument('--os_auth_url', help=argparse.SUPPRESS)

    arg_parser.add_argument('--os-auth-token', metavar='<auth-token>',
        default=novaclient_utils.env('OS_AUTH_TOKEN', 'NOVA_AUTH_TOKEN'),
        help='Defaults to env[OS_AUTH_TOKEN].')
    arg_parser.add_argument('--os_auth_token', help=argparse.SUPPRESS)

    arg_parser.add_argument("--swift-auth-url", type=str)
    arg_parser.add_argument("--swift-username", type=str)
    arg_parser.add_argument("--swift-tenant", type=str)
    arg_parser.add_argument("--swift-password", type=str)

