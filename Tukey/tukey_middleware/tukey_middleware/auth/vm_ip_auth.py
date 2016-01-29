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

from .admin_auth import AdminAuth
from .base import raise_unauthorized
from tukey_middleware import local_settings
from tukey_middleware.utils import cache_attr


class VmIpAuth(AdminAuth):
    """ find out who the user is from the VM IP then
    return info about the user."""

    def __init__(self, get_cloud_func, cloud_name, ip):

        self.cloud_name = cloud_name
        self.ip = ip
        self.get_cloud_func = get_cloud_func
        self.settings = local_settings.vm_ip_auth

    def _init_auth(self):
        """
        Initialize the tukey-middleware auth proxy so that when we look at
        memcached as the admin user all the values we need to look up the instances
        will be there.  Returns an auth token for "tukey_admin_user".
        """
        keystone_admin_url = self.settings["tukey_keystone_url"]
        auth_token = self._get_auth_token(keystone_admin_url,
                self.settings["tukey_admin_user"],
                self.settings["tukey_admin_pass"])

        # we need this
        result = requests.get("%s/v2.0/tenants" % keystone_admin_url,
            headers={"x-auth-token": auth_token})

        tenant_data = json.loads(result.text)

        for tenant in tenant_data["tenants"]:
            if tenant["enabled"]:
                tenant_id = tenant["id"]

        url = "%s/v2.0/tokens" % keystone_admin_url
        requests.post(url, data=json.dumps(
                {"auth": {"token": {"id": auth_token}, "tenantId": tenant_id}}),
                headers={"x-auth-token": auth_token,
                        "content-type": "application/json"})
        return auth_token

    def _get_user_id_tenant_id(self, get_cloud_func, ip):
        """
        Look up the IP this request came from in cloud_name's list of VMs.  Then
        returns the password of that VMs owner.
        """

        auth_token = self._init_auth()

        cloud = get_cloud_func(self.cloud_name, auth_token)

        for i in cloud.admin_list_instances():
            try:
                for net in i["addresses"]:
                    if str(ip) == str(i["addresses"][net][0]["addr"]):
                        user_id = i["user_id"]
                        tenant_id = i["tenant_id"]
                        return user_id, tenant_id
            except KeyError:
                continue
        else:
            error = json.dumps(
                    {"error": "reqeust not from a vm running on %s" %
                            cloud.name})
            return error, error

        return user_id, tenant_id

    def _run_query(self, query_string):
        '''Formats self.cloud_name, self.username() into query_string then
        returns the rows of the query '''

        cloud_name = self.cloud_name
        username = self.username()
        query = query_string % {"cloud_name":cloud_name, "username": username}

        engine = sqlalchemy.create_engine(self.settings["auth_db_str"])
        with engine.begin() as connection:
            result = connection.execute(query)
        return result

    def _username_to_password(self):
        '''Query the password from the Tukey authentication database.  This
        password is the users OpenStack password which is the same as their
        cifs password.'''

        result = self._run_query("""select password from
        login join login_enabled on login.id = login_enabled.login_id
        join cloud on cloud.cloud_id = login.cloud_id
        where cloud_name='%(cloud_name)s' and username='%(username)s';""")

        for row in result:
            return row[0]

    def _username_to_identifiers(self):
        '''Find OpenID and Shibboleth identifiers based on username'''

        result = self._run_query("""select identifier, method_name from
        login join login_enabled on login.id = login_enabled.login_id
        join cloud on cloud.cloud_id = login.cloud_id
        join login_identifier on login_identifier.userid = login.userid
        join login_method on
            login_method.method_id = login_identifier.method_id
        where cloud_name='%(cloud_name)s' and username='%(username)s';""")

        identifiers = []
        for row in result:
            identifiers.append({"identifier": row[0], "method": row[1]})
        return identifiers

    @cache_attr
    def _user_tenant(self):
        return self._get_user_id_tenant_id(self.get_cloud_func, self.ip)

    @cache_attr
    def user_id(self):
        return self._user_tenant()[0]

    @cache_attr
    def tenant_id(self):
        return self._user_tenant()[1]

    @cache_attr
    def password(self):
        return self._username_to_password()

    @cache_attr
    @raise_unauthorized
    def username(self):
        return self._keystone_attr("user", self.user_id())["user"]["name"]

    @cache_attr
    @raise_unauthorized
    def tenant_name(self):
        return self._keystone_attr("tenant", self.tenant_id())["tenant"]["name"]

    @cache_attr
    def identifiers(self):
        return self._username_to_identifiers()

