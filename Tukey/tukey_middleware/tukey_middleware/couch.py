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
''' Couchdb wrapper wrapper '''

import couchdb
import json
import requests

from .flask_utils import NotFound


class Couch(object):
    '''Implementation of persistant keyvalue store interface with unique
    id generation'''

    def __init__(self, db_name=None, url=None):
        '''url is the url of couchdb like: 'http://localhost:5984/'. Default
        is 'http://localhost:5984/' '''
        self.url = 'http://localhost:5984'
        if url:
            self.couch = couchdb.Server(url=url)
            self.url = url
        else:
            self.couch = couchdb.Server()
        self.db_name = db_name
        if self.db_name and self.db_name not in self.couch:
            raise NotFound("db %s does not exist" % self.db_name)

    def new_id(self):
        ''' Generate and return new id '''
        return self.couch.uuids()[0]

    def _as_documents(self, text):
        '''Deserialize and return the documents'''
        return [item["doc"] for item in json.loads(text)["rows"]]

    def __getitem__(self, key):
        ''' Provides dict interface get '''
        if type(key) is list:
            resp = requests.post("%s/%s/_all_docs?include_docs=true" % (
                    self.url, self.db_name), data=json.dumps({"keys": key}))
            return self._as_documents(resp.text)
        else:
            return self.couch[self.db_name][key]

    def __setitem__(self, key, value):
        ''' Provides dict interface set '''
        self.couch[self.db_name][key] = value

    def save(self, doc):
        ''' Wrapper to couchdb.save() '''
        return self.couch[self.db_name].save(doc)[0]

    def raw_db(self):
        ''' Access the raw couchdb.Server methods '''
        return self.couch[self.db_name]

    def list_all(self):
        ''' List all databases stored in this CouchDB server'''
        resp = requests.get("%s/%s/_all_docs?include_docs=true" % (self.url,
                self.db_name))
        return self._as_documents(resp.text)
