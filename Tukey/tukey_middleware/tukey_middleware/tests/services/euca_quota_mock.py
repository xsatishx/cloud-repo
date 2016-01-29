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

''' Runs as a fake euca quota lister for testing purposes '''

from flask import Flask, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return '''{"quota_set": {
                "metadata_items": 0,
                "injected_file_content_bytes": 0,
                "injected_files": 0,
                "gigabytes": 0,
                "ram": 10,
                "floating_ips": 0,
                "security_group_rules": 0,
                "instances": 10,
                "volumes": 0,
                "cores": 10,
                "security_groups": 0
            }}'''

if __name__ == "__main__":
    app.run(host='127.0.0.2', debug=True, port=9402)

