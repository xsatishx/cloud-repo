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

from tukey_middleware.cloud_driver.base import uuid_quickfail
from cinderclient.v1.client import Client as cinder_client

from tukey_middleware.cloud_driver.openstack import OpenStackDriver


class OpenStackVolumeDriver(OpenStackDriver):

    def __init__(self, auth_driver=None, client_format=None):

        super(OpenStackVolumeDriver, self).__init__(auth_driver)

        fixed_cinder_client = self.fix_token_class("fixed_cinder_client",
                cinder_client, self.auth.get_endpoint("volume"))

        api_key = ""

        self.cinder_client = fixed_cinder_client(self.auth.username(),
                api_key, project_id=self.auth.tenant_id(),
                auth_url=self.auth.auth_url)


    def list_volumes(self):
        volumes = []
        for i in self.cinder_client.volumes.list():
            volumes.append({k: v for k, v in vars(i).items() if k != "manager"})
        return volumes

    @uuid_quickfail
    def get_volume(self, volume_id):
        volume = {k: v for k, v in vars(self.cinder_client.volumes.get(
                volume_id)).items() if k != "manager"}
        return volume

    def detach_volume(self, instance_id, volume_id):
        return self.cinder_client.volumes.detach(volume_id)

    def attach_volume(self, instance_id, volume_id, mount_point):
        return self.cinder_client.volumes.attach(volume_id, instance_id,
            mount_point)

    def list_volume_types(self):
        return self.cinder_client.volume_types.list()

    def list_volume_snapshots(self):
        return self.cinder_client.volume_snapshots.list()

    def get_volume_quotas(self, tenant_id):
        return self._get(self.cinder_client.quotas, self.auth.tenant_id())

    def create_volume(self, size, **kwargs):
        return self.cinder_client.volumes.create(size, **kwargs)

    def delete_volume(self, volume_id):
        return self.cinder_client.volumes.delete(volume_id)
