#  Copyright 2014 Open Cloud Consortium
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

''' HTTP API definitions for compatibility with the Cinder OpenStack API
http://api.openstack.org/api-ref.html '''

import flask
import json
from utils import Rest
import sys

rest = Rest('cinder', __name__)


@rest.after_request
def add_mimetype(response):
    response.headers["content-type"] = "application/json"
    return response


@rest.get('/types')
def list_types():
    return rest.api_manager.list_for_all("volume_types",
            lambda c: c.list_volume_types())


@rest.get('/volumes/detail')
def list_volumes():
    return rest.api_manager.list_for_all("volumes", lambda c: c.list_volumes())


@rest.post('/volumes')
def create_volume(data):

    volume_info = json.loads(data)["volume"]
    size = volume_info.pop("size")
    del volume_info["status"]
    del volume_info["attach_status"]
    volume_info["name"] = volume_info["display_name"]
    volume_info["display_name"] = volume_info["display_name"][
        volume_info["display_name"].find("-") + 1:]

    return rest.api_manager.do_action("volume", volume_info,
            lambda c, k: c.create_volume(size,
            **{ke: v for ke, v in k.items() if ke != "name"}))


@rest.get('/snapshots/detail')
def list_snapshots():
    return rest.api_manager.list_for_all("snapshots",
            lambda c: c.list_volume_snapshots())


@rest.get('/os-quota-sets/<tenant_id2>')
def get_quota(tenant_id2):
    return rest.api_manager.get_item("quota_set",
        lambda cloud: cloud.get_volume_quotas(tenant_id2))


@rest.get('/volumes/<volume_id>')
def get_volume(volume_id):
    #TODO: implement paging
    # ?limit=1000&
    # maybe we can fix paging
    volume = rest.api_manager.get_item("volume",
        lambda cloud: cloud.get_volume(volume_id))

    return volume


@rest.delete('/volumes/<volume_id>')
def delete_volume(volume_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_volume(volume_id))
    cloud.delete_volume(volume_id)
    return ""

