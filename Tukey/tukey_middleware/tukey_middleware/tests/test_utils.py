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

''' These are not testutils but tests of the utils '''

from tukey_middleware import utils

import unittest
import tempfile
import os


class UtilsTestCase(unittest.TestCase):

    def test_logger(self):
        log_file, name = tempfile.mkstemp()
        logger = utils.get_logger(log_file_name=name)
        logger.info("test")
        log_contents = os.read(log_file, 100)
        assert log_contents == "test\n"

    def test_get_class(self):
        test = utils.get_class(
            "tukey_middleware.auth.keystone_proxy.KeystoneProxy")
        auth = test.handle_parameters({
                    "memcache_client":  {
                        "class": "tukey_middleware.tests.services.mc_mock.ClientPreload",
                        "params": [["localhost:11211"], 1]
                    },
                    "eucarc_path":  "tukey_middleware/tests/data/%s"
                })
        inst = auth("test_cloud", "test_token")

        test2 = utils.get_class("tukey_middleware.cloud_driver.euca.EucaDriver")
        test2(inst)


if __name__ == "__main__":
    unittest.main()

