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

''' OpenStack cloud '''

from tukey_middleware.cloud_driver.base import CloudDriver, uuid_quickfail
from glanceclient.client import Client as glance_client
from novaclient import exceptions as nova_exceptions
from novaclient.v1_1.client import Client as nova_client
from glanceclient.exc import HTTPException




class OpenStackDriver(CloudDriver):

    def fix_token_class(self, class_name, base_class, management_url):

        #TODO: When you set up a novaclient like this using an auth token
        # instead of a username or password the auth token is not present in
        # the manger classes. So I inject the auth token... obviously this is
        # bad.

        def __getattribute__(inner_self, name):

            try:
                manager = super(base_class, inner_self).__getattribute__(
                        name)
                manager.api.client.auth_token = self.auth.auth_token()
                manager.api.client.projectid = self.auth.tenant_name()
                manager.api.client.management_url = management_url
            except AttributeError:
                pass

            return super(base_class, inner_self).__getattribute__(name)

        return type(class_name, (base_class,),
                {"__getattribute__": __getattribute__})


    def __init__(self, auth_driver=None, client_format=None):
        ''' Relying on contructor injection '''

        super(OpenStackDriver, self).__init__(auth_driver)

        self.client_format = client_format

        auth_url = self.auth.auth_url

        fixed_nova_client = self.fix_token_class("fixed_nova_client",
                nova_client, "")

        api_key = ""
        self.client = fixed_nova_client(self.auth.username(), api_key,
                self.auth.tenant_id(), auth_url=auth_url)

        endpoint = self.auth.get_endpoint("image")
        #TODO: this just doesn't seem right? the question is do we define the
        # endpoints in keystone to not have the /v1 or am i calling glanceclient
        # wrong?  hopefully and probably the latter.
        if endpoint.endswith("/v1"):
            endpoint = endpoint[:-3]
        self.glance_client = glance_client('1',
                endpoint,
                token=self.auth.auth_token())


    def _list(self, manager, search_opts=None):
        if search_opts is not None:
            items = manager.list(search_opts=search_opts)
        else:
            items = manager.list()

        return [{k: v for k, v in vars(i).items() if k not in
                ["_info", "manager"]} for i in items]

    def _get(self, manager, item_id):
        return {k: v for k, v in vars(manager.get(item_id)).items()
                if k != "manager"}

    def _delete(self, manager, item_id):
        return manager.delete(item_id)

    def admin_list_instances(self, instance_data=None):
        return self._list(self.client.servers,
            search_opts={"all_tenants": "True"})

    def list_instances(self, instance_data=None):
        return self._list(self.client.servers)

    def list_keypairs(self):
        return self._list(self.client.keypairs)

    def list_sizes(self):
        return self._list(self.client.flavors)

    def list_security_groups(self):
        return self._list(self.client.security_groups)

    def list_floating_ips(self):
        return self._list(self.client.floating_ips)

    def list_usage(self, start, end):
        return [{k: v for k, v in vars(i).items() if k != "manager"}
                for i in self.client.usage.list(start, end)]

    def list_quotas(self):
        return {k: v for k, v in vars(self.client.quotas.get(
                self.auth.tenant_id())).items()
                if k not in ["manager", "_info", "_loaded"]}

    def list_images(self):
        if False:  # self.client_format != "python-glanceclient":
            return self._list(self.client.images)
        images = []
        for i in self.glance_client.images.list():
            images.append({k: v for k, v in vars(i).items() if k != "manager"})
            if images[-1]["owner"] == self.auth.tenant_id():
                images[-1]["owner"] = self.auth.tukey_tenant_id()
        return images

    @uuid_quickfail
    def get_image(self, image_id):
        if False:  # self.client_format != "python-glanceclient":
            return self._get(self.client.images, image_id)
        try:
            image = {k: v for k, v in vars(self.glance_client.images.get(
                    image_id)).items() if k != "manager"}
            return image
        except HTTPException:
            return

    def get_size(self, flavor_id):
        ''' OpenStack flavor ids are integers.  If the value is not an integer
        we know it is for euca or aws so we can fail fast'''
        try:
            int(flavor_id)
        except Exception:
            raise nova_exceptions.NotFound(404)
        return self._get(self.client.flavors, flavor_id)

    @uuid_quickfail
    def get_instance(self, instance_id):
        return self._get(self.client.servers, instance_id)

    @uuid_quickfail
    def create_image(self, instance_id, image_name, metadata=None):
        return self.client.servers.create_image(instance_id, image_name,
                metadata=metadata)

    @uuid_quickfail
    def get_log(self, instance_id, length):
        return self.client.servers.get(instance_id).get_console_output(
                length=length)

    @uuid_quickfail
    def get_instance_security_groups(self, instance_id):
        manager = self.client.servers
        sec_groups = manager.get(instance_id).list_security_group()
        sec_groups = [{k: v for k, v in vars(i).items() if k not in
                ["_info", "manager"]} for i in sec_groups]
        return sec_groups

    def import_keypair(self, keypair_name, public_key):
        manager = self.client.keypairs
        return {k: v for k, v in vars(manager.create(keypair_name,
                public_key=public_key)).items() if k != "manager"}

    def create_keypair(self, keypair_name):
        return self.import_keypair(keypair_name, public_key=None)

    def delete_keypair(self, keypair_name):
        return self._delete(self.client.keypairs, keypair_name)

    def pause_instance(self, instance_id):
        return self.client.servers.pause(instance_id)

    def unpause_instance(self, instance_id):
        return self.client.servers.unpause(instance_id)

    def suspend_instance(self, instance_id):
        return self.client.servers.suspend(instance_id)

    def unsuspend_instance(self, instance_id):
        return self.client.servers.unsuspend(instance_id)

    def reboot_instance(self, instance_id, reboot_type):
        return self.client.servers.reboot(instance_id, reboot_type=reboot_type)

    def update_instance(self, instance_id, name=None):
        return self.client.servers.update(instance_id, name=name)

    def delete_instance(self, instance_id):
        return self._delete(self.client.servers, instance_id)

    def delete_image(self, image_id):
        return self._delete(self.client.images, image_id)

    def set_image_metadata(self, image_id, **meta):
        # TODO: duplicated code from get_image
        meta["purge_props"] = False
        return {k: v for k, v in vars(self.glance_client.images.update(
                image_id, **meta)).items() if k != "manager"}

    def launch_instances(self, name, image, flavor, meta=None, files=None,
            reservation_id=None, min_count=None,
            max_count=None, security_groups=None, userdata=None,
            key_name=None, availability_zone=None,
            block_device_mapping=None, nics=None, scheduler_hints=None,
            config_drive=None, **kwargs):

        security_groups = [sg["name"] for sg in security_groups]

        #TODO: handle sec groups correctly
        boot_args = [name, image, flavor]
        boot_kwargs = dict(
            meta=meta, files=files, userdata=userdata,
            reservation_id=reservation_id, min_count=min_count,
            max_count=max_count, security_groups=security_groups,
            key_name=key_name, availability_zone=availability_zone,
            scheduler_hints=scheduler_hints, config_drive=config_drive,
            **kwargs)

        return {k: v for k, v in vars(self.client.servers.create(*boot_args,
                **boot_kwargs)).items() if k != "manager"}
