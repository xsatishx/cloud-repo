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

''' Flask HTTP API tests.  This may require a name change to not be confused
    with the programming language API'''

from tukey_middleware.api import nova, glance, utils as api_utils
from tukey_middleware.cloud_driver.registry import CloudRegistry
from flask import Flask

import unittest
import json


class ApiTestCase(object):
    ''' Test cases for the OpenStack api like /servers/ /os- whatever '''

    class TestClientWithAuth(object):
        ''' Wrap the flask test client with an auth token header '''

        def __init__(self, test_client):
            self.test_client = test_client
            self.headers = [("x-auth-token", "test_token")]

        def get(self, path):
            #TODO: make kwargsian
            return self.test_client.get(path, headers=self.headers)


    def setUp(self):

        app = Flask('api')
        #self.rest.registry = CloudRegistry()
        #self.rest.logger = utils.get_logger()
        self.rest = api_utils.set_api_manager(self.rest, CloudRegistry())

        app.register_blueprint(self.rest)
        self.app = self.TestClientWithAuth(app.test_client())

    def test_auth(self):
        ''' Try without the auth-token header to see that its 401'''
        self.app.headers = []
        rv = self.app.get(self.test_auth_route)
        assert rv.status_code == 401


class NovaApiTestCase(ApiTestCase, unittest.TestCase):
    ''' Test cases for the nova(compute, keypair) api like /servers/ /os- whatever '''

    def setUp(self):
        self.rest = nova.rest
        self.test_auth_route = '/tenant_id/servers/detail'
        super(NovaApiTestCase, self).setUp()

    def test_list_instances(self):
        ''' insure that list instances HTTP GET always has servers'''
        rv = self.app.get('/tenant_id/servers/detail')
        servers = json.loads(rv.data)
        assert "servers" in servers

    def test_list_keypairs(self):
        ''' insure that list keypairs HTTP GET always has keypairs'''
        rv = self.app.get('/tenant_id/os-keypairs')
        keypairs = json.loads(rv.data)
        assert "keypairs" in keypairs

    def test_list_security_groups(self):
        ''' insure that list security-groups HTTP GET always has security-groups'''
        rv = self.app.get('/tenant_id/os-security-groups')
        security_groups = json.loads(rv.data)
        assert "security_groups" in security_groups

    def test_list_floating_ips(self):
        ''' insure that list floating-ips HTTP GET always has floating-ips'''
        rv = self.app.get('/tenant_id/os-floating-ips')
        floating_ips = json.loads(rv.data)
        assert "floating_ips" in floating_ips

    def test_list_quota_sets(self):
        ''' insure that list quota-sets HTTP GET always has quota-sets
        NOTE: the URL is os-quota-sets but the json has "quota_set":'''
        rv = self.app.get('/tenant_id/os-quota-sets/tenant_id')
        quota_set = json.loads(rv.data)
        assert "quota_set" in quota_set

    def test_list_flavors(self):
        ''' insure that list flavors HTTP GET always has flavors'''
        rv = self.app.get('/tenant_id/flavors/detail')
        print rv.data
        flavors = json.loads(rv.data)
        assert "flavors" in flavors

    def test_list_simple_tenant_usage(self):
        ''' insure that list flavors HTTP GET always has tenant_usages'''
        rv = self.app.get('/tenant_id/os-simple-tenant-usage/tenant_id')
        usages = json.loads(rv.data)
        assert "tenant_usage" in usages


class GlanceApiTestCase(ApiTestCase, unittest.TestCase):
    ''' Test cases for the OpenStack nova api like /servers/ /os- whatever '''

    def setUp(self):
        self.rest = glance.rest
        self.test_auth_route = '/tenant_id/images/detail'
        super(GlanceApiTestCase, self).setUp()


if __name__ == "__main__":
    unittest.main()
