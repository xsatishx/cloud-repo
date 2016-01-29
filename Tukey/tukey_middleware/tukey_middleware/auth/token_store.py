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

''' Layer that takes keystone auth tokens and values for superglobal store'''

import hashlib
import json

class TokenStore(object):
    ''' Layer that takes keystone auth tokens and values for superglobal
    store'''

    def __init__(self, mc):
        self.memc = mc

    @staticmethod
    def __get_hash(key):
        ''' Get a hash that is less than 250 characters '''
        return str(hashlib.sha512(key).hexdigest())

    def set(self, key, value, expiration=None):
        ''' Set superglobal key-value pair handling keys up to Python string
        limit'''

        hash_key = self.__get_hash(key)

        old_value_string = self.memc.get(hash_key)
        if old_value_string:
            old_values = json.loads(old_value_string)
            old_values[key] = value
        else:
            old_values = {key: value}

        if expiration is None:
            # could be 0
            self.memc.set(hash_key, json.dumps(old_values))
        else:
            self.memc.set(hash_key, json.dumps(old_values))

    def get(self, key):
        ''' Get superglobal key-value pair handling keys up to Python string
        limit'''

        hash_key = self.__get_hash(key)
        old_value_string = self.memc.get(hash_key)

        if not old_value_string:
            return old_value_string

        values = json.loads(old_value_string)
        return values[key]
