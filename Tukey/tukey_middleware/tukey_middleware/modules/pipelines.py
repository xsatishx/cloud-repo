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

import flask
import json
import base64
import requests
from flask import request
from tukey_middleware.cloud_driver.registry import CloudRegistry
from tukey_middleware.api.utils import Rest

from tukey_middleware import local_settings

# import the local settings

rest = Rest('v0', __name__)

@rest.post('/pipeline')
def launch_pipeline(data):
    # Generate an auth token for an admin user
    '''
    {
        "cloud": "sullivan",
        # b64 encoded
        "config_file": "date    20130702\nsp  ce\n ...."
        #"flavorRef": "1",
        #"imageRef": "someimageid",
        "name": "my-pipeline-vm",
        # we now have automount so not needed
        #"samba_password": "horrible_secret",
        "username": "me",
        "script_path": "/glusterfs/users/myuser/scripts/pipeline.py",
        # these aren't really needed?????
        #"input_dir": "/glusterfs/bionimbus/modENCODE_ChIP-seq",
        #"output_dir": "/glusterfs/users/pmakella/test"
    }
    '''

    print "THE DATA ", data
    args = json.loads(data)
    cloud = rest.api_manager.get_cloud_by_id(args.pop("cloud"))

    if "userdata" in args:
        userdata_b64 = args.pop("userdata")
        #TODO:
        # mimic the run userdata logic and embed it in our new stuff
    # get the config files if any
    conf = " ".join(['<(echo -ne "%s")' % base64.b64decode(args.pop(k))
            for k in args.keys() if k.startswith("config_file")])

        #sudo mount -t cifs \\\\\\\\10.103.114.4\\\\glusterfs /glusterfs/ -o user=%(username)s,password=%(samba_password)s,noperm,nobrl,rsize=65536
    args["userdata"] = ('''#!/bin/bash
        %(script_path)s ''' % args) + conf# + ('''
        #euca-terminate-instances $(wget -O - -q http://meta-data/1.0/meta-data/instance-id)''' % args)

    print args["userdata"]

    #del args["samba_password"]
    del args["script_path"]
    del args["username"]

    #e94be063-b033-4eed-bcdd-de60f2b6aad5
    return json.dumps(cloud.launch_instances(args.pop("name"),
            local_settings.modules["pipelines"]["image"],
            local_settings.modules["pipelines"]["size"], **args))

