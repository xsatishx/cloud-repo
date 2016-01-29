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

''' HTTP API definitions for compatibility with the Glance OpenStack API
http://api.openstack.org/api-ref.html '''

import flask
import json
from utils import Rest
import sys
from glanceclient.v1 import images as glance_images

rest = Rest('glance', __name__)


@rest.after_request
def add_mimetype(response):
    response.headers["content-type"] = "application/json"
    return response


@rest.get('/images/detail')
def list_images():
    return rest.api_manager.list_for_all("images", lambda c: c.list_images())


@rest.get('/images/<image_id>')
def get_image(image_id):
    #TODO: implement paging
    # ?limit=1000&property-image_type=snapshot
    # maybe we can fix paging
    image = rest.api_manager.get_item("image",
        lambda cloud: cloud.get_image(image_id))

    @flask.after_this_request
    def add_headers(response):
        for k, v in json.loads(image)["image"].items():
            if k not in ['_info', 'properties']:
                response.headers[str('x-image-meta-%s' % k)] = str(v)

        return response

    return image


@rest.put('/images/<image_id>')
def edit_image(data, image_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_image(image_id))

    meta = {}
    prefix = 'x-image-meta-'
    for header, value in flask.request.headers.items():
        header = header.lower()
        if header.startswith(prefix) and header[
                len(prefix):].replace("-", "_") in glance_images.UPDATE_PARAMS:
            param = header[len(prefix):].replace("-", "_")
            meta[param] = value

    image = cloud.set_image_metadata(image_id, **meta)

    # TODO: duplicated code find a way to fix this!
    @flask.after_this_request
    def add_headers(response):
        for k, v in image.items():
            if k not in ['_info', 'properties']:
                response.headers['x-image-meta-%s' % k] = v
        return response

    return json.dumps({"image": image})


@rest.delete('/images/<image_id>')
def delete_image(image_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_image(image_id))
    cloud.delete_image(image_id)
    return ""
