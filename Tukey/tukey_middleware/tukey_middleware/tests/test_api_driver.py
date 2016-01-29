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

''' Tests for the ApiManger class.  The api manager class abstracts common tasks
    in interfacing between the OpenStack HTTP APIs and the Tukey/OSDC API
    programming language API'''

from tukey_middleware.api.utils import ApiManager
import unittest


class ApiManagerTestCase(unittest.TestCase):

    class FakeCloud(object):

        def __init__(self):
            self.cloud = "cloud_name"
            self.cloud_name = "Cloud Name"

    class FakeRegistry(object):

        def all_clouds(self, auth_token):
            return [FakeCloud()]


    def setUp(self):
        self.api_manager = ApiManager(FakeRegistry(), None)


    def test_get_item_is_tagging(self):

        item = self.api_manager.get_item("some_name", lambda _ : {"fake": "yep"})
        item_obj = json.loads(item)["some_name"]
        assert item_obj["fake"] == "yep"
        assert item_obj["cloud_id"] == "cloud_name"
        assert item_obj["cloud_name"] == "Cloud Name"
        assert item_obj["cloud"] == "Cloud Name"


