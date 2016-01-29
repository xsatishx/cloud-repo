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
import re
import socket

def uuid_format(uuid):
    ''' format the uuid into nodash format and return else None '''
    hexits = 5 * ("[a-fA-F0-9]",)
    dash = re.compile("%s{8}-%s{4}-%s{4}-%s{4}-%s{12}" % hexits)
    nodash = re.compile("%s{8}%s{4}%s{4}%s{4}%s{12}" % hexits)

    try:
        if dash.match(uuid):
            return uuid.replace("-", "")
        elif not nodash.match(uuid):
            return None
    except TypeError:
        return None
    return uuid


class SourceInterface():

    def __init__(self, source_ip):
        self.source_ip = source_ip
        self.true_socket = socket.socket

    def __enter__(self):

        def bound_socket(*a, **k):
            sock = self.true_socket(*a, **k)
            sock.bind((self.source_ip, 0))
            return sock

        if self.source_ip:
            socket.socket = bound_socket

    def __exit__(self, exit_type, value, traceback):
        socket.socket = self.true_socket

