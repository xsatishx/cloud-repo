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

''' Client library for the file ID service and metadata service. '''

import json
import requests
import subprocess
import magic
import xmldict

from .object_info import ObjectInfo, SwiftObject, SshFile, LocalFile, UdpipeFile
from keystoneclient.v2_0.client import Client as KeystoneClient
from swiftclient.client import get_object, get_auth, put_object, put_container, head_object
from tukey_middleware.utils import cache_attr
from utils import uuid_format, SourceInterface
from sys import exit


class HttpException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Client(object):
    ''' OSDC ID Service client.  Use to get basic metadata and links to
    additional data services'''

    USER_AGENT = 'python-osdcclient'

    # TODO:
    # Assumes that the userinfo and metadata services are running on the same
    # USE the check from other thing
    # set these in local settings
    # server as the ID server
    USER_INFO_PATH = "/user_info/v0/"
    METADATA_PATH = "/metadata/v0/"
    ID_PATH = "/ids/v0/"

    def __init__(self, id_service, os_username=None, os_tenant_name=None,
            os_password=None, os_auth_url=None, os_auth_token=None,
            interface=None, remote_user=None, id_service_auth_token=None,
            swift_auth_url=None, swift_tenant=None, swift_username=None,
            swift_password=None):
        ''' id_service is a full url of the id service to use. The remaining
        parameters are OpenStack Auth creds that are optional. VM IP Auth will
        be used if it applies'''

        self.id_service = id_service.strip("/")

        self.auth_token = os_auth_token
        self._username = os_username
        self._tenant_name = os_tenant_name
        self.interface = interface
        self.remote_user = remote_user
        self.os_auth_url = os_auth_url

        self._password = os_password

        self.swift_auth_url = swift_auth_url if swift_auth_url else os_auth_url

        self._swift_tenant = swift_tenant
        self._swift_username = swift_username
        self._swift_password = swift_password

        if os_username and os_tenant_name and os_password:
            if not os_auth_token:
                auth_client = KeystoneClient(username=os_username,
                    tenant_name=os_tenant_name, password=os_password,
                    auth_url=os_auth_url)
                self.auth_token = auth_client.auth_token

        self.headers = {
            "User-Agent": self.USER_AGENT,
            "content-type": "application/json"
            }

        if self.auth_token:
            self.headers["x-auth-token"] = self.auth_token
            self.headers["x-auth-user-name"] = self._username
            self.headers["x-auth-tenant-name"] = self.tenant_name
        if id_service_auth_token:
            self.headers["x-id-auth-token"] = id_service_auth_token

    @property
    def swift_tenant(self):
        if self._swift_tenant is None:
            return self.tenant_name
        return self._swift_tenant

    @property
    def swift_username(self):
        if self._swift_username is None:
            return self.username
        return self._swift_username

    @property
    def swift_password(self):
        if self._swift_password is None:
            return self.password
        return self._swift_password

    @property
    def id_auth_token(self):
        return self.headers["x-id-auth-token"]

    @cache_attr
    def _user_info(self):
        ''' GET all of the user info so we only need one request '''
        user_str = self.http_get("%s%s" % (self.id_service,
                self.USER_INFO_PATH)).text
        return json.loads(user_str)

    @cache_attr
    def get_cloud_info(self, cloud):
        ''' Query the metadata service for infromation about cloud "cloud"'''
        user_str = self.http_get("%s%sclouds/%s" % (self.id_service,
                self.METADATA_PATH, cloud)).text
        return json.loads(user_str)

    def upload_metadata(self, project, raw_metadata):
        ''' upload xml or json to the metadata server'''
        headers = {}
        headers.update(self.headers)
        try:
            file_type = magic.from_buffer(raw_metadata[:200])
            if file_type == "XML document text":
            #headers["content-type"] = "xml"
                metadata = xmldict.xml_to_dict(raw_metadata)["ResultSet"]["Result"]
        except Exception:
            metadata = raw_metadata
        #else:
        #    metadata = json.loads(raw_metadata)

        path = "%s%s%s" % (self.id_service, self.METADATA_PATH, project)

        with SourceInterface(self.interface):
            chunk_size = 1024
            ids = []
            for start in range(0, len(metadata), chunk_size):
                response = requests.put(path, data=json.dumps(
                        metadata[start: start + chunk_size]), headers=headers)
                if "x-id-auth-token" in response.headers:
                    self.headers["x-id-auth-token"] = response.headers[
                            "x-id-auth-token"]
                ids.append(response.text)
            return ids

    def get_projects(self, write=False):
        '''If write list the projects this user can write to else list the
        projects this user can read.  Returns a list of dictionaries with three
        attributes id, name and description'''
        resp = self.http_get("%s%s%s" % (self.id_service, self.METADATA_PATH,
                "?write=True" if write else ""))
        return json.loads(resp.text)

    @property
    @cache_attr
    def password(self):
        ''' if the client is using vm ip auth then fetch the password'''
        return self._user_info()["password"]

    @property
    @cache_attr
    def username(self):
        ''' if the client is using vm ip auth then fetch the username'''
        return self._user_info()["username"]

    @property
    @cache_attr
    def tenant_name(self):
        ''' if the client is using vm ip auth then fetch the tenant_name'''
        return self._user_info()["tenant_name"]

    @property
    @cache_attr
    def cloud_name(self):
        '''name of the cloud this user is on'''
        #version issue
        try:
            return self._user_info()["cloud_name"]
        except Exception:
            return "sullivan"

    def http_get(self, path):
        ''' GET request with source ip set if defined for self '''
        with SourceInterface(self.interface):
            response = requests.get(path, headers=self.headers)
            if response.status_code >= 300:
                # sparta
                raise HttpException(response.status_code)

            if "x-id-auth-token" in response.headers:
                self.headers["x-id-auth-token"] = response.headers[
                        "x-id-auth-token"]
            return response

    def http_post(self, path, data):
        ''' POST request with source ip set if defined for self '''
        with SourceInterface(self.interface):
            response = requests.post(path, data=data, headers=self.headers)
            if "x-id-auth-token" in response.headers:
                self.headers["x-id-auth-token"] = response.headers[
                        "x-id-auth-token"]
            return response

    def object_info_factory(self, object_info):
        ''' Given dictionary object_info returns appropriate object with
        class derived from ObjectInfo chosen from "protcol" entry in
        object_info '''
        if object_info["protocol"] == "swift":
            return SwiftObject(object_info, self.swift_tenant,
                    self.swift_username, self.swift_password)
        elif object_info["protocol"] == "ssh":
            if object_info["cloud_name"] == self.cloud_name:
                return LocalFile(object_info)
            return SshFile(object_info, remote_user=self.remote_user)
        elif object_info["protocol"] == "udpipe":
            return UdpipeFile(object_info, self.get_cloud_info,
                    remote_user=self.remote_user)
        else:
            return ObjectInfo(object_info)

    def update(self, uuid, attributes):
        ''' update attributes for an id where attributes is a dictionary'''

        if not uuid_format(uuid):
            raise TypeError

        return self.http_post("%s%s%s" % (self.id_service, self.ID_PATH,
                uuid), json.dumps(attributes)).text

    def get_id_info(self, uuid, as_ids=False):
        ''' Given a uuid return that files metadata as a uuid '''

        if not uuid_format(uuid):
            raise TypeError

        resp = self.http_get("%s%s%s" % (self.id_service, self.ID_PATH, uuid))

        if resp.status_code != 200:
            return {}

        object_info = json.loads(resp.text)

        if "ids" in object_info:
            if as_ids:
                return [obj for obj in object_info["ids"]]
            return [self.get_id_info(obj) for obj in object_info["ids"]]

        if type(object_info) is list:
            objects = [self.object_info_factory(obj) for obj in object_info]
            return objects

        return self.object_info_factory(object_info)

    def register(self, filepath, protocol, extra=None):
        ''' Reigster filepath and protocol with the ID service.  If there is
        an interface specified use that.  The interface parameter is useful
        when testing on the same host as the ID service and you want to use
        the VM IP Auth '''

        if protocol == "swift":
            path_parts = filepath.split("/")
            object_name = path_parts.pop()
            url =  "%s//%s/%s/%s" % ((path_parts[0],) + tuple(path_parts[2:5]))
            container = "/".join(path_parts[5:])
            if self.swift_auth_url == self.os_auth_url:
                token = self.auth_token
            else:
                _, token = get_auth(self.swift_auth_url, "%s:%s" % (
                        self.swift_tenant, self.swift_username),
                        self.swift_password)

            size = head_object(url, token, container,
                    object_name)["content-length"]

            swift = {"swift": {
                    "url": url,
                    "container": container,
                    "object": object_name,
                    "auth_url": self.swift_auth_url
                    },
                    "filesize": size
                }
            if extra:
                extra.update(swift)
            else:
                extra = swift

        record = {"filepath": filepath, "protocol": protocol}
        if extra:
            record.update(extra)

        return self.http_post("%s%s" % (self.id_service, self.ID_PATH),
                json.dumps(record)).text

    def register_collection(self, collection, extra=None):
        ''' Reigster this list as a collection.  The list can either contain
        ids or dictionaries to create ids for. '''
        record = {"ids": json.loads(collection)}
        if extra:
            record.update(extra)
        return self.http_post("%s%s" % (self.id_service, self.ID_PATH),
                json.dumps(record)).text

    def upload(self, uuid):
        ''' Upload a file or files whose info pointed to by this uuid '''

        file_info = self.get_id_info(uuid)

        # see if file_info is an ObjectInfo
        try:
            file_info.upload()
        except AttributeError:
            # maybe its a list of ObjectInfos
            for info in file_info:
                info.upload()

