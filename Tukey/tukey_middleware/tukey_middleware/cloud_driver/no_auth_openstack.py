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

''' Talk to a single OpenStack without an Authentication driver.  Use the
    OpenStack calls.  This is primarily for running the instance metadata
    on various clouds.'''

from base import CloudDriver

from novaclient.client import Client as nova_client

from tukey_middleware import local_settings

settings = local_settings.vm_ip_auth


class NoAuthOpenStack(CloudDriver):

    def _list(self, manager, search_opts=None):
        if search_opts is not None:
            items = manager.list(search_opts=search_opts)
        else:
            items = manager.list()

        return [{k: v for k, v in vars(i).items() if k != "manager"}
                for i in items]

    def admin_list_instances(self, instance_data=None):
        os_settings = settings[self.cloud]

        client = nova_client('1.1', os_settings["os_admin_user"],
            os_settings["os_admin_pass"], os_settings["os_admin_tenant"],
            auth_url=settings["tukey_keystone_url"] + "/v2.0")

        return self._list(client.servers,
            search_opts={"all_tenants": "True"})

    @property
    def name(self):
        return self.cloud
