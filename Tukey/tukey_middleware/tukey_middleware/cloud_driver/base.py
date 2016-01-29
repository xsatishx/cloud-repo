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

''' The CloudDriver interface is the generic cloud interface for actions like
launching instances listing instances and keypairs etc.'''

from novaclient import exceptions as nova_exceptions
from functools import wraps


def uuid_quickfail(fn):
    '''When given a nonrandom uuid generated for nonOpenStack resources don't
    contact this OpenStack API just return the 404 exception'''

    @wraps(fn)
    def decorated(*args, **kwds):
        '''Check non self argument for fake uuid'''
        if args[1].endswith("0000-0000-000000000000"):
            raise nova_exceptions.NotFound(404)
        return fn(*args, **kwds)
    return decorated


class CloudDriver(object):
    ''' the cloud ...
    all of the listing methods of this base class (list_instances list_images)
    will return empty lists and all of the action methods will return errors'''

    def __init__(self, auth_driver=None):
        ''' Constructor injection of the auth_driver which is initilized before
        being passed in '''

        self.cloud_id = "none"
        self.cloud_name = "Not Set"
        self.auth = auth_driver

    def list_instances(self):
        ''' This is the generic CloudDriver so it returns no instances'''
        return []

    def list_keypairs(self):
        return []

    def list_sizes(self):
        return []

    def list_security_groups(self):
        return []

    def list_floating_ips(self):
        return []

    def list_quotas(self):
        return []

    def list_usage(self, start, stop):
        return []

    def list_images(self):
        return []

    def list_volumes(self):
        return []

    def list_volume_types(self):
        return []

    def list_volume_snapshots(self):
        return []

    def get_instance_security_groups(self, instance_id):
        return []

    def get_size(self, size_id):
        raise nova_exceptions.NotFound(404)

    def get_image(self, image_id):
        raise nova_exceptions.NotFound(404)

    def get_instance(self, instance_id):
        raise nova_exceptions.NotFound(404)

    def get_volume(self, image_id):
        raise nova_exceptions.NotFound(404)

    def import_keypair(self, keypair_name, public_key):
        raise nova_exceptions.NotFound(404)
