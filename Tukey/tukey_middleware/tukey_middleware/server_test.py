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

import json
import os
import sys
sys.path.append(os.getcwd())

from tukey_middleware.api import nova, glance, utils
from flask import Flask
from tukey_middleware.cloud_driver.registry import CloudRegistry

from tukey_middleware.modules.instance_metadata import user_info
from tukey_middleware.modules.ids import ids



def make_app():
    '''App builder (wsgi) Entry point for REST API server'''

    app = Flask('api')

    @app.route('/', methods=['GET'])
    def version_list():
        '''Basic HTTP API version listing for Compatible APIs '''
        return json.dumps({
            "versions": [
                {
                    "id": "v1.1",
                    "status": "CURRENT",
                    "comment": "Nova compatibility API"
                },
                {
                    "id": "v1",
                    "status": "CURRENT",
                    "comment": "Glance compatibility API"
                }
            ]
        })

    settings = {
        "test_cloud": {
            "driver": "tukey_middleware.cloud_driver.osdc_euca.OsdcEucaDriver",
            "name": "Adler",
            "auth_driver_parameters": {
                "memcache_client":  {
                    "class":
                        "tukey_middleware.tests.services.mc_mock.ClientPreload",
                    "params": [["localhost:11211"], 1]
                },
                "eucarc_path":  "tukey_middleware/tests/data/%s"
            }
        },
        "test_openstack": {
            "driver": "tukey_middleware.cloud_driver.openstack.OpenStackDriver",
            "name": "Sullivan",
            "auth_driver_parameters": {
                "memcache_client":  {
                    "class":
                        "tukey_middleware.tests.services.mc_mock.ClientPreload",
                    "params": [["localhost:11211"], 1]
                }
            }

        }
    }

    registry = CloudRegistry(settings=settings)

    nova_bp = utils.set_api_manager(nova.rest, registry)
    glance_bp = utils.set_api_manager(glance.rest, registry)

    app.register_blueprint(nova_bp, url_prefix='/v1.1')
    app.register_blueprint(nova_bp, url_prefix='/v2')
    app.register_blueprint(glance_bp, url_prefix='/v2')
    app.register_blueprint(glance_bp, url_prefix='/v1')

    utils.Rest.has_tenant_id = False
    user_info_bp = utils.set_api_manager(user_info.rest, registry)
    ids_bp = utils.set_api_manager(ids.rest, registry)

    app.register_blueprint(user_info_bp, url_prefix='/user_info/v0')
    app.register_blueprint(ids_bp, url_prefix='/ids/v0')

    return app


def main():
    ''' Run the app '''
    make_app().run(debug=True, host='127.4', port=8774)

if __name__ == "__main__":
    main()
