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


class MockObjectNotClosedException(Exception):
    pass

class DbConnMock(object):

    class CursorMock(object):

        def __init__(self):
            ''' Set is_open so that we will know if the client code has closed
            the connection '''
            self.is_open = True

        def execute(self, query_str):
            ''' fake execution '''
            pass

        def fetchall(self):
            ''' Return some fake results to play with '''
            return [('OSDC-Adler', 'mgreenway-ldisk', 411320.0, 20566), ('OSDC-Adler', 'mgreenway-ram', 71981.0, 20566L), ('OSDC-Adler', 'mgreenway-vms', 20566, 20566L), ('atwood', 'mgreenway-du', 0.0, 21127L), ('atwood', 'mgreenway-cores', 33403.0, 21127L), ('atwood', 'mgreenway-vms', 33403.0, 21127L), ('OSDC-Adler', 'mgreenway-du', 234452.4, 20566L), ('atwood', 'mgreenway-ldisk', 0.0, 21127L), ('atwood', 'mgreenway-ram', 16701.5, 21127L), ('OSDC-Adler', 'mgreenway-cores', 20566.0, 20566L)]

        def close(self):
            self.is_open = False

        def __del__(self):
            ''' destructor to check that client code has closed the cursor '''
            if self.is_open:
                print "CursorMock object is still open!"
                raise MockObjectNotClosedException


    def __init__(self):
        self.is_open = True

    def cursor(self):
        ''' Return a fake cursor '''
        return self.CursorMock()

    def close(self):
        '''endut!'''
        self.is_open = False

    def __del__(self):
        if self.is_open:
            print "DbConnMock Object is still open!"
            raise MockObjectNotClosedException

