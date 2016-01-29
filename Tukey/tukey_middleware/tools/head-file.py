#!/usr/bin/env python

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

import argparse
import sys

from utils import err, add_openstack_env
from tukey_middleware.modules.ids import Client


class IdServiceClient(object):

    def usage(self, error_msg="", usage_msg=None, exit_code=1):
        if usage_msg is None:
            usage_msg = self.parser.format_usage()
        err(error_msg)
        err(usage_msg)
        exit(exit_code)

    def run(self):
        self.parser = argparse.ArgumentParser(
                description="ssh and runs command on id file")
        self.parser.add_argument("command", type=str,
                choices=["head", "cat", "tail"])
        self.parser.add_argument("cmd_args", metavar="C", type=str,
                nargs=argparse.REMAINDER)
        self.parser.add_argument("-l", dest="login_name", type=str)
        # -d is the first flag not in the three command programs
        self.parser.add_argument("-d", dest="id_service",
                default="http://127.1:6666/", type=str)
        self.parser.add_argument("uuid", type=str)
        self.parser.add_argument("-i", dest="interface", type=str)

        add_openstack_env(self.parser)

        args = self.parser.parse_args()

        client = Client(args.id_service, os_username=args.os_username,
                os_tenant_name=args.os_tenant_name,
                os_password=args.os_password,
                os_auth_url=args.os_auth_url, os_auth_token=args.os_auth_token,
                interface=args.interface)

        file_info = client.get_id_info(args.uuid)

        if file_info.protocol == "ssh":
            file_info.login_name = args.login_name

        return file_info.read()


def main():
    client = IdServiceClient()
    sys.stdout.write(client.run())

if __name__ == "__main__":
    main()
