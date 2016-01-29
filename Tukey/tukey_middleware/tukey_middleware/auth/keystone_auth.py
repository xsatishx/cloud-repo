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

import json
import sqlalchemy
import requests

from functools import wraps
from tukey_middleware import local_settings

from admin_auth import AdminAuth
from base import raise_unauthorized



class KeystoneAuth(AdminAuth):
    """ find out who the user is from the VM IP then
    return info about the user."""

    def __init__(self, cloud_name, user_token, user, tenant):
        self.cloud_name = cloud_name
        self.settings = local_settings.vm_ip_auth
        access = self._keystone_attr("token", user_token)["access"]
        if user == access["user"]["name"] and tenant == access["token"][
                "tenant"]["name"]:

            self._username = user
            self._tenant_name = tenant
            self._tenant_id = access["token"]["tenant"]["id"]
            self._user_id = access["user"]["id"]


    @raise_unauthorized
    def user_id(self):
        return self._user_id

    @raise_unauthorized
    def username(self):
        return self._username

    @raise_unauthorized
    def tenant_id(self):
        return self._tenant_id

    @raise_unauthorized
    def tenant_name(self):
        return self._tenant_name
