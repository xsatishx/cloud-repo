import os,sys


sys.path.append('/var/www/tukey/tukey-portal/openstack_dashboard')
sys.path.append('/var/www/tukey/tukey-portal')
import settings
from psqlgraph import PsqlGraphDriver, Node, Edge
from signpostclient import SignpostClient
import urlparse
import binascii,json

required_field = ['date_collected','description','title','grant_or_support_source_and_id',
    'investigator_affiliation','date_updated','date_uploaded','investigator_name','availability_type',
    'acknowledgements','publications','size']

ROOT_URL = 'https://www.opensciencedatacloud.org/publicdata/'

class MetadataImporter(object):
    def __init__(self,metadata={}):
        self.metadata = metadata
        self.driver=PsqlGraphDriver(settings.METADATA_DB['HOST'],
            settings.METADATA_DB['USER'],settings.METADATA_DB['PASSWORD'],
            settings.METADATA_DB['NAME'])
        self.signpost = SignpostClient(settings.SIGNPOST_URL,version='v0')

    def find_props(self,props):
        return self.driver.nodes().labels('dataset').props(props).count()>0
        

    def validate_metadata(self):
        for key in required_field:
            if key not in self.metadata:
                print "%s not provided" % key
                return False
        if 'short_description' not in self.metadata:
            print 'short description not provided, use description as short description'
            self.metadata['short_description']= self.metadata['description']
            
        if 'slug' not in self.metadata:
            self.metadata['slug'] = "-".join(self.metadata['title'].lower().split(" ")) 
     
        if 'availability_mechanism' not in self.metadata:
            self.metadata['availability_mechanism']='udr, rsync' 

        if self.find_props({'slug':self.metadata['slug']}):
            print 'slug "%s" exist before, please change a slug' % self.metadata['slug']
            return False
        if 'url' not in self.metadata or self.metadata['url'].strip()=='':
            self.metadata['url'] = urlparse.urljoin(ROOT_URL,self.metadata['slug'])
        return True

    def search_identifier(self,ark):
        while self.signpost.search(ark):
            new_ark = 'ark:/31807/osdc-' + binascii.b2a_hex(os.urandom(8))
            print '%s exists, create new ark %s' % (ark,new_ark)
            ark = new_ark
        return ark.split(":")[-1]
    
    def import_keywords(self):
        nodes = []
        for keyword in self.metadata['keywords'].split(","):
            keyword=keyword.strip()
            node = self.driver.nodes().labels('keyword').props({'value':keyword}).first()
            if not node:
                doc = self.signpost.create()
                node = Node(label='keyword',node_id = doc.did,properties = {'value':keyword})
                self.driver.node_merge(node=node)
                print 'create new keyword %s' % keyword
            nodes.append(node)
        return nodes
        
    def import_metadata(self):
        with self.driver.session_scope():
            if not self.validate_metadata():
                return
            
            doc = self.signpost.create()
            doc.urls=[self.metadata['url']]
            doc.identifiers = {
                'ark':self.search_identifier('ark:/31807/osdc-'+doc.did.split('-')[0])
            }
            doc.patch()
            properties = self.metadata.copy()
            del properties['url']
            del properties['keywords']
            
            node = Node(node_id=doc.did,label='dataset',properties=properties)
            self.driver.node_merge(node=node)
            keyword_nodes = self.import_keywords()
            for keyword in keyword_nodes:
                self.driver.edge_insert(Edge(node.node_id,keyword.node_id,'member_of'))
            print 'metadata %s created' % doc.did
   
    def delete_metadata(self,did):
        with self.driver.session_scope():
            node = self.driver.nodes().ids(did).first()
            if node:
                self.driver.node_delete(node_id=did)
            doc = self.signpost.get(did)
            doc.delete()

if __name__ == "__main__":
    if len(sys.argv)==3:
        if sys.argv[1] == 'create':
            metadata = json.load(open(sys.argv[2],'r'))
            importer = MetadataImporter(metadata)
            importer.import_metadata()
            exit()
        elif sys.argv[1] == 'delete':
            print 'delete %s' % sys.argv[2]
            importer = MetadataImporter()
            importer.delete_metadata(sys.argv[2])
            exit()
    print '''
        To create a new metadata, use "./import_metadata create metadata.json".
        To delete a metadata use "import_metadata delete $did"
'''
