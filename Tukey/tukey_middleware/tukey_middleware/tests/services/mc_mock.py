#  Copyright 2013 Open Cloud Consortium
# #   Licensed under the Apache License, Version 2.0 (the "License");
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

''' This is a fake memcache for testing purposes '''
import memcache

class Client(object):
    ''' This mock only implements the subset of the python-memcache interface
    that the tukey middleware code interacts with '''

    def __init__(self, memcache_servers, debug=0):
        ''' Initialize a dictionary to keep track mimic mc behavior'''
        self.store = {}


    def get(self, key):
        ''' Lookup key in the dictionary and return the value '''
        if key not in self.store:
            raise memcache.Client.MemcachedKeyNoneError
        return self.store[key]

    def set(self, key, value, expiration):
        ''' Set key in store to value for now ingore the expiration '''

        self.store[key] = value


class ClientPreload(Client):
    ''' For registry settings so we can have preloaded data '''

    def __init__(self, memcache_servers, debug=0):

        super(ClientPreload, self).__init__(memcache_servers, debug)

        self.set("test_token", {"test_cloud": {"username": "test_user"},
            "test_openstack": {'tokenId': 'test_token', 'tenantId': u'test_user',
            u'access': {u'token':
                {u'expires': u'2013-07-11T16:28:46Z', u'id': u'test_token'},
                u'serviceCatalog': {}, u'user':
                    {u'username': u'test_user', u'roles_links': [],
                    u'id': u'test_user', u'roles': [], u'name': u'test_user'}},
                    'host': '127.0.0.2', 'path': '', 'port': '8774'}
            }, None)
