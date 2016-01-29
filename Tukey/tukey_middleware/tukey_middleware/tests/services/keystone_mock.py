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

''' Runs as a fake euca cc for testing purposes '''

from flask import Flask, request

import json
import time
import datetime

app = Flask(__name__)

def expiration(token_lifetime):
    '''Returns times stamp of token_lifetime from now
    '''
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    current = time.time()
    return str(datetime.datetime.fromtimestamp(current + token_lifetime).strftime(date_format))

#keystone
@app.route("/v2.0/tokens", methods=["GET","POST"])
def tokens():

    auth = json.loads(request.data)["auth"]
    if False:#"tenantId" in auth or "tenantName" in auth:
        return '{"access": {"token": {"expires": "%s", "id": "18e59gb40fb14bd599999253dcdafaa8"}, "serviceCatalog": {}, "user": {"username": "test_user", "roles_links": [], "id": "959992c53d244fea80799989c999cd99", "roles": [], "name": "test_user"}}}' % expiration(1000)
    else:
        return '{"access": {"token": {"expires": "%(expiration)s", "id": "test_token", "tenant": {"description": null, "enabled": true, "id": "65e91ae53f564ad98e7733dc6a20217f", "name": "mgreenway"}}, "serviceCatalog": [{"endpoints": [{"adminURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f", "region": "RegionOne", "internalURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f", "publicURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f"}], "endpoints_links": [], "type": "volume", "name": "volume"}, {"endpoints": [{"adminURL": "http://%(host)s/v1", "region": "RegionOne", "internalURL": "http://%(host)s/v1", "publicURL": "http://%(host)s/v1"}], "endpoints_links": [], "type": "image", "name": "glance"}, {"endpoints": [{"adminURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f", "region": "RegionOne", "internalURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f", "publicURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f"}], "endpoints_links": [], "type": "compute", "name": "nova"}, {"endpoints": [{"adminURL": "http://%(host)s/services/Admin", "region": "RegionOne", "internalURL": "http://%(host)s/services/Cloud", "publicURL": "http://%(host)s/services/Cloud"}], "endpoints_links": [], "type": "ec2", "name": "ec2"}, {"endpoints": [{"adminURL": "http://10.103.105.2:35357/v2.0", "region": "RegionOne", "internalURL": "http://%(host)s/v2.0", "publicURL": "http://%(host)s/v2.0"}], "endpoints_links": [], "type": "identity", "name": "keystone"}], "user": {"username": "mgreenway", "roles_links": [], "id": "95eae2c53d244fea80762689cd97cd1f", "roles": [{"id": "15217113754b4a03806868ae012e575d", "name": "Member"}], "name": "mgreenway"}}}' % {"host": "127.0.0.4:8774", "expiration": expiration(1000)}

@app.route("/v2.0/tenants", methods=["GET","POST"])
def tenants():

    return '{"tenants_links": [], "tenants": [{"enabled": true, "description": null, "name": "test_user", "id": "33391ae53f5000000e7730000a20217f"}]}'


if __name__ == "__main__":
    app.run(host='127.4', debug=True, port=5000)

