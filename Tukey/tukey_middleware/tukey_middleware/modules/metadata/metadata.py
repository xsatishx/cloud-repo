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

from tukey_middleware.couch import Couch
from tukey_middleware.flask_utils import Unauthorized
from tukey_middleware.modules.ids.object_info import UdpipeFile, LocalFile
from tukey_middleware.modules.ids.ids import IdAcl

class Metadata(object):
    def __init__(self, raw_metadata, filetype, metadata_service, project_name,
        cloud, store):
        ''' take raw metadata '''
        self._metadata = raw_metadata
        self.project_name = project_name
        self.filetype = filetype
        self.store = store(project_name)
        self.metadata_service = metadata_service
        self.cloud = cloud

    def num_files(self, metdata_entry):
        ''' How many files are referenced by this metadata entry.  This is
        used to find how many ids grab when formatting metadata'''
        # a reasonable default
        return 1

    def format_metadata(self, metadata_entry, ids):
        ''' Format the entry so that it is ready to go into the metadata
        service. Do nothing'''
        metadata_entry["file_id"] = ids[0]
        return metadata_entry

    def get_files(self, metadata_entry):
        ''' get information about the files referenced by this entry'''
        return None

    def ingest(self, id_function, file_acl=None):
        ''' Given raw metadata as a list of dictionaries iterate through it
        creating ids for each file referenced then insert the ids into the
        metadata.  Then upload the metadata and return the list of ids created
        '''

        files = [f for row in self._metadata for f in self.get_files(row)]

        if file_acl is None:
            file_acl = [{
                "grantee": {
                    "type": "tenant_name",
                    "id": "AllUsers"
                },
                "permission": "read"
                }]

        collection_id, ids = id_function(files, acl=file_acl)

        metadata = []
        index = 0
        for row in self._metadata:
            metadata.append(self.format_metadata(row, ids[index:]))
            index += self.num_files(row)

        self.store.raw_db().update(metadata)
        return collection_id


class TcgaMetadata(Metadata):
    ''' class for handling tcga format metadata'''

    def get_files(self, row):
        return [self.filetype.create(file_info["filename"],
                    size=file_info["filesize"],
                    cloud=self.cloud,
                    metadata_server=self.metadata_service)
                for file_info in row["files"]["file"]]

    def num_files(self, row):
        return len(row["files"]["file"])

    def format_metadata(self, row, ids):
        for index in range(self.num_files(row)):
            row["files"]["file"][index]["id"] = ids[index]
        return row


class ThousandGenomeMetadata(Metadata):
    ''' class for handling 1000genome specific metadata '''

    _file_types = None

    @property
    def file_types(self):
        if self.file_types is None:
            if "BAM FILE" in self._metadata[0]:
                self._file_types = ["BAM FILE", "BAI FILE", "BAS FILE"]
            elif "FASTQ_FILE" in self._metadata[0]:
                self._file_types = ["FASTQ_FILE", "PAIRED_FASTQ"]
        return self._file_types

    def has_file_type(self, entry):
        return entry and not entry.isspace()

    def num_files(self, row):
        row_count = 0
        for file_type in self.file_types:
            if self.has_file_type(row[file_type]):
                row_count += 1
        return row_count

    def get_files(self, row):
        return [self.filetype.create(
                "/glusterfs/osdc_public_data/1000genomes/ftp/%s"
                % row[file_type], acl=[{
                   "grantee": {
                       "type": "tenant_name",
                       "id": "AllUsers"
                   },
                   "permission": "read"
                }],
                cloud=self.cloud) for file_type in self.file_types
                if self.has_file_type(row[file_type])]

    def format_metadata(self, row, ids):
        for index, file_type in enumerate(self.file_types):
            if self.has_file_type(row[file_type]):
                row["%s id" % file_type] = ids[index]
        return row

def _file_format(file_format):
    ''' file_format is a string then return the class that string refers to'''

    if file_format == "udpipe":
        return UdpipeFile
    elif file_format == "local":
        return LocalFile


def update_metadata(user, project_name, raw_metadata, metadata_service,
        create_id):
    ''' The project_name, raw_metadata as dictionary, metadata_service url and
    create_id is a function that takes a list of ids and an acl'''

    for prj in list_projects(user, write=True, ignore=[]):
        if prj["id"] == project_name:
            project_info = prj
            break
    else:
        raise Unauthorized(
                "You do not have permission to write to this project")

    if project_info["metadata_format"] == "tcga":
        project_class = TcgaMetadata
    elif project_info["metadata_format"] == ["thousandgenomes"]:
        project_class = ThousandGenomeMetadata

    project = project_class(raw_metadata,
            _file_format(project_info["file_format"]), metadata_service,
            project_name, project_info["cloud"], Couch)

    return project.ingest(create_id, file_acl=project_info["file_acl"])


def list_projects(user, write=None, ignore=None):
    ''' Return the list of projects this user can see'''

    if ignore is None:
        ignore = ["_rev", "acl", "file_protocol", "metadata_format", "cloud",
                "file_acl"]

    store = Couch(db_name="project")
    projects = store.list_all()

    perm = IdAcl.WRITE if write else IdAcl.READ

    visible = []
    for record in projects:
        acl = IdAcl(record["acl"])
        if acl.allow(perm, IdAcl.TENANT_NAME, user.tenant_name()) or \
                acl.allow(perm, IdAcl.USERNAME, user.username()):
            visible.append(record)

    return  [{k.strip("_"): v for k, v in i.items() if k not in ignore}
            for i in visible]
