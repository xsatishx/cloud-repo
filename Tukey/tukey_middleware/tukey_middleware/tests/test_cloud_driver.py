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

''' Test cases for the programming language API'''

from tukey_middleware.cloud_driver.base import CloudDriver
from tukey_middleware.cloud_driver.euca import EucaDriver
from tukey_middleware.cloud_driver.osdc_euca import OsdcEucaDriver, OsdcUsage
from tukey_middleware.cloud_driver.registry import CloudRegistry
from tukey_middleware.cloud_driver.openstack import OpenStackDriver

from tukey_middleware.auth.base import Auth
from tukey_middleware.auth.keystone_proxy import KeystoneProxy

import unittest
import subprocess

from datetime import datetime

import services.euca_mock
import services.mc_mock
import services.db_mock


class CloudDriverTestCase(unittest.TestCase):
    ''' Test cases for the cloud driver '''

    def setUp(self):
        self.cloud = CloudDriver(Auth("test", "test"))


    def empty_list(self, some_list):
        ''' for the generic driver listing should give an empty list
        to simplify aggregation'''
        assert len(some_list) == 0

    def test_list_instances(self):
        self.empty_list(self.cloud.list_instances())

    def test_list_keypairs(self):
        self.empty_list(self.cloud.list_keypairs())

    def test_list_sizes(self):
        self.empty_list(self.cloud.list_sizes())

    def test_list_security_groups(self):
        self.empty_list(self.cloud.list_security_groups())

    def test_list_floating_ips(self):
        self.empty_list(self.cloud.list_floating_ips())

    def test_list_quotas(self):
        self.empty_list(self.cloud.list_quotas())

    def test_list_usage(self):
        start = datetime.now() #"2013-07-01T00:00:00"
        end = datetime.now()#"2013-07-15T17:24:45.266255"
        self.empty_list(self.cloud.list_usage(start, end))


class AbstractDriverTestCase(object):
    '''Mixin for common tests that apply to all drivers '''

    def test_instances(self):
        instances = self.cloud.list_instances()
        assert len(instances) > 0
        for i in instances:
            assert "image" in i
            assert "id" in i

    def test_keypairs(self):
        keypairs = self.cloud.list_keypairs()
        assert len(keypairs) > 0
        for k in keypairs:
            assert "name" in k
            assert "fingerprint" in k

    def test_security_groups(self):
        sec_groups = self.cloud.list_security_groups()

    def test_floating_ips(self):
        ips = self.cloud.list_floating_ips()

    def test_quotas(self):
        quotas = self.cloud.list_quotas()

    def test_usages(self):
        start = datetime.now()#"2013-07-01T00:00:00"
        end = datetime.now()#"2013-07-15T17:24:45.266255"
        usages = self.cloud.list_usage(start, end)

    def test_sizes(self):
        sizes = self.cloud.list_sizes()
        assert len(sizes) > 0
        for k in sizes:
            assert "vcpus" in k
            assert "name" in k

    def test_images(self):
        images = self.cloud.list_images()

class EucaDriverTestCase(unittest.TestCase):
    ''' The Eucalyptus Driver '''

    def setUp(self):
        # fire up fake euca
        # and then kill it when we are done

        mc = services.mc_mock.Client(["localhost:11211"], 1)
        mc.set("test_token", {"test_cloud": {"username": "test_user"}}, None)

        auth = KeystoneProxy("test_cloud", "test_token", mc,
            eucarc_path="tukey_middleware/tests/data/%s")

        self.cloud = EucaDriver(auth)

    def test_euca_instances(self):
        instances = self.cloud.list_instances()
        inst_dict = instances[0]
        assert inst_dict["image"]["id"] == "00938d13-6d00-0000-0000-000000000000"


class OsdcEucaTestCase(unittest.TestCase, AbstractDriverTestCase):
    ''' Osdc Specific additions to the euca driver '''

    def setUp(self):
        # fire up fake euca
        # and then kill it when we are done

        mc = services.mc_mock.Client(["localhost:11211"], 1)
        mc.set("test_token", {"test_cloud": {"username": "test_user"}}, None)

        auth = KeystoneProxy("test_cloud", "test_token", mc,
            eucarc_path="tukey_middleware/tests/data/%s")

        usage_resources = {
            'cloud': {
                'adler': 'OSDC-Adler',
                'sullivan': 'OSDC-Sullivan',
                'atwood': 'atwood'
            },
            'hadoop': {
                'occ_y': 'OCC-Y',
                'occ_lvoc_hadoop': 'OCC-LVOC-HADOOP'
            }
        }

        usage = OsdcUsage(services.db_mock.DbConnMock(), usage_resources)

        self.cloud = OsdcEucaDriver(auth_driver=auth, usage=usage,
            quota_host='127.2')



class OpenStackDriverTestCase(unittest.TestCase, AbstractDriverTestCase):
    ''' The OpenStack Driver '''

    def setUp(self):
        # fire up fake euca
        # and then kill it when we are done
        subprocess.call("python tukey_middleware/tests/services/openstack_mock.py 2> /dev/null &",
                shell=True)


        mc = services.mc_mock.Client(["localhost:11211"], 1)
        mc.set("test_token", {"test_cloud":
            {'tokenId': 'test_token',
            'tenantId': u'test_user',
            u'access': {u'token':
                {u'expires': u'2013-07-11T16:28:46Z', u'id': u'test_token'},
                u'serviceCatalog': {}, u'user':
                    {u'username': u'test_user', u'roles_links': [],
                    u'id': u'test_user', u'roles': [], u'name': u'test_user'}},
                    'host': '127.0.0.2', 'path': '', 'port': '8774'}}, None)

        auth = KeystoneProxy("test_cloud", "test_token", mc)

        self.cloud = OpenStackDriver(auth)



class CloudRegistryTestCase(unittest.TestCase):

    def setUp(self):

        settings = {
            "test_cloud": {
                "driver": "tukey_middleware.cloud_driver.euca.EucaDriver",
                "auth_driver": "tukey_middleware.auth.keystone_proxy.KeystoneProxy",
                "name": "Adler",
                "auth_driver_parameters": {
                    "memcache_client":  {
                        "class": "tukey_middleware.tests.services.mc_mock.ClientPreload",
                        "params": [["localhost:11211"], 1]
                    },
                    "eucarc_path":  "tukey_middleware/tests/data/%s"
                }
            },
            "test_openstack": {
                "driver": "tukey_middleware.cloud_driver.openstack.OpenStackDriver",
                "auth_driver": "tukey_middleware.auth.keystone_proxy.KeystoneProxy",
                "name": "Sullivan",
                "auth_driver_parameters": {
                    "memcache_client":  {
                        "class": "tukey_middleware.tests.services.mc_mock.ClientPreload",
                        "params": [["localhost:11211"], 1]
                    }
                }

            }
        }

        self.registry = CloudRegistry(settings=settings)


    def test_registry(self):
        clouds = self.registry.all_clouds("test_token")
        instances = []
        for cloud in clouds:
            instances += cloud.list_instances()
        instances


if __name__ == "__main__":
    unittest.main()
