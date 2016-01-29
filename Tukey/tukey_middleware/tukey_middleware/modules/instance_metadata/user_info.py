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

import flask
import json
import requests

from flask import request, g
from keystoneclient.v2_0 import client
from tukey_middleware import local_settings
from tukey_middleware.auth.base import TukeyAuthException
from tukey_middleware.flask_utils import with_user, return_error

rest = flask.Blueprint('v0', __name__)

settings = local_settings.vm_ip_auth

@rest.route('/')
def default_info():
    '''
    Return JSON packed with all of the user's info:
        username, password, identifiers.
    '''
    return get_info(cloud_name=settings["default"])

@rest.route('/cloud')
def get_cloud():
    ''' return the default cloud'''
    return settings["default"]


@rest.route('/<cloud_name>/')
@return_error
@with_user(rest, use_cloud_name=True)
def get_info(cloud_name):
    ''' return all of the user info '''
    try:
        password = g.user.password()
        identifiers = g.user.identifiers()
    except TukeyAuthException:
        password = ""
        identifiers = []

    return json.dumps({
        "username": g.user.username(),
        "tenant_name": g.user.tenant_name(),
        "password": password,
        "identifiers": identifiers,
        "cloud_name": cloud_name
        })


@rest.route('/password')
def default_password():
    '''
    Return the user's samba/OpenStack password.
    If there is no cloud specified look in the settings file for a default.
    This allows the OSDC init-cloud.sh to be the same across clouds
    '''
    return get_password(cloud_name=settings["default"])


@rest.route('/username')
def default_username():
    return get_username(cloud_name=settings["default"])


@rest.route('/identifiers')
def default_identifiers():
    return get_identifiers(cloud_name=settings["default"])


@rest.route('/tenant_name')
def default_tenant_name():
    return get_tenant_name(cloud_name=settings["default"])


@rest.route('/<cloud_name>/password')
@return_error
@with_user(rest, use_cloud_name=True)
def get_password(cloud_name=None):
    ''' return the users openstack/samba password '''

    return g.user.password() if g.user.password() is not None else ""


@rest.route('/<cloud_name>/username')
@return_error
@with_user(rest, use_cloud_name=True)
def get_username(cloud_name=None):
    ''' return the username '''

    return g.user.username() if g.user.username() is not None else ""


@rest.route('/<cloud_name>/identifiers')
@return_error
@with_user(rest, use_cloud_name=True)
def get_identifiers(cloud_name=None):
    ''' return single sign on indentifiers '''

    return json.dumps(g.user.identifiers())


@rest.route('/<cloud_name>/tenant_name')
@return_error
@with_user(rest, use_cloud_name=True)
def get_tenant_name(cloud_name=None):
    ''' return the tenant name '''

    return g.user.tenant_name()
