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

''' Classes for managing Object/File info stored in the ID Service '''

import fractions
import multiprocessing
import os
import subprocess
import time
import threading

from swiftclient.client import get_object, get_auth, put_object, put_container


#def get_object_info()

class ObjectInfo(object):
    '''
    so clients do not have to deal with dicts and JSON.
    '''

    def __init__(self, info):
        ''' Info is a dict with the limited metadata attributes stored
        in the id service.'''
        self.info = info

    @property
    def path(self):
        ''' a file system path'''
        return self.info.get("filepath", self.info.get("path", None))

    @property
    def id(self):
        ''' the file id '''
        return self.info["_id"]

    @property
    def size(self):
        ''' Size in bytes of the file data '''
        return self.info["filesize"]

    @property
    def protocol(self):
        ''' The access protocol, S3, Swift, SSH, UDR ...'''
        return self.info["protocol"]

    @property
    def host(self):
        ''' The hostname of the service where the object lives'''
        #TODO: this should actaully be a lookup from the cloud name
        # given a cloud name a service will tell us the url
        return  "%s.opensciencedatacloud.org" % self.info["cloud_name"]

    @property
    def cloud(self):
        ''' Cloud name where object lives: Sullivan, Atwood ...'''
        return self.info["cloud_name"]

    @property
    def name(self):
        ''' Human readable name for this file'''
        return self.info["filepath"].split("/")[-1]


class SwiftObject(ObjectInfo):
    ''' If the protocol is Swift ObjectInfo '''

    # BIG TODO: pass the token in from outside so we only have to do the
    # auth once!
    # Token expiration. we should be able to fetch this from
    # keystone/swift but if not this is the default
    # TODO: set to reasonable value
    TOKEN_EXPIRATION = 0

    def __init__(self, info, tenant_name, username, password, token=None,
            url=None):

        super(SwiftObject, self).__init__(info)

        self.swift_info = self.info["swift"]
        self.tenant_name = tenant_name
        self.username = username
        self.password = password

        if token and url:
            self._token, self._url = token, url
        else:
            self._token, self._url = None, None


    def _get_auth(self):
        ''' swift authentication '''
        self._url, self._token = get_auth(self.swift_info["auth_url"],
                "%s:%s" % (self.tenant_name, self.username),
                self.password)

    @property
    def token(self):
        ''' don't get the token unless we need it'''
        if self._token is None:
            self._get_auth()
        return self._token

    @property
    def url(self):
        ''' don't get the url unless we need it'''
        if self._url is None:
            self._get_auth()
        return self._url

    def read(self, read_bytes=None, offset=None):
        ''' Read the object from swift if not read_bytes read the whole
        object'''
        headers = {}
        if read_bytes is not None and offset is not None:
            headers["Range"] = "bytes=%s-%s" % (offset, offset + read_bytes)

        return get_object(self.swift_info["url"], self.token,
               self.swift_info["container"], self.swift_info["object"],
               headers=headers)[1][:read_bytes]

    def ingest(self):
        ''' Upload a file when creating an id, generally used with swift'''

        put_container(self.url, self.token, self.swift_info["container"])

        put_object(self.url, token=self.token,
                container=self.swift_info["container"],
                name=self.swift_info["object"], contents=open(self.path))

    @property
    def name(self):
        ''' The object name to be used as human readable file name'''
        return self.swift_info["object"]


    @staticmethod
    def create(url, container, object_name, size=None,
            ingestion_status="ingested", metadata_server=None):
        ''' Format a dictionary with the required format for a swift file id'''
        return {
            "size": size,
            "protocol": "swift",
            "filepath": "%s/%s/%s" % (url, container, object_name),
            "metadata_server": metadata_server,
            "ingestion_status": ingestion_status,
            "swift": {
                "container": container,
                "object_name": object_name,
                "url": url
            }
        }


class SshFile(ObjectInfo):
    ''' Simple fetching using ssh '''

    def __init__(self, info, remote_user=None):

        self.login_name = remote_user

        self.logger = object()

        def debug(*args, **kwargs):
            ''' in case the outside world doesn't assign'''
            print args, kwargs

        self.logger.debug = debug

        super(SshFile, self).__init__(info)


    def write(self, write_buffer=None, offset=None):
        ''' write using dd over ssh '''

        self.logger.debug("we are in the read function")
        ssh = "ssh -l %s" % self.login_name if self.login_name else "ssh"

        eof = "e3cb5b605ae611e3949a0800200c9a66veryunlikely"
        here_file = "2>&1 <<'%s' \n%s\n%s\n" % (eof, write_buffer, eof)

        if offset is not None and offset != 0:
            dd_cmd = 'dd of=%s bs=1 seek=%s count=%s %s' % (self.path, offset,
                    len(write_buffer), here_file)
        else:
            dd_cmd = 'dd of=%s bs=1 count=%s %s' % (self.path,
                    len(write_buffer), here_file)

        cmd = '%s %s "%s" | sed -r \'$!d;s/([0-9]+).*/\\1/g\'' % (ssh,
                self.host, dd_cmd)
        self.logger.debug("cmd is %s", cmd)

        try:
            output = subprocess.check_output(cmd, shell=True)
            self.logger.debug("output is %s", output)
            return output
        except subprocess.CalledProcessError as e:
            return str(e) + "\n"


    def read(self, read_bytes=None, offset=None):
        ''' read using dd over ssh '''

        ssh = "ssh -l %s" % self.login_name if self.login_name else "ssh"

        if offset is not None and offset != 0:
            gcd = fractions.gcd(offset, read_bytes)
            if gcd == 1:
                dd_cmd = 'dd if=%s bs=%s skip=1 count=%s' % (self.path, offset,
                    read_bytes/offset + 1)
            else:
                dd_cmd = 'dd if=%s bs=%s skip=%s count=%s' % (self.path, gcd,
                    offset/gcd, read_bytes/gcd)

        elif read_bytes:
            self.logger.debug("setting read_byte stuff for %s bytes", read_bytes)
            dd_cmd = 'dd if=%s bs=%s count=1' % (self.path, read_bytes)

        else:
            dd_cmd = 'dd if=%s' % (self.path)


        cmd = '%s %s "%s 2>/dev/null"' % (ssh, self.host, dd_cmd)
        self.logger.debug("cmd is %s", cmd)

        try:
            return subprocess.check_output(cmd, shell=True)[:read_bytes]
        except subprocess.CalledProcessError as e:
            return str(e) + "\n"


