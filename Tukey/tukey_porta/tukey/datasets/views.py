from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse,Http404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from .models import DataSet, Key, KeyValue
from .forms import UpdateDataSetForm, AddDataSetForm
from datetime import datetime, timedelta
import uuid,json
from settings import METADATA_DB, SIGNPOST_URL 
from psqlgraph import PsqlGraphDriver,Node
from signpostclient import SignpostClient

#This needs work -- a lot of assumptions, lack of error checking and general ugliness

osdc_prefix = 'osdc'

#does not support time zones -- for now leave it up to the submission scripts to put in UTC.
time_format='%Y-%m-%d %H:%M:%S'

valid_keys = ['source', 'source_url', 'description', 'short_description', 'keyword', 'size', 'modified', 'license', 'osdc_location', 'osdc_folder', 'osdc_hs_location', 'osdc_hs_folder']

pg_driver = PsqlGraphDriver(METADATA_DB['HOST'],METADATA_DB['USER'],
                METADATA_DB['PASSWORD'],METADATA_DB['NAME'])

signpost = SignpostClient(SIGNPOST_URL,version='v0')

def init_keys():
    for key in valid_keys:
        k = Key(key_name=key, public=True)
        k.save()

def add_dataset(title, prefix):
    key = str(uuid.uuid4())
    slug = slugify(title)

    d = DataSet(key=key, prefix=prefix, title=title, slug=slug)
    d.save()

    return d


def add_keyvalue(d, key_name_str, v):
    k = Key.objects.get(key_name=key_name_str)
    #should some validation be done? -- just going to check for modified so that store it in time_format
    if type(v) is datetime:
        v = v.strftime(time_format)

    key_value = KeyValue(dataset=d, key=k, value=v)
    key_value.save()

#expects ids and values
#again, probably can be done better, need to filter updated fields on the form level somehow?
def update_keyvalues(keyvalues_id_value):
    for (key_id, value) in keyvalues_id_value:
        k = KeyValue.objects.get(id=key_id)
        if type(value) is datetime:
            value = value.strftime(time_format)

        if value != k.value:
            k.value = value
            k.save()


def datasets_list_index(request, keyword_filter=None):
    datasets = []
    with pg_driver.session_scope():
        query = pg_driver.nodes()

    if keyword_filter is not None:
        keyword = query.labels('keyword').props({'value':keyword_filter}).first()
        nodes = []
        for edge in keyword.edges_in:
            nodes.append(edge.src)
    else:
        nodes = query.labels('dataset').order_by(Node.properties['title'].astext).all()
       
    for node in nodes:
        doc = signpost.get(node.node_id)
        result=node.properties
        result['keyword']=[]
        result['identifiers']=doc.identifiers
        for edge in node.edges_out:
            result['keyword'].append(edge.dst['value'])
        datasets.append(result)
    return render_to_response('datasets/datasets_list_index.html', {'keyword_filter':keyword_filter,'datasets' : (datasets)}, context_instance=RequestContext(request))

def dataset_detail(request, dataset_id):
    with pg_driver.session_scope():
        dataset = pg_driver.nodes().labels('dataset').props({'slug':dataset_id}).first()
        
        dataset_dict = {}
        if dataset:
            dataset_dict = dataset.properties
            doc = signpost.get(dataset.node_id)
            dataset_dict['identifiers'] = doc.identifiers
            dataset_dict['keyword']=[]
            for edge in dataset.edges_out:
                dataset_dict['keyword'].append(edge.dst['value']) 
            return render_to_response('datasets/dataset_detail.html', {'dataset': dataset_dict}, context_instance=RequestContext(request))
        else:
            raise Http404("Dataset does not exist")
