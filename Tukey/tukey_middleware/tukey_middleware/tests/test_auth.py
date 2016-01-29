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

''' Authentication layer test cases'''

from tukey_middleware.auth.base import Auth
from tukey_middleware.auth.keystone_proxy import KeystoneProxy
from tukey_middleware.auth.vm_ip_auth import VmIpAuth
import services.mc_mock
import unittest


class AuthTestCase(unittest.TestCase):
    ''' Test cases for auth base class'''

    #def setUp(self):
    def test_init_auth(self):
        auth = Auth("test", "test")


class VmIpAuthTestCase(unittest.TestCase):

    def setUp(self):
        ''' Let's mock up this VmIpAuth thing '''
        self.vm_ip_auth = VmIpAuth(get_cloud, "test_cloud", "127.0.0.1")

        # VmIpAuth uses the local_settings.py file directly.  This may not be
        # the best way to do that but... so we will just override it with our own
        settings = {
            "driver":
                "tukey_middleware.cloud_driver.no_auth_openstack.NoAuthOpenStack",
            "name": "Sullivan",
            "auth_driver_parameters": {

            }
        }

        self.vm_ip_auth.settings = settings


class KeystoneProxyTestCase(unittest.TestCase):

    def setUp(self):

        mc = services.mc_mock.Client(["localhost:11211"], 1)

        mc.set("test_token", {"test_cloud": {"username": "test_user"}}, None)

        self.auth = KeystoneProxy("test_cloud", "test_token", mc,
                eucarc_path="tukey_middleware/tests/data/%s")

    def test_host(self):
        assert self.auth.host() == "127.0.0.3"

    def test_path(self):
        assert self.auth.path() == "/services/Eucalyptus"

if __name__ == "__main__":
    unittest.main()
