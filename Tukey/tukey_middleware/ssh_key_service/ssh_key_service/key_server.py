#  Copyright 2014 Open Cloud Consortium
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
''' Listens for requests to create/delete entries from users' authorized_keys
files '''

import argparse
import gnupg
import json
import os
import pwd
import logging

from flask import Flask, request, abort
from ssh_key_service import local_settings

app = Flask(__name__)

#logging settings
logger = logging.getLogger('tukeysshkeyserver')


def file_key_user(encrypted):
    ''' takes gpg encrypted message and returns the key file name, the
    public key and the username '''

    message = GPG.decrypt(encrypted, passphrase=GPG_PASSPHRASE)
    logger.debug("the message is %s", message)

    key_info = json.loads(str(message))

    if key_info["passphrase"] != PASSPHRASE:
        abort(401)

    logger.debug("username %s", key_info['username'])

    key_file = "%s/.ssh/authorized_keys" % pwd.getpwnam(key_info["username"])[5]

    logger.debug("file name %s", key_file)

    public_key = key_info["public_key"]

    if public_key[-1] != '\n':
        public_key = public_key + '\n'

    return key_file, public_key, key_info["username"]


@app.route("/", methods=['PUT'])
def put():
    ''' Appends key key_text to authorized_keys file key_file_name.
    If key_text ends with a newline it is appended to the file that's
    name is specified by the string key_file_name otherwise a newline
    is concatenated to the end of key_text and then appended.'''

    key_file, public_key, username = file_key_user(request.data)

    logger.debug("going to open %s", key_file)

    file_existed = os.path.isfile(key_file)

    key_file = open(key_file, 'a')
    key_file.write(public_key)

    if not file_existed:
        pwd_ent = pwd.getpwnam(username)
        os.fchown(public_key, pwd_ent.pw_uid, pwd_ent.pw_gid)

    key_file.close()


@app.route("/", methods=['DELETE'])
def delete():
    ''' Deletes any line matching the the string key_text from
    file key_file_name.
    Reads in all lines of the
    '''

    key_file, public_key, _ = file_key_user(request.data)

    key_file = open(key_file)
    keys = key_file.readlines()
    key_file.close()

    key_file = open(key_file, 'w')

    logger.debug(public_key)
    logger.debug([key for key in keys if key != public_key])

    key_file.writelines([key for key in keys if key != public_key])

    key_file.close()


def main():
    ''' Run the ssh key service server '''

    global GPG
    global GPG_PASSPHRASE
    global PASSPHRASE

    parser = argparse.ArgumentParser(
            description="append and remove public keys from authorized_keys")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--gpg-home")
    parser.add_argument("--gpg-passphrase")
    parser.add_argument("--passphrase")

    args = parser.parse_args()

    GPG_PASSPHRASE = local_settings.KEY_SERVER_GPG_PASSPHRASE
    PASSPHRASE = local_settings.KEY_SERVER_PASSPHRASE
    gpg_home = local_settings.KEY_SERVER_GPG_HOME

    if args.gpg_home:
        gpg_home = args.gpg_home

    if args.gpg_passphrase:
        GPG_PASSPHRASE = args.gpg_passphrase

    if args.passphrase:
        PASSPHRASE = args.passphrase

    GPG = gnupg.GPG(gnupghome=gpg_home)
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

