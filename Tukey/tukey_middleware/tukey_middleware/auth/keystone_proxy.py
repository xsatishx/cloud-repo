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

from tukey_middleware import utils
from tukey_middleware.auth.token_store import TokenStore
from tukey_middleware.auth.base import (Auth, raise_unauthorized,
        TukeyAuthException)
from keystoneclient.v2_0 import Client as keystone_client

import memcache
import sys


class Ec2rcHandler(object):
    '''handles parsing of the eucarc'''

    def __init__(self, eucarc_path, cloud, username):

        try:
            with open(eucarc_path % (cloud, username)) as eucarc_file:
                self.ec2_creds = self.parse_eucarc(eucarc_file.read())
        except IOError:
            raise TukeyAuthException()

        self.ec2_creds = dict(self.ec2_creds.items() + self.parse_host(
            self.ec2_creds["EC2_URL"]).items())

    def __getitem__(self, attr):
        return self.ec2_creds[attr]

    def parse_eucarc(self, eucarc):
        ''' read standard eucarc text and return a dict of the values '''

        creds = {}
        lines = eucarc.split('\n')
        for line in lines:
            splitLine = line.split(' ')
            if len(splitLine) != 2:
                continue
            keyPair = splitLine[1].split('=')
            creds[keyPair[0]] = keyPair[1].strip("'\"")
        return creds

    def parse_host(self, url):
        """ Parse URL of the type found in eucarc EC2_URL.
        Returns dict with keys 'host','port','path'
        :param url: full URL with port and path for cloud api interface
        """
        # this seems like a job for regexp
        sections = url.split(':')
        host_port_path = {}
        host_port_path['host'] = sections[1][2:]
        host_port_path['port'] = sections[2].split('/')[0]
        host_port_path['path'] = sections[2][len(host_port_path['port']):]
        return host_port_path


class KeystoneProxy(Auth):
    ''' Used to talk to the old tukey-middleware authentication proxy that
    uses memcached to keep track of user credentials '''

    def __init__(self, cloud_name, auth_token, memcache_client, eucarc_path=None):
        ''' eucarc_path should be a format string that allows for the username
        '''

        self.token_store = TokenStore(memcache_client)

        self.eucarc_path = eucarc_path

        self._keystone = None

        super(KeystoneProxy, self).__init__(cloud_name, auth_token)


    def init_auth(self, cloud_name, auth_token):
        ''' The KeystoneProxy uses the dictionary self.values to answer all
        the future auth questions '''

        try:
            values = self.token_store.get(str(auth_token))
            if values == None:
                 self.values = {}
            else:
                if cloud_name in values:
                    # store the distinguished info
                    self._tukey_internal = values["__tukey_internal"]
                    self.values = values[cloud_name]
                else:
                    self.values = {}

        except memcache.Client.MemcachedKeyNoneError:
            self.values = {}

        # ec2 clouds
        if "username" in self.values.keys():
            self._username = self.values["username"]
            self.ec2 = Ec2rcHandler(self.eucarc_path, cloud_name,
                    self._username)

        # openstack clouds
        elif "access" in self.values.keys():
            self._username = self.values["access"]["user"]["username"]


    @raise_unauthorized
    def username(self):
        return self._username

    @raise_unauthorized
    def ec2_access_key(self):
        return self.ec2["EC2_ACCESS_KEY"]

    @raise_unauthorized
    def ec2_secret_key(self):
        return self.ec2["EC2_SECRET_KEY"]

    def get_value(self, key):
        if key in self.values:
            return self.values[key]
        return self.ec2[key]

    @raise_unauthorized
    def host(self):
        return self.get_value("host")

    @raise_unauthorized
    def port(self):
        return self.get_value("port")

    @raise_unauthorized
    def path(self):
        return self.get_value("path")

    @raise_unauthorized
    def auth_token(self):
        return self.values["access"]["token"]["id"]

    @raise_unauthorized
    def tenant_id(self):
        return self.values["access"]["token"]["tenant"]["id"]

    @raise_unauthorized
    def tukey_tenant_id(self):
        return self._tukey_internal["access"]["token"]["tenant"]["id"]

    @property
    def auth_url(self):
        '''Format auth url, Need to support https!'''
        return self.get_endpoint("identity")

    @property
    def keystone(self):
        ''' Keystone client '''
        if self._keystone is None:
            self._keystone = keystone_client(auth_url=self.auth_url,
                    tenant_id=self.tenant_id(), token=self.auth_token())
        return self._keystone

    @raise_unauthorized
    def tenant_name(self):
        ''' Fetch project name from keystone client'''
        return self.keystone.project_name

    def get_endpoint(self, name):
        ''' Return the internal URL of endpoint with name 'name' '''
        for service in self.values["access"]["serviceCatalog"]:
            if service["type"] == name:
                return service["endpoints"][0]["publicURL"]

    @staticmethod
    def handle_parameters(params):

        try:
            ec2path = params["eucarc_path"]
        except KeyError:
            ec2path = None

        mc_class = utils.get_class(params["memcache_client"]["class"])
        mc_params = params["memcache_client"]["params"]
        mc = mc_class(mc_params[0], mc_params[1])


        logger = utils.get_logger()
        logger.debug(mc)
        logger.debug("doing lambda now ")

        return lambda cloud, token : KeystoneProxy(cloud, token, mc, eucarc_path=ec2path)
