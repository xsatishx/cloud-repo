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
import requests

class AdminAuth(object):


    def _get_auth_token(self, base_url, username, password, tenant_name=None):
        ''' Most of the time we just want the token not the expiration also '''
        token_info = self._get_token_info(base_url, username, password,
                tenant_name)
        return token_info["id"]

    def _get_token_info(self, base_url, username, password, tenant_name=None):
        """
        Currently the proxied auth endpoints are not playing well with the
        tukey and keystone client libraries so doing a raw http request to get
        an auth token.
        """

        url = "%s/v2.0/tokens" % base_url
        auth_data = {"auth": {"passwordCredentials": {"username": username,
                "password": password}}}

        if tenant_name is not None:
            auth_data["auth"]["tenantName"] = tenant_name

        result = requests.post(url,
                data=json.dumps(auth_data),
                headers={"content-type": "application/json"})
        token_data = json.loads(result.text)
        return token_data["access"]["token"]

    def _keystone_attr(self, attr, object_id):
        """
        As admin user look up the user id and return the string of that user_id's
        username
        """
        cloud_settings = self.settings[self.cloud_name]
        keystone_admin_url = cloud_settings["keystone_admin_url"]
        auth_token = self._get_auth_token(keystone_admin_url,
                cloud_settings["os_admin_user"],
                cloud_settings["os_admin_pass"],
                tenant_name=cloud_settings["os_admin_tenant"])

        url = "%s/v2.0/%ss/%s" % (keystone_admin_url, attr, object_id)
        result = requests.get(url, headers={"x-auth-token": auth_token})
        user_data = json.loads(result.text)
        return user_data

