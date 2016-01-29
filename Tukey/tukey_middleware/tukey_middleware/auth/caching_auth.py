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
''' Create auth tokens to prevent talking to keystone repeatedly '''

import memcache
import requests
import uuid

from .vm_ip_auth import VmIpAuth
from .base import raise_unauthorized, TukeyAuthException


class CachingAuth(object):
    ''' Use caching to speed up client auth. '''

    def __init__(self, token=None, auth=VmIpAuth,
            memcache_server='127.1:11211'):

        self._auth = auth

        if token is not None:
            self.id_auth_token = str(token)
        else:
            self.id_auth_token = None

        self._cached_info = None
        self.memcache_client = memcache.Client([memcache_server])

    def _get_from_class_cache(self, attr, super_func):
        if self._cached_info and attr in self._cached_info:
            return self._cached_info[attr]
        else:
            try:
                self._cached_info[attr] = super_func()
                self.memcache_client.set(self.id_auth_token, self._cached_info)
                return self._cached_info[attr]
            except TypeError:
                raise TukeyAuthException("Not a valid ID service auth token")

    def _get_from_external_cache(self, attr, super_func):
        if self._cached_info:
            return self._get_from_class_cache(attr, super_func)
        elif self.id_auth_token:
            try:
                self._cached_info = self.memcache_client.get(self.id_auth_token)
                return self._get_from_class_cache(attr, super_func)
            except memcache.Client.MemcachedKeyNoneError:
                raise TukeyAuthException()
        while True:
            try:
                self.id_auth_token = str(uuid.uuid4())
                if not self.memcache_client.get(self.id_auth_token):
                    break
            except memcache.Client.MemcachedKeyNoneError:
                break
        self._cached_info = {}
        self.memcache_client.set(self.id_auth_token, self._cached_info)
        return self._get_from_class_cache(attr, super_func)

    # I have go to be able to do this programmatically

    @raise_unauthorized
    def user_id(self):
        return self._get_from_external_cache("user_id", self._auth.user_id)

    @raise_unauthorized
    def tenant_id(self):
        return self._get_from_external_cache("tenant_id", self._auth.tenant_id)

    @raise_unauthorized
    def password(self):
        return self._get_from_external_cache("password", self._auth.password)

    @raise_unauthorized
    def username(self):
        return self._get_from_external_cache("username", self._auth.username)

    @raise_unauthorized
    def tenant_name(self):
        return self._get_from_external_cache("tenant_name",
                self._auth.tenant_name)

    @raise_unauthorized
    def identifiers(self):
        return self._get_from_external_cache("identifiers",
                self._auth.identifiers)

