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
''' The Flask HTTP API for Metadata service. '''

import json
import flask
import xmldict
import socket

from .metadata import update_metadata, list_projects
from flask import request, g
from functools import partial
from tukey_middleware.couch import Couch
from tukey_middleware.flask_utils import return_error, with_user, same_server
from tukey_middleware.local_settings import metadata as settings
from tukey_middleware.modules.ids.client import Client as IdServiceClient
from tukey_middleware.modules.ids.ids import create_id

rest = flask.Blueprint("metadata", "name")

ID_SERVICE = "http://localhost:8774"
ID_SERVICES = ["http://localhost:8774", "http://172.16.1.76:8774"]


@rest.route("/clouds/<cloud>")
@return_error
@with_user(rest)
def get_cloud_info(cloud):
    ''' Return info about the cloud '''

    couch = Couch("clouds")
    return json.dumps(couch[cloud])


@rest.route("/<project_name>", methods=["GET"])
@return_error
@with_user(rest)
def get_metadata(project_name):
    ''' Return the full metadata of the project '''
    couch = Couch(project_name)
    # Wrong!
    # TOOD: fix this
    return json.dumps(couch)

@rest.route("/", methods=["GET"])
@return_error
@with_user(rest)
def get_projects():
    ''' List of projects that this user can write to'''
    return json.dumps(list_projects(g.user,
            request.args.get('write', False)))


def _create_id():
    ''' Note the else branch has not been tested!'''
    for service in settings["id_services"]:
        if same_server(service):
            return partial(create_id, g.user)
    else:
        id_client = IdServiceClient(settings["id_services"][0],
                id_service_auth_token=g.user.id_auth_token)
        return lambda record, acl: id_client.register_collection(record,
                extra={"acl": acl})


@rest.route("/<project_name>", methods=["PUT"])
@return_error
@with_user(rest)
def put_metadata(project_name):
    ''' Return info about the cloud '''

    if request.headers["content-type"] in ["xml", "text/xml",
            "application/xml"]:
        raw_metadata = xmldict.xml_to_dict(request.data)
    elif request.headers["content-type"] in ["json", "text/json",
            "application/json"]:
        raw_metadata = json.loads(request.data)

    host, port = request.host.split(":")
    metadata_service = "http://%s:%s" % (socket.gethostbyaddr(host)[0], port)
    return update_metadata(g.user, project_name, raw_metadata, metadata_service,
            _create_id())
