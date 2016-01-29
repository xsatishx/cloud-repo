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
''' OSDC File/Object ID Service '''

import json
import couchdb

from tukey_middleware import local_settings
from tukey_middleware.flask_utils import Unauthorized, FormatError, NotFound

from tukey_middleware.couch import Couch
from .utils import uuid_format

settings = local_settings.ids


def can_create_ids(user):
    ''' Check if the user is allowed to create new ids '''
    #TODO: actually something
    # use a keystone role?
    return True


class IdAcl(object):
    '''"acl": [{"permission": "read", "grantee":
            {"id": "name", "type": "username"}}]
    Possible permissions:
        ["READ", "WRITE", "READ_ACP", "WRITE_ACP", "FULL_CONTROL"] '''

    PERM = "permission"
    GRANTEE = "grantee"
    TYPE = "type"
    ID = "id"

    READ = "read"
    READ_ACP = "read_acp"
    WRITE = "write"
    WRITE_ACP = "write_acp"
    FULL_CONTROL = "full_control"

    USERNAME = "username"
    TENANT_NAME = "tenant_name"

    # special tenants
    ALL_USERS = "AllUsers"
    AUTHENTICATED_USERS = "AuthenticatedUsers"

    def __init__(self, acl):
        perm_types = [self.READ, self.READ_ACP, self.WRITE, self.WRITE_ACP,
                self.FULL_CONTROL]
        grantee_types = [self.USERNAME, self.TENANT_NAME]
        self.perms = {}

        for perm in acl:
            if perm[self.GRANTEE][self.TYPE] not in grantee_types or \
                    perm[self.PERM] not in perm_types:
                raise
            grantee = perm[self.GRANTEE]
            perm_key = "%s:%s" % (grantee[self.TYPE], grantee[self.ID])
            perm_set = self.perms.get(perm_key, set())
            perm_set.add(perm[self.PERM])
            self.perms[perm_key] = perm_set

    def allow(self, permissions, grantee_type, grantee):
        ''' determine is grantee of grantee_type has permissions in this acl
        permissions will be like READ'''

        return self._allow(permissions, grantee_type, grantee) or\
                self._allow(permissions, self.TENANT_NAME, self.ALL_USERS)


    def _allow(self, permission, grantee_type, grantee):
        ''' Check against the internal hash for quick lookup then return if
        specified perms matched or grantee has FULL_CONTROL'''
        perm_key = "%s:%s" % (grantee_type, grantee)
        if perm_key not in self.perms:
            return False
        perms = self.perms[perm_key]
        return permission in perms or self.FULL_CONTROL in perms

    @staticmethod
    def default(username, tenant_name):
        '''return the default permissions for a user registering a new object:
        FULL_CONTROL for their username and tenant'''
        return [{
                IdAcl.PERM: IdAcl.FULL_CONTROL,
                IdAcl.GRANTEE: {
                        IdAcl.TYPE: IdAcl.USERNAME,
                        IdAcl.ID: username
                    }
            },{
                IdAcl.PERM: IdAcl.FULL_CONTROL,
                IdAcl.GRANTEE: {
                        IdAcl.TYPE: IdAcl.TENANT_NAME,
                        IdAcl.ID: tenant_name
                    }
            }]


def valid_record(record):
    '''There can be additional attributes but there needs to be at least
    those specified here. '''
    object_attributes = ["size", "username", "tenant_name", "acl",
            "protocol", "cloud_name", "metadata_server"]
    collection_attributes = ["ids"]
    return (set(object_attributes).issubset(set(record.keys())) or \
            set(collection_attributes).issubset(record.keys())) \
            and IdAcl(record["acl"])


def get_metadata(user, uuid, perm, ignore=None):
    '''Retrun the simple metadata associated with this id if the user making
    this request is permitted to see it'''
    if ignore is None:
        ignore = []

    store = Couch(settings["db_name"])
    try:
        record = store[uuid]
        acl = IdAcl(record["acl"])
        if acl.allow(perm, IdAcl.TENANT_NAME, user.tenant_name()) or \
                 acl.allow(perm, IdAcl.USERNAME, user.username()):
            if "ids" in record:
                collection = store[record["ids"]]
                # check for nested collection for now assume one level of
                # nesting.
                if "ids" in collection[0]:
                    return {"ids":[item["_id"] for item in collection]}
                return [{k: v for k, v in item.items() if k not in ignore}
                        for item in collection]
            return {k: v for k, v in record.items() if k not in ignore}
        else:
            raise Unauthorized()
    except couchdb.ResourceNotFound:
        raise NotFound()



def modify_acl(user, uuid, data, func):
    ''' Helper function to change acl of uuid.  func takes arguments metadata
    of uuid attribute ["acl"] and data["acl"] then set new acl to func's
    return value. '''
    record_str = get_metadata(user, uuid, IdAcl.WRITE_ACP)
    try:
        IdAcl(data["acl"])
        record = json.loads(record_str)
        record["acl"] =  func(record["acl"], data["acl"])
        store = Couch(settings["db_name"])
        store[uuid] = record
    except (KeyError, ValueError):
        raise NotFound()


def register_object(user, record):
    ''' Create a new id for this metadata '''
    if not can_create_ids(user):
        raise Unauthorized("You do not have permission to create new IDs")

    record = format_object(user, record)

    store = Couch(settings["db_name"])
    uuid = store.save(record)
    return uuid


def format_object(user, record):
    ''' From simple object metadata register and return generate UUID '''

    record["username"] = user.username()
    record["tenant_name"] = user.tenant_name()

    if "cloud_name" not in record:
        record["cloud_name"] = local_settings.vm_ip_auth["default"]

    if "metadata_server" not in record:
        #TODO: have default metadata server
        record["metadata_server"] = ""

    if "acl" not in record:
        record["acl"] = IdAcl.default(user.username(), user.tenant_name())

    if not valid_record(record):
        raise FormatError()

    return record


def create_id(user, data, acl=None):
    ''' register objects or collections'''
    try:
        data.keys()
        if "ids" in data:
            data = data["ids"]
            raise AttributeError()
        return register_object(user, data), data
    except AttributeError:
        collection = []
        # each entitty can either be an ID or an JSON object description
        ids = []
        objects = []
        for entity in data:
            uuid = uuid_format(entity)
            if uuid:
                ids.append(uuid)
            else:
                #collection.append(register_object(user, entity))
                objects.append(format_object(user, entity))

        store = Couch(settings["db_name"])
        id_tuples = store.raw_db().update(objects)
        collection = ids + [tup[1] for tup in id_tuples]

        if acl:
            return register_object(user,
                    {"ids": collection, "acl": acl}), collection
        return register_object(user, {"ids": collection}), collection

