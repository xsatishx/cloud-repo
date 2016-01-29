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


from flask import request
import flask
import socket

from . import local_settings
from .auth.base import TukeyAuthException
from .auth.caching_auth import CachingAuth
from .auth.vm_ip_auth import VmIpAuth
from .auth.keystone_auth import KeystoneAuth
from functools import wraps


class Unauthorized(Exception):
    ''' Exception for acl violations '''

    def __init__(self, message):
        Exception.__init__(self, message)


class FormatError(Exception):
    ''' Throw when there is a violation of record formats'''
    pass


class NotFound(Exception):
    ''' Throw when a requested resource does not exist'''
    def __init__(self, message=None):
        Exception.__init__(self, message)


def with_user(rest, use_cloud_name=False):
    def inner(fn):
        ''' Provide the decorated function with a g.user object.  If the
        decorated function has a named arg "cloud_name" use that for the name
        of the cloud when building the user if use_cloud_name.
        '''

        @wraps(fn)
        def decorated(*args, **kwds):
            if use_cloud_name and "cloud_name" in kwds:
                flask.g.user = get_user_from_request(
                        rest.registry.get_cloud_by_id,
                        cloud_name=kwds["cloud_name"])
            else:
                flask.g.user = get_user_from_request(
                        rest.registry.get_cloud_by_id)
            return (fn(*args, **kwds), 200,
                    {"x-id-auth-token": flask.g.user.id_auth_token})
        return decorated
    return inner


def return_error(fn):
    ''' Catch a set of exceptions and return http error messages based on the
    type of exception.  This allows our functions to be Flask agnostic'''

    @wraps(fn)
    def decorated(*args, **kwds):
        #if local_settings.debug:
        #    return fn(*args, **kwds)
        try:
            return fn(*args, **kwds)
        except TukeyAuthException:
            return ("Unauthorized", 403)
        except Unauthorized as e:
            return (e.message, 403)
        except FormatError:
            return ("Incorrect record format", 400)
        except NotFound as e:
            if e.message:
                return (e.message, 404)
            return ("Record not found", 404)
    return decorated


def get_user_from_request(get_cloud_func,
        cloud_name=local_settings.vm_ip_auth["default"]):
    ''' return user object using requestor ip or openstack creds'''
    headers = request.headers
    id_token = headers.get("x-id-auth-token", None)

    if "x-auth-token" in headers:
        user = CachingAuth(auth=KeystoneAuth(cloud_name,
                headers["x-auth-token"], headers["x-auth-user-name"],
                headers["x-auth-tenant-name"]), token=id_token)
    else:
        user = CachingAuth(auth=VmIpAuth(get_cloud_func, cloud_name,
                request.remote_addr), token=id_token)

    return user


def same_server(service):
    ''' determines whether "service" is running in the same server instance
    as this '''

    my_addr, my_port = request.host.split("/")[-1].split(":")
    my_host = socket.gethostbyaddr(my_addr)[0]

    service_addr, service_port = service.split("/")[-1].split(":")
    service_host = socket.gethostbyaddr(service_addr)[0]

    return True
    #return my_host + my_port == service_host + service_port



