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


class Instance(object):

    def __init__(self, id=None, name=None, address=None, size=None,
        image_id=None, key_name=None, status=None, created_at=None,
        user_id=None, tenant_id=None, updated_at=None, progress=None):

        for key, value in locals().items():
            self.__setattr__(key, value)

        if self.name is None:
            self.name = self.id

        if self.tenant_id is None:
            self.tenant_id = self.user_id

        if self.updated_at is None:
            self.updated_at = self.created_at

        self.defaults = {
            "OS-EXT-STS power_state": 1,
            "progress": 100, "accessIPv4": "",
            "accessIPv6": "",
            "image": {"id": self.image_id},
            "flavor": {"id": self.size},
            "addresses": {"private": [{"addr": self.address, "version": 4}]}
        }

    def __getitem__(self, key):

        attr = getattr(self, key, None)

        if attr is None and key in self.defaults:
            attr = self.defaults[key]

        if attr is None:
            attr = ''

        return attr

    def as_dict(self):
        return {key: self.__getitem__(key) for key in
            self.__dict__.keys() + self.defaults.keys()
            if key not in ["self", "defaults"]}
