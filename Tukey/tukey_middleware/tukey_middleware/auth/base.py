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

''' Authentication interface class '''

import traceback

from tukey_middleware import utils
from functools import wraps

class Auth(object):

    def __init__(self, cloud_name, auth_token):

        self.logger = utils.get_logger()

        self.logger.debug("cloud_name %s", cloud_name)
        self.logger.debug("auth_token %s", auth_token)

        self.init_auth(cloud_name, auth_token)

    def init_auth(self, cloud_name, auth_token):

        self.logger.info("Driver did not implement init_auth")


    def auth_token(self):
        ''' Return the auth_token for this cloud and user if the cloud has
        auth_tokens '''
        self.logger.info("Driver did not implement auth_token")
        return None

    def tenant_id(self):
        ''' Returns the tenant id for the cloud and user determined by the
        auth token and cloud name '''
        self.logger.info("Driver did not implement tenant_id")
        return None

    @staticmethod
    def handle_parameters(param_dict):
        return Auth


class TukeyAuthException(Exception):
    ''' Throw this exception when we have an unauthorized request '''
    def __init__(self, message=None):
        Exception.__init__(self, message)

def raise_unauthorized(fn):
    ''' decorator for wrapping AttributeError exception and returning
    TukeyAuthException '''
    @wraps(fn)
    def decorated(*args, **kwds):
        try:
            return fn(*args, **kwds)
        except (AttributeError, KeyError) as exc:
            logger = utils.get_logger()
            logger.warn("Raising TukeyAuthException from %s", exc.message)
            logger.warn(" %s", traceback.format_exc())
            raise TukeyAuthException()
    return decorated
