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

'''HTTP API required for Tukey Portal to talk to the Tukey Middleware '''

import flask
import json
import memcache

from flask import Blueprint
from tukey_middleware.auth.token_store import TokenStore

rest = Blueprint('osdc', __name__)


@rest.route('/clouds', methods=('GET', 'POST'))
def clouds():
    ''' Looks up auth token key and returns the clouds this user
    has been authenticated against '''

    token_store = TokenStore(memcache.Client(['127.0.0.1:11211']))
    token_id = flask.request.headers["x-auth-token"]
    token_info = token_store.get(str(token_id))
    active_clouds = json.dumps(
            [key for key in token_info if key != "__tukey_internal"])
    print active_clouds
    return active_clouds

