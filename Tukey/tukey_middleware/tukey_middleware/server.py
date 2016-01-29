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
''' Flask server code for production use as WSGI with Apache '''

import argparse
import json
import os
import sys
sys.path.append(os.getcwd())

from flask import Flask

from tukey_middleware.api import nova, glance, utils, keystone, osdc, cinder
from tukey_middleware.cloud_driver.registry import CloudRegistry
from tukey_middleware.modules import pipelines
from tukey_middleware.modules.ids import server as ids
from tukey_middleware.modules.metadata import server as metadata
from tukey_middleware.modules.instance_metadata import user_info

import local_settings


def make_app():
    '''App builder (wsgi) Entry point for REST API server'''

    app = Flask('api')

    @app.route('/', methods=['GET'])
    def version_list():
        '''Basic HTTP API version listing for Compatible APIs '''
        return json.dumps({
            "versions": [
                {
                    "id": "v1",
                    "status": "CURRENT",
                    "comment": "Nova compatibility API"
                },
                {
                    "id": "v1",
                    "status": "CURRENT",
                    "comment": "Nova and Glance compatibility API"
                },
                {
                    "id": "v1",
                    "status": "CURRENT",
                    "comment": "Glance compatibility API"
                },
                {
                    "id": "v2.0",
                    "status": "CURRENT",
                    "comment": "Keystone compatibility API"
                },
                {
                    "id": "user_info/v0",
                    "status": "CURRENT",
                    "comment": "VM username and password provider"
                },
                {
                    "id": "user_info/v0",
                    "status": "CURRENT",
                    "comment": "VM username and password provider"
                },
                {
                    "id": "modules/v0",
                    "status": "CURRENT",
                    "comment": "VM username and password provider for "
                            "init-cloud.sh"
                },
                {
                    "id": "metadata/v0",
                    "status": "CURRENT",
                    "comment": "Metadata service"
                },
                {
                    "id": "ids/v0",
                    "status": "CURRENT",
                    "comment": "Object ID service"
                }
            ]
        })

    registry = CloudRegistry(settings=local_settings.settings)

    nova_bp = utils.set_api_manager(nova.rest, registry)
    glance_bp = utils.set_api_manager(glance.rest, registry)
    cinder_bp = utils.set_api_manager(cinder.rest, registry)
    keystone_bp = utils.set_api_manager(keystone.rest, registry)
    osdc_bp = utils.set_api_manager(osdc.rest, registry)

    # TODO: need to have some kind of module thing
    pipeline_bp = utils.set_api_manager(pipelines.rest, registry)

    # this is stupid this is all really stupid!
    app.register_blueprint(nova_bp, url_prefix='/compute')
    app.register_blueprint(glance_bp, url_prefix='/v1')
    app.register_blueprint(cinder_bp, url_prefix='/volume')

    app.register_blueprint(keystone_bp, url_prefix='/v2.0')

    app.register_blueprint(osdc_bp, url_prefix='/osdc/v0')

    utils.Rest.has_tenant_id = False

    user_info_bp = utils.set_api_manager(user_info.rest, registry)
    ids_bp = utils.set_api_manager(ids.rest, registry)
    metadata_bp = utils.set_api_manager(metadata.rest, registry)

    app.register_blueprint(user_info_bp, url_prefix='/user_info/v0')
    app.register_blueprint(user_info_bp, url_prefix='/modules/v0')

    app.register_blueprint(ids_bp, url_prefix='/ids/v0')
    app.register_blueprint(metadata_bp, url_prefix='/metadata/v0')

    return app


def main():
    ''' Run the app '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8774, type=int)
    parser.add_argument("--host", default='0.0.0.0')
    args = parser.parse_args()


    make_app().run(debug=True, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
