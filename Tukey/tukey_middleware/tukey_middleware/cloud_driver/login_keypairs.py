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

''' For managing ssh public keys on login nodes '''
import gnupg
import json
import os
import requests
import sqlalchemy
import tempfile

from M2Crypto import DSA, BIO
from novaclient import exceptions as nova_exceptions
from novaclient.client import Client
from novaclient.client import HTTPClient
from subprocess import Popen, PIPE
from tukey_middleware import utils
from tukey_middleware.cloud_driver.base import CloudDriver
from tukey_middleware.cloud_driver.osdc_euca import OsdcEucaDriver


class SshKeyStoreClient(object):
    ''' Client for managing pubkeys with the current tukeyauth
    postgres database to be replaced by Keystone or LDAP or a
    combination of both'''

    def __init__(self, username, cloud_name, db_connection_string):
        self.cloud_name = cloud_name
        self.username = username
        self.engine = sqlalchemy.create_engine(db_connection_string)
        self.logger = utils.get_logger()

    def insert_sshkey(self, pubkey, fingerprint, keyname):
        ''' Insert pubkey fingerprint keyname, userid and cloud_id into the
        keypair table '''

        insert_and_query = """
            insert into keypair (pubkey, fingerprint, name, userid, cloud_id)
            select '%(pubkey)s', '%(fingerprint)s', '%(keyname)s', userid,
                cloud.cloud_id
            from cloud, login where username='%(username)s' and
                cloud_name='%(cloud)s' and login.cloud_id=cloud.cloud_id;
            select id from keypair where fingerprint='%(fingerprint)s';
        """ % {"pubkey": pubkey, "fingerprint": fingerprint, "keyname": keyname,
                    "username": self.username, "cloud": self.cloud_name}

        with self.engine.begin() as connection:
            result = connection.execute(insert_and_query)

        return result

    def delete_sshkey(self, keyname):
        ''' Delete key with keyname, username and cloud_name from keypair'''

        delete_keypair = """
            delete from keypair using cloud, login
            where name='%(keyname)s' and keypair.userid=login.userid and
            cloud.cloud_name='%(cloud)s' and cloud.cloud_id=login.cloud_id
            and keypair.cloud_id = cloud.cloud_id
            and login.username='%(username)s';
        """ % {"keyname": keyname, "cloud": self.cloud_name,
                "username": self.username}

        self.logger.debug(delete_keypair)

        with self.engine.begin() as connection:
            result = connection.execute(delete_keypair)

        return result

    def list_keypairs(self):
        ''' All keypairs from keypair with username and cloud_name '''
        query = """
            select name, fingerprint, pubkey from keypair, login, cloud
            where cloud_name='%(cloud)s' and cloud.cloud_id = keypair.cloud_id
            and login.cloud_id = cloud.cloud_id
            and login.username='%(username)s' and login.userid=keypair.userid;
        """ % {"username": self.username, "cloud": self.cloud_name}

        try:
            with self.engine.begin() as connection:
                results = connection.execute(query)
        except Exception:
            return []

        return [{"keypair": {"name": row[0], "fingerprint": row[1],
            "public_key": row[2]}} for row in results]

    def get_pubkey(self, keyname):

        select_keypair = """
            select pubkey, fingerprint from keypair, cloud, login
            where name='%(keyname)s' and username='%(username)s' and
            cloud_name='%(cloud)s' and cloud.cloud_id = login.cloud_id
            and login.userid = keypair.userid;
        """ % {"keyname": keyname, "username": self.username,
                "cloud": self.cloud_name}

        self.logger.debug(select_keypair)
        with self.engine.begin() as connection:
            return [row[0] for row in connection.execute(select_keypair)][0]


class SshKeyserviceClient(object):
    ''' This is the client for the HTTP ssh key population
    service.  The host runs on a login node and modifies a users
    authorized_keys file removing and inserting pubkeys based on
    authorized, encrypted requests'''

    def __init__(self, username, fingerprint, gpg_home_dir,
        gpg_host_pubkey_filename, gpg_passphrase, host_passphrase, host):

        self.username = username
        self.gpg_host_pubkey_filename = gpg_host_pubkey_filename
        self.host_passphrase = host_passphrase
        self.fingerprint = fingerprint
        self.gpg_passphrase = gpg_passphrase
        self.host = host

        self.gpg = gnupg.GPG(gnupghome=gpg_home_dir)
        self.logger = utils.get_logger()

    def _get_recipient(self):
        self.logger.debug(self.gpg_host_pubkey_filename)

        with open(self.gpg_host_pubkey_filename) as keyfile:
            host_key = keyfile.read()
        self.logger.debug(host_key)

        import_result = self.gpg.import_keys(host_key)

        return import_result.fingerprints[0]

    def _send_request(self, public_key, method):

        raw_message = json.dumps(
        {
            "username": self.username,
            "public_key": public_key,
            "passphrase": self.host_passphrase
        })

        message = self.gpg.encrypt(raw_message, self._get_recipient(),
            always_trust=True, sign=self.fingerprint,
            passphrase=self.gpg_passphrase)

        self.logger.debug("host: %s", self.host)

        resp = method(self.host, data=str(message))

        if resp.status_code != 200:
            #TODO: need our own proper exception here
            raise

        self.logger.debug("content %s", resp.text)
        return resp.text

    def send_key(self, public_key):
        return self._send_request(public_key, requests.put)

    def delete_key(self, public_key):
        return self._send_request(public_key, requests.delete)