class LocalFile(ObjectInfo):

    def __init__(self, info):

        self.at = 0
        self.lock = threading.Lock()
        super(LocalFile, self).__init__(info)

    def close(self):
        self.fid.close()

    def _seek_and_read(self, read_bytes, offset):
        with self.lock:
            if self.at != offset:
                self.fid.seek(offset)
                self.at = self.fid.tell()
            else:
                self.at += read_bytes
            return self.fid.read(read_bytes)

    def read(self, read_bytes=None, offset=None):
        try:
            return self._seek_and_read(read_bytes, offset)
        except AttributeError as e:
            if str(e.message).endswith("has no attribute 'fid'"):
                self.fid = file(self.path)
                self.at = 0
                return self._seek_and_read(read_bytes, offset)
            else:
                raise

    @staticmethod
    def create(filepath, size=None, ingestion_status="ingested",
            metadata_server=None, acl=None):
        ''' Format a dictionary with the required format for a udpipe file id'''
        return {
            "size": size,
            "protocol": "ssh",
            "acl": acl,
            "filepath": filepath,
            "metadata_server": metadata_server,
            "ingestion_status": ingestion_status
        }



class UdpipeFile(ObjectInfo):
    ''' Information needed to send file over udpipe '''

    def __init__(self, info, get_cloud_info, remote_user=None):

        self.get_cloud_info = get_cloud_info
        self.remote_user = remote_user
        super(UdpipeFile, self).__init__(info)
        self.udpipe_info = self.info["udpipe"]
        self.dry_run = False

    def popen(self, cmd, shell=True):
        '''wrapper for subprocess.Popen'''
        if self.dry_run:
            print cmd

            class FakeProc():
                ''' Fake class for popening'''
                def wait(self):
                    pass
            return FakeProc()
        else:
            return subprocess.Popen(cmd, shell=shell)

    def ingest(self):
        ''' upload to the destination server using udpip '''

        # this can get set at the client
        password = self.udpipe_info["password"]
        cloud_info = self.get_cloud_info(self.udpipe_info["destination"])
        host = cloud_info["udpipe"]["host"]

        if self.remote_user:
            destination = "%s@%s" % (self.remote_user,
                    host)
        else:
            destination = host
        port = self.udpipe_info["port"]
        local_path = self.udpipe_info["local_path"]
        remote_cores = cloud_info["udpipe"]["cores"]

        threads = min(remote_cores, multiprocessing.cpu_count())

        udpipe_cmd = "ssh %s '" + cloud_info["udpipe"]["command"] + "'"
        remote_cmd = udpipe_cmd % (destination, threads,
                password, port, self.path)

        local_cmd = "up -n %s -p %s %s %s < %s " % (threads, password,
                host, port, local_path)

        print "Running ", remote_cmd
        remote_proc = self.popen(remote_cmd, shell=True)

        time.sleep(3)

        print "Running ", local_cmd
        local_proc = self.popen(local_cmd, shell=True)

        local_proc.wait()
        remote_proc.wait()
        print "done!"

    @staticmethod
    def create(filepath, cloud=None, size=None,
            ingestion_status="not ingested", metadata_server=None,
            source_path=None, password=os.urandom(32).encode("hex"),
            port=9000):
        ''' Format a dictionary with the required format for a udpipe file id'''
        return {
            "size": size,
            "protocol": "udpipe",
            "metadata_server": metadata_server,
            "udpipe": {
                "destination": cloud,
                "port": port,
                "local_path": source_path,
                "filepath": filepath,
                "password": password,
                "ingestion_status": ingestion_status
            }
        }


class Ascp(ObjectInfo):
    ''' Information needed to send file over udpipe '''

    def __init__(self, info, get_cloud_info, remote_user=None):

        self.get_cloud_info = get_cloud_info
        self.remote_user = remote_user
        super(Ascp, self).__init__(info)
        self.ascp = self.info["ascp"]

    def ingest(self):
        ''' upload to the destination server using udpip '''

        # this can get set at the client
        cloud_info = self.get_cloud_info(self.ascp["destination"])
        host = cloud_info["ascp"]["host"]

    @staticmethod
    def create(filepath, cloud=None, size=None,
            ingestion_status="not ingested", metadata_server=None,
            private_key=None, flow_control=None, maximum_bandwidth=None,
            source_path=None):
        ''' Format a dictionary with the required format for a udpipe file id'''
        return {
            "size": size,
            "protocol": "aspera",
            "metadata_server": metadata_server,
            "ascp": {
                "ingestion_status": ingestion_status,
                "private_key": private_key,
                "flow_control": flow_control,
                "maximum_bandwidth": maximum_bandwidth,
                "destination": cloud,
                "source_path": source_path,
                "filepath": filepath
            },
        }

