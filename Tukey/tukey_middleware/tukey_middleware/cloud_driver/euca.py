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

''' Eucalyptus cloud '''

from tukey_middleware.cloud_driver.base import CloudDriver
from functools import wraps
from .instance import Instance
from libcloud.compute.providers import get_driver
from libcloud.compute.types import InvalidCredsError
from libcloud.compute.types import Provider
from novaclient import exceptions as nova_exceptions
from subprocess import Popen, PIPE
from tukey_middleware.utils import debug_result


import sys
import time
import xmldict


def invalid_creds_retry(fn):
    ''' Try the request 10 sleeping 0.25 seconds between requests. After the
    10 try which should be about 2.5 seconds rethrow the InvalidCredsError'''

    @wraps(fn)
    def decorated(*args, **kwds):
        for i in range(10):
            try:
                return fn(*args, **kwds)
            except InvalidCredsError as e:
                time.sleep(0.25)
                pass
        raise InvalidCredsError(e)
    return decorated


class EucaDriver(CloudDriver):

    #TODO: replace with a library
    SSH_KEYGEN = '/usr/bin/ssh-keygen'

    def __init__(self, auth_driver=None, flavors=[]):
        ''' Relying on contructor injection '''

        super(EucaDriver, self).__init__(auth_driver)

        self.flavors = flavors

        Driver = get_driver(Provider.EUCALYPTUS)
        self.conn = Driver(self.auth.ec2_access_key(),
                secret=self.auth.ec2_secret_key(), host=self.auth.host(),
                port=self.auth.port(), path=self.auth.path(), secure=False)

    def _encode_id(self, id):
        base = id.split("-")[1].lower()
        #TODO: need to put a unique id here so that we can dismiss or accept
        return "%s%s-%s00-0000-0000-000000000000" % ("00", base[:6],
            base[6:8])

    def _decode_id(self, id_type, id):
        return "%s-%s" % (id_type, str(id[2:8] + id[9:11]).upper())

    def _get_item(self, items, item_id):
        for i in items:
            if i["id"] == item_id:
                return i
        return None

    def _format_instance(self, node):
        '''Take a libcloud node and convert to OpenStack style tukey dict'''

        return Instance(id=self._encode_id(node.id),
                  name=node.id,
                  address=node.extra["private_dns"],
                  size=node.extra["instancetype"],
                  image_id=self._encode_id(node.extra["imageId"]),
                  key_name=node.extra["keyname"], status=node.extra["status"],
                  created_at=node.extra["launchdatetime"],
                  user_id=self.auth.username()).as_dict()

    @invalid_creds_retry
    def list_instances(self, nodes=None):
        if nodes is None:
            nodes = self.conn.list_nodes()
        instances = []
        for node in nodes:
            instances.append(self._format_instance(node))
        return instances

    @invalid_creds_retry
    def list_keypairs(self):
        ''' List the keys, libcloud didn't work so we had to fetch some xml'''

        aws_schema = "http://ec2.amazonaws.com/doc/2010-08-31/"
        xml_as_dict = xmldict.xml_to_dict(self.conn.connection.request(
                self.conn.path, params={"Action": "DescribeKeyPairs"}
                ).__dict__["body"].replace(aws_schema, ""))
        if xml_as_dict["DescribeKeyPairsResponse"]["keySet"] is None:
            keypairs = []
        else:
            keypairs = xml_as_dict["DescribeKeyPairsResponse"]["keySet"]["item"]

            if "keyName" in keypairs:
                keypairs["keyMaterial"] = ""
                keypairs = [keypairs]
            else:
                for item in keypairs:
                    if "keyName" in keypairs:
                        item["keyMaterial"] = ""

        return [{"public_key": "", "name": k["keyName"],
            "fingerprint": k["keyFingerprint"]} for k in keypairs]

    def list_sizes(self):
        return self.flavors

    def get_instance(self, instance_id):
        return self._get_item(self.list_instances(), instance_id)

    @debug_result
    def get_image(self, image_id):
        return self._get_item(self.list_images(), image_id)

    def get_size(self, size_id):
        return self._get_item(self.list_sizes(), size_id)

    @invalid_creds_retry
    def delete_instance(self, instance_id):
        for i in self.conn.list_nodes():
            if self._encode_id(i.id) == instance_id:
                return self.conn.destroy_node(i)

    @invalid_creds_retry
    def list_images(self):
        #TODO: add more shim as needed

        containers = {"machine": "ami", "ramdisk": "ari", "kernel": "aki"}

        #json_results = json_results.replace('"state": "available"','"state": "active"')
        return [{"id": self._encode_id(im.id),
            "name": im.name,
            "status": "active",
            "deleted_at": None,
            "deleted": False,
            "protected": False,
            "updated": "",
            "created": "",
            "owner": im.extra["ownerid"],
            "user_id": "mgreenway",
            "architecture": "x86_64",
            "state": "active",
            "links": [{
                    "href": "http://127.0.0.1/v1.1/mgreenway/images/detail",
                    "rel": "self"
                },
                {
                    "href": "http://127.0.0.1/mgreenway/images/detail",
                    "rel": "bookmark"
                }],
            "progress": 100,
            "minRam": 0,
            "container_format": containers[im.extra["imagetype"]],
            "is_public": im.extra["ispublic"],
            "image_type": "snapshot",
            "properties": {
                "image_type": "snapshot"
            },
            "metadata": {}} for im in self.conn.list_images()]

    def create_keypair(self, keypair_name):
        ''' Create euca keypair then generate a public_key using commandline
        ssh-keygen.'''
        try:
            resp = self.conn.ex_create_keypair(name=keypair_name)
            resp['name'] = keypair_name
            resp['private_key'] = resp['keyMaterial']
            resp['fingerprint'] = resp['keyFingerprint']

            #TODO use a library to do this
            command = " ".join(["/bin/echo -e ",
                    "'%s'" % resp['private_key'].replace('\n', '\\n'), "|",
                    self.SSH_KEYGEN, "-y -f /dev/stdin"])

            process = Popen(command, stdout=PIPE, shell=True)
            resp['public_key'] = process.communicate()[0]

            return resp
        except Exception:
            raise nova_exceptions.Conflict(409,
                    message="Key pair '%s' already exists." % keypair_name)

    def delete_keypair(self, keypair_name):
        resp = self.conn.ex_delete_keypair(keypair_name)
        return resp


    @invalid_creds_retry
    def _create_node(self, name=None, image=None, size=None, ex_keyname=None,
            ex_mincount=None, ex_userdata=None):
        return self.conn.create_node(name=name, image=image, size=size,
                ex_keyname=ex_keyname, ex_mincount=ex_mincount,
                ex_userdata=ex_userdata)

    def launch_instances(self, name, image, flavor, meta=None, files=None,
            reservation_id=None, min_count=None,
            max_count=None, security_groups=None, userdata=None,
            key_name="", availability_zone=None,
            block_device_mapping=None, nics=None, scheduler_hints=None,
            config_drive=None, **kwargs):

        #Get the image object
        #Get the size object
        for s in self.conn.list_sizes():
            if flavor == s.id:
                size = s

        for i in self.conn.list_images():
            if self._decode_id("emi", image) == i.id:
                image_obj = i

        return self._format_instance(
            self._create_node(name=name, image=image_obj, size=size,
                ex_keyname=key_name, ex_mincount=str(min_count),
                ex_userdata=userdata))
