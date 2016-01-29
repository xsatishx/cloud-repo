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

''' OSDC extensions to Eucalyptus cloud driver'''

import json
import time
import requests
import memcache
import os

from .. import utils
from euca import EucaDriver

#TODO: need to use sqlalchemy
#TODO: apparently it is bad to release resources with __del__

def time_to_unix(time_str):
    ''' Take string in OpenStack time format and get integer'''
    if '.' in time_str:
        format_str = '%Y-%m-%dT%H:%M:%S.%f'
    else:
        format_str = '%Y-%m-%dT%H:%M:%S'

    os.environ['TZ'] = 'UTC'
    return int(time.mktime(time.strptime(time_str, format_str)))


class OsdcUsage(object):

    USAGE_ATTRIBUTES = {
        'hadoop': ['jobs', 'hdfsdu'],
        'cloud': ['du', 'cores', 'ram']
    }

    USAGE_HOURS = ['jobs', 'cores', 'ram']

    def __init__(self, db_connection, resources):

        self.db_connection = db_connection
        self.resources = resources

        self.logger = utils.get_logger()

    def __del__(self):
        self.db_connection.close()

    def get_usage_batch(self, start, stop, username):
        ''' Get all of the users usage attributes at once using a single
        powerful query.  One query to rule them all'''

        return ''.join(["""select res, fea, sum(val), count(val)
            from log where ts < %(stop)s and ts > %(start)s
            and fea like '%(username)s-""" % locals(), "%' group by res, fea;"])

    def get_usages(self, resources, attributes):

        return [(res, attr, name) for attr in attributes for name, res in
                resources.items()]

    def list_usages(self, start, stop, tenant_id):

        db_cursor = self.db_connection.cursor()
        _start_unix = time_to_unix(start)
        _stop_unix = time_to_unix(stop)

        attributes = OsdcUsage.USAGE_ATTRIBUTES

        for resource_type in self.resources.keys():
            usages = self.get_usages(self.resources[resource_type],
                attributes[resource_type])

        self.logger.debug(usages)

        results = {}

        mc = memcache.Client(["127.0.0.1:11211"], debug=0)

        try:
            stored_usage = mc.get("usage-%s" % tenant_id)
            cached = stored_usage is not None
        except memcache.Client.MemcachedKeyNoneError:
            cached = False

        if cached and stored_usage["start"] == _start_unix:
            query = self.get_usage_batch(stored_usage["stop"],
                    _stop_unix, tenant_id)
            db_cursor.execute(query)
            batch_results = db_cursor.fetchall()
        else:
            cached = False
            db_cursor.execute(self.get_usage_batch(_start_unix, _stop_unix,
                    tenant_id))
            batch_results = db_cursor.fetchall()

        formatted = {}
        for result in batch_results:
            attr = result[1].split('-')[1]

            if result[0] not in formatted:
                formatted[result[0]] = {}

            if attr in self.USAGE_HOURS:
                formatted[result[0]][attr] = result[2] / 60
            else:
                formatted[result[0]][attr] = result[2] / result[3]
                formatted[result[0]]["%s-count" % attr] = result[3]
                formatted[result[0]]["%s-raw" % attr] = result[2]

        if cached:
            old = stored_usage["results"]
            for cloud, _ in formatted.items():
                if cloud in old:
                    for key, _ in formatted[cloud].items():
                        if key not in old[cloud] or key.split('-')[-1] in [
                                'count', 'raw']:
                            continue

                        if key in self.USAGE_HOURS:
                            formatted[cloud][key] += old[cloud][key]
                        else:
                            formatted[cloud]["%s-count" % key] += old[cloud][
                                    "%s-count" % key]
                            formatted[cloud]["%s-raw" % key] += old[cloud][
                                    "%s-raw" % key]
                            formatted[cloud][key] = formatted[cloud][
                                    "%s-raw" % key] / formatted[cloud][
                                    "%s-count" % key]
                    old[cloud].update(formatted[cloud])

            old.update(formatted)
            formatted = old

        usage_to_cache = {"start": _start_unix, "stop": _stop_unix,
                    "results": formatted}

        if cached and len(batch_results) == 0:
            usage_to_cache["stop"] = stored_usage["stop"]

        mc.set("usage-%s" % tenant_id, usage_to_cache, 2592000)

        for resource, attr, name in usages:
            result_key = name + '_' + attr
            try:
                results[result_key] = formatted[resource][attr]
            except KeyError:
                results[result_key] = None

        results = {key: result if key.endswith("du") or
                result is None else float(result)
                for key, result in results.items()}

        results = {key: float(result) for key, result in results.items()
            if result is not None}

        self.logger.debug("query result %s", results)

        # create the aggregates

        for resource_type in attributes.keys():
            for attribute in attributes[resource_type]:
                results[resource_type + '_' + attribute] = 0
                for cloud in self.resources[resource_type].keys():
                    if cloud + '_' + attribute in results:
                        results[resource_type + '_' + attribute] += results[
                            cloud + '_' + attribute]

        self.logger.debug(results)

        final_usages = dict({
            "server_usages": [],
            "start": start,
            "stop": stop,
            "tenant_id": tenant_id,
            "total_hours": (_stop_unix - _start_unix) / (60. * 60)
        }.items() + results.items())

        self.logger.debug(final_usages)
        db_cursor.close()
        return final_usages


class OsdcEucaDriver(EucaDriver):

    EUCA_FLAVORS = [{"name": "m1.small",
            "id": "m1.small",
            "vcpus": 1,
            "ram": 3584,
            "disk": 20,
            "swap": "",
            "OS-FLV-EXT-DATA:ephemeral": 0},
        {"name": "c1.medium",
            "id": "c1.medium",
            "vcpus": 2,
            "ram": 7168,
            "disk": 20,
            "swap": "",
            "OS-FLV-EXT-DATA:ephemeral": 0},
        {"name": "m1.large",
            "id": "m1.large",
            "vcpus": 4,
            "ram": 14336,
            "disk": 20,
            "swap": "",
            "OS-FLV-EXT-DATA:ephemeral": 0},
        {"name": "m1.xlarge",
            "id": "m1.xlarge",
            "vcpus": 8,
            "ram": 28672,
            "disk": 20,
            "swap": "",
            "OS-FLV-EXT-DATA:ephemeral": 0},
        {"name": "c1.xlarge",
            "id": "c1.xlarge",
            "vcpus": 8,
            "ram": 28672,
            "disk": 20,
            "swap": "",
            "OS-FLV-EXT-DATA:ephemeral": 0}]

    def __init__(self, auth_driver=None, flavors=None, usage=None,
        quota_host='10.103.112.3', quota_port=9402):
        ''' Relying on contructor injection '''

        if flavors is None:
            flavors = OsdcEucaDriver.EUCA_FLAVORS

        super(OsdcEucaDriver, self).__init__(auth_driver, flavors)

        self.usage = usage
        self.quota_host = quota_host
        self.quota_port = quota_port

    def list_quotas(self):
        ''' List the quotas from the now defunct euca-quota cloud '''
        r = requests.get('http://%s:%s/%s' % (self.quota_host, self.quota_port,
                self.auth.username()))
        return json.loads(r.text)["quota_set"]

    def list_usage(self, start, end):
        return self.usage.list_usages(start, end, self.auth.username())

    def list_security_groups(self):
        return [{
            "description": "not_implemented",
            "id": 1,
            "name": "default",
            "rules": [],
            "tenant_id": "openstack"
        }]
