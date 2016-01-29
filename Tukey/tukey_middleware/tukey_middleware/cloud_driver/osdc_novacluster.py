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

''' OSDC Cluster Launch'''

import novacluster.novacluster as nc
import datetime

from threading import Thread
from novaclient import exceptions as nova_exceptions
from tukey_middleware import utils
from tukey_middleware.cloud_driver.base import CloudDriver
from tukey_middleware.cloud_driver.base import uuid_quickfail

class OsdcNovacluster(CloudDriver):
    ''' novacluster cluster launch driver '''

    def __init__(self, cloud):

        self._cloud = cloud

        self.cloud = "cluster%s" % self._cloud.cloud_id
        self.cloud_id = "cluster%s" % self._cloud.cloud_id
        self.cloud_name = "cluster%s" % self._cloud.cloud_id

    @uuid_quickfail
    def delete_instance(self, instance_id):
        ''' Delete cluster that has instance with instance_id as a member'''
        cluster_id = nc.get_cluster_id(self._cloud.client, instance_id)
        return nc.delete_cluster(self._cloud.client, cluster_id)

    def launch_instances(self, name, image, flavor, meta=None, files=None,
            reservation_id=None, min_count=None,
            max_count=None, security_groups=None, userdata=None,
            key_name=None, availability_zone=None,
            block_device_mapping=None, nics=None, scheduler_hints=None,
            config_drive=None, **kwargs):
        ''' Launch a cluster'''

        # TODO: theme handling?

        # name is used to provide extra information to this function via the
        # openstack launch api
        extras = name.split("-")

        headnode_size = extras[0]
        headnode_image = "-".join(extras[1:6])

        # check the quotas

        quotas = self._cloud.list_quotas()
        instances = self._cloud.list_instances()
        flavor_dict = {f["id"]: f for f in self._cloud.list_sizes()}

        # in flavors it's "vcpus" in quotas it's "cores"
        quotas["vcpus"] = quotas["cores"]

        get_old_total = lambda attr: sum(
            [flavor_dict[i["flavor"]["id"]].get(attr, 1) for i in instances])

        get_new_total = lambda attr: (
                min_count * flavor_dict[flavor].get(attr, 1)
                + flavor_dict[headnode_size].get(attr, 1))

        for stat in ["vcpus", "ram", "instances"]:
            if get_old_total(stat) + get_new_total(stat) > quotas[stat]:
                raise nova_exceptions.OverLimit(413, message="Quota exceeded")

        constructor = nc.TORQUECluster

        cluster = constructor(self._cloud.client, min_count,
                self._cloud.client.images.get(headnode_image),
                self._cloud.client.images.get(image), node_flavor=flavor,
                headnode_flavor=int(headnode_size), os_key_name=key_name)

        # There is an issue with using novaclient as the same user from
        # multiple processes because of locks that it creates. This used
        # multiprocessing.Process before but caused a problem on the pdc
        # production server. Using threading.Thread caused the issue to go
        # away. My theory was that the GIL prevent the deadlock from happening
        # Could still be an issue.

        launch_proc = Thread(target=cluster.launch)

        launch_proc.start()

        return {"server": {}}