class SshKeygen(object):

    SSH_KEYGEN = '/usr/bin/ssh-keygen'

    def _run_ssh(self, arguments, key_material):
        command = self.SSH_KEYGEN + arguments
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(key_material)
        temp.close()

        process = Popen(command % temp.name, stdout=PIPE, shell=True)
        #TODO: log exit code
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        os.unlink(temp.name)

        return output

    def _pubkey_from_private(self, private_key):
        return self._run_ssh(" -f %s -i -m PKCS8", private_key)[:-1]

    def fingerprint(self, public_key):
        return self._run_ssh(" -lf %s", public_key).split()[1]

    def generate_keypair(self, password=None):
        ''' Generate a 1024 bit DSA key.  Someday they will be password
        protected.
        returns public key, private key '''

        dsa = DSA.gen_params(1024, os.urandom)

        mem_pub = BIO.MemoryBuffer()
        mem_private = BIO.MemoryBuffer()

        dsa.gen_key()
        if password is None:
            dsa.save_key_bio(mem_private, cipher=None)
        else:
            dsa.save_key_bio(mem_private, callback=lambda _: password)

        private_key = mem_private.getvalue()

        dsa.save_pub_key_bio(mem_pub)

        public_key = self._pubkey_from_private(mem_pub.getvalue())

        return public_key, private_key


class LoginKeypairsDriver(CloudDriver):
    ''' Driver implementation to handle keypairs for SSH login nodes'''

    def __init__(self, cloud_name, cloud_id, db_connection_string, fingerprint,
            gpg_home_dir, gpg_host_pubkey_filename, gpg_passphrase,
            host_passphrase, host, username, auth_driver=None):

        self.keygen = SshKeygen()
        self.db_client = SshKeyStoreClient(username, cloud_id,
                db_connection_string)

        self.remote_client = SshKeyserviceClient(username, fingerprint,
                gpg_home_dir, gpg_host_pubkey_filename, gpg_passphrase,
                host_passphrase, host)

        self.cloud = "Login %s" % cloud_name
        self.cloud_id = "login%s" % cloud_id

        # a special tukey comment
        # in scenarios such as the heartbleed bug of 4/14 we can easily
        # determine which privates were generated by tukey and downloaded
        # over ssl.
        self.key_comment = "tukey@opensciencedatacloud.org"


    def list_keypairs(self):
        return self.db_client.list_keypairs()

    def import_keypair(self, keypair_name, public_key, private_key=''):
        ''' import keypair sent by the user'''
        fingerprint = self.keygen.fingerprint(public_key)
        try:
            self.db_client.insert_sshkey(public_key, fingerprint, keypair_name)
            self.remote_client.send_key(public_key)
        except sqlalchemy.exc.IntegrityError:
            raise nova_exceptions.Conflict(409,
                    message="Key pair '%s' already exists." % keypair_name)

        return {"keypair": {
                "public_key": public_key,
                "private_key": private_key,
                "user_id": "",
                "name": keypair_name,
                "fingerprint": fingerprint}}

    def create_keypair(self, keypair_name):
        ''' Create a new keypair then import the public key '''
        public_key, private_key = self.keygen.generate_keypair()
        public_key = "%s %s" % (public_key, self.key_comment)
        return self.import_keypair(keypair_name, public_key,
                private_key=private_key)

    def delete_keypair(self, keypair_name):
        ''' Delete keypair with name keypair_name from the database and from
        the login node '''
        try:
            pubkey = self.db_client.get_pubkey(keypair_name)
            self.db_client.delete_sshkey(keypair_name)
            self.remote_client.delete_key(pubkey)
        except sqlalchemy.exc.IntegrityError:
            raise nova_exceptions.Conflict(404,
                    message="Key pair '%s' doesn't exist." % keypair_name)
        return


class AllKeypairsDriver(CloudDriver):
    ''' Driver implementation for creating/importing keypairs for all clouds'''

    def __init__(self, drivers):
        self.drivers = drivers

    @staticmethod
    def _all_keypairs(drivers, public_key, keypair_name):
        ''' Run import on all clouds in drivers. Once imported push on done
        stack so if we run into a problem like the next cloud already has a
        keypair with keypair_name we can pop and delete the imported keypairs
        and raise the exception '''
        done = []

        for driver in drivers:
            try:
                # bug the private key disapears into th eehter
                new_keypair = driver.import_keypair(keypair_name, public_key)
                done.append(driver)
            except nova_exceptions.NotFound:
                # import not implemented for this cloud
                continue
            except Exception as exc:
                for d in done:
                    d.delete_keypair(keypair_name)
                raise exc

        return new_keypair

    def import_keypair(self, keypair_name, public_key):
        return self._all_keypairs(self.drivers, public_key, keypair_name)

    def create_keypair(self, keypair_name):
        ''' Create keypair on one cloud then import to all the others. If one
        of the clouds is Eucalyptus then create the keypair on that cloud
        because Eucalyptus 2.0 doesn't allow you to import keypairs'''

        # eucalyptus doesn't support importing keypairs. so if we want to
        # create a keypair on all clouds and one is eucalyptus we can create
        # the keypair there then upload else where
        for driver in self.drivers:
            if type(driver) == OsdcEucaDriver:
                keypair = driver.create_keypair(keypair_name)
                self._all_keypairs(
                        [d for d in self.drivers if type(d) != OsdcEucaDriver],
                        keypair["public_key"], keypair_name)
                return keypair

        keypair = self.drivers[0].create_keypair(keypair_name)
        self._all_keypairs(self.drivers[1:], keypair["public_key"],
                keypair_name)
        return keypair

