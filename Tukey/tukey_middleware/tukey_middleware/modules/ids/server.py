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
''' The Flask HTTP API for Obejct ID service. '''

import json
import flask

from flask import request, g
from tukey_middleware.flask_utils import (get_user_from_request, return_error,
        with_user)

from .ids import create_id, modify_acl, get_metadata, IdAcl


rest = flask.Blueprint("v0.1", __name__)

@rest.route("/<uuid>")
@return_error
@with_user(rest)
def get_id(uuid):
    ''' Get the record associated with this UUID.
    TODO: timing attack information leak
    '''
    return json.dumps(get_metadata(g.user, uuid, IdAcl.READ,
            ignore=["acl"]))


@rest.route("/<uuid>/acl")
@return_error
@with_user(rest)
def get_acl(uuid):
    ''' return acl metadata associated with uuid'''
    return json.dumps(get_metadata(g.user, uuid, IdAcl.READ,
            ignore=["filepath", "cloud_name"]))


@rest.route("/<uuid>/acl", methods=["PUT"])
@return_error
@with_user(rest)
def set_acl(uuid):
    '''Set acl associated with id to JSON PUT data'''
    data = json.loads(request.data)
    modify_acl(g.user, uuid, data, lambda old, new: new)
    return "Success"


@rest.route("/<uuid>/acl", methods=["POST"])
@return_error
@with_user(rest)
def update_acl(uuid):
    '''Update acl associated with id to JSON PUT data'''
    data = json.loads(request.data)
    modify_acl(g.user, uuid,
            data, lambda old, new: old + new)
    return "Success"


@rest.route("/<uuid>")
def update_id(uuid):
    '''Update id metadata with new values. TODO: Implement'''
    if request.headers["content-type"].lower() != "application/json":
        return ("content-type must be application/json\n", 400)
    try:
        data = json.loads(request.data)
    except ValueError:
        return ("Request body is not valid JSON\n", 400)

    # call function for stuf


@rest.route("/", methods=["PUT", "POST"])
@return_error
@with_user(rest)
def set_id():
    ''' Create a new object or collection of objects
    list as such ["b0144f1805876f2b903339021d007a34",
        {
            "username": "mgreenway",
            "protocol": "ssh",
            "filepath": "/home/ubuntu/tukey_middleware/README.rst",
            "tenant_name": "mgreenway",
            "acl": [{
                "grantee": {
                    "type": "username",
                    "id": "mgreenway"
                },
                "permission": "full_control"
            },
            {
                "grantee": {
                    "type": "tenant_name",
                    "id": "mgreenway"
                },
                "permission": "full_control"
            }],
            "cloud_name": "sullivan",
            "metadata_server": ""}]
    The list can be either ids of existing files or new object metadata

    1. check that the user can create new IDs
    2. validate the ID entry
    3. append user information to the entry
    4. generate a new UUID for the record
    5. send the record to the datastore
    6. return the UUID
    '''

    if request.headers["content-type"].lower() != "application/json":
        return ("content-type must be application/json\n", 400)
    try:
        data = json.loads(request.data)
    except ValueError:
        return ("Request body is not valid JSON\n", 400)


    return create_id(g.user, data, acl=data.get("acl", None))[0]
