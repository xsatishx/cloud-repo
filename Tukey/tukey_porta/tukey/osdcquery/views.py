import os, random, string

from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import urlencode
from horizon.decorators import require_auth
from horizon import tables

from .forms import OsdcQueryForm
from .forms import QueryFields
from .models import TcgaMetadata, NameNum

from osdcquery.osdcquery.query import ESQuery, ESQueryMetadata, CDBQuery
from osdcquery.osdcquery.util import get_class
from osdcquery.osdcquery.fs_handler import UnixFsHandler
from osdcquery.osdcquery.links import TcgaLinks
from osdcquery.osdcquery.config import tcga

import pyelasticsearch

#please forgive me.
query_url = tcga.es_url
query_index = tcga.es_index
query_doc_type = tcga.es_doc_type

cdb_url = tcga.cdb_url
cdb_osdc = tcga.cdb_osdc
cdb_cghub = tcga.cdb_cghub
cdb_query = tcga.cdb_query
cdb_query_username = tcga.cdb_query_username
cdb_query_password = tcga.cdb_query_password

old_dir = tcga.target_dir
new_dir = tcga.link_dir

cdbq = CDBQuery(cdb_url, cdb_osdc, cdb_query, cdb_query_username, cdb_query_password)

sample_types = {
    "01" : "Primary Solid Tumor",
    "02" : "Recurrent Solid Tumor", 
    "03" : "Primary Blood Derived Cancer - Peripheral Blood",
    "04" : "Recurrent Blood Derived Cancer - Bone Marrow",
    "05" : "Additional - New Primary",
    "06" : "Metastatic",
    "07" : "Additional Metastatic",
    "08" : "Human Tumor Original Cells",
    "09" : "Primary Blood Derived Cancer - Bone Marrow",
    "10" : "Blood Derived Normal",
    "11" : "Solid Tissue Normal",
    "12" : "Buccal Cell Normal",
    "13" : "EBV Immortalized Normal",
    "14" : "Bone Marrow Normal",
    "20" : "Control Analyte",
    "40" : "Recurrent Blood Derived Cancer - Peripheral Blood",
    "50" : "Cell Lines",
    "60" : "Primary Xenograft Tissue",
    "61" : "Cell Line Derived Xenograft Tissue",
}

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

class QueryAction(tables.Action):
    name = "Launch Instance with Selected Result"
    #url = "horizon:project:instances:launch"
    #classes = ("btn-launch", "ajax-modal")

    def handle(self, table, request, obj_ids):
        manifest = cdbq.get_manifest(table.manifest_id)
        for result in manifest["results"]:
            if result not in obj_ids:
                manifest["results"][result]["reason"] = "user_removed"

        cdbq.update_manifest(table.manifest_id, manifest)

        cloud = "tcga"

        rest_url = "?".join([urlresolvers.reverse(
                "horizon:project:instances:launch"),
                urlencode(
                    #{"cloud": cloud.capitalize(),
                    {"cloud": cloud.upper(),
                    "customization_script": ('''#!/bin/bash
if [ `whoami` != "%s" ]
then
  exit 1
fi
source /glusterfs/data/apps/osdcquery/.venv/bin/activate
cd /glusterfs/data/apps/osdcquery
python -m osdcquery.osdcquery -c osdcquery.config.tcga -a %s 2> /tmp/osdcquery-out
echo "done query" > /tmp/osdcquery-done
''') % (request.user.username, table.manifest_id) })])

        return HttpResponseRedirect(rest_url)

class TcgaTable(tables.DataTable):
    disease_abbr = tables.Column("disease_abbr", verbose_name = "Disease")
    center_name = tables.Column("center_name", verbose_name = "Center")
    library_strategy = tables.Column("library_strategy", verbose_name="Run Type")
    #platform = tables.Column("platform", verbose_name="Platform")
    sample_name = tables.Column("sample_name", verbose_name="Sample Type")
    last_modified = tables.Column("last_modified", verbose_name="Last Modified")
    #upload_date = tables.Column("upload_date", verbose_name="Uploaded")    
    state = tables.Column("state", verbose_name="State")
    file_size = tables.Column("total_filesize", verbose_name="File Size")
    analysis_id = tables.Column("analysis_id", verbose_name = "Analysis ID")

    manifest_id = None
    query_name = None
    generated_query = None

    class Meta:
        name = "Query Results"
        table_actions = ( QueryAction, )

class TcgaTableView(tables.DataTableView):
    table_class = TcgaTable
    template_name = "osdcquery/results.html"

    def get_data(self):
        query_name = self.kwargs["query_name"]
        print("query_name %s" % query_name)
        query_string = self.kwargs["query"]
        print("query_string: %s" % query_string)
        top_dir = os.path.join(self.kwargs["top_dir"], query_name)
        print("top_dir: %s" % top_dir)

        #top_dir = os.path.join(new_dir, query_name)
        data_dir = os.path.join(top_dir, "data")

        #So broken/silly, please ignore this
        fs_handler = UnixFsHandler()
        dir_builder = TcgaLinks(old_dir, data_dir)

        esq = ESQuery(query_url, query_string, query_name, query_index, query_doc_type)

        query_results = esq.perform_query()
        cdbq.get_status(query_results)
        esq_meta = ESQueryMetadata(dir_builder, fs_handler, top_dir, old_dir, esq, cdbq, self.request.user.username)
        self.get_table().manifest_id = cdbq.register_manifest(esq_meta.manifest)
        self.get_table().query_name = query_name
        self.get_table().generated_query = query_string

        data = []
        for entry in query_results["hits"]["hits"]:
            source = entry["_source"]
            source["id"] = source["_id"]

            if "sample_type" in source:
                if source["sample_type"] in sample_types:
                    source["sample_name"] = sample_types[source["sample_type"]]
                else:
                    source["sample_name"] = source["sample_type"]

            if "files" in source:
                total_filesize = 0
                for datafile in source["files"]:
                    total_filesize += int(datafile["filesize"])

            source["total_filesize"] = sizeof_fmt(total_filesize)
            #print(entry["_source"])
            data.append(TcgaMetadata(source))
        return data

    #    @require_auth
    def get(self, request, *args, **kwargs):
        return require_auth(super(TcgaTableView, self).get)(request, *args, **kwargs)

#    @require_auth
    def post(self, request, *args, **kwargs):
        return require_auth(super(TcgaTableView, self).post)(request, *args, **kwargs)

class TestTable(tables.DataTable):
    name = tables.Column('name')
    num = tables.Column('number')

    class Meta:
        name = "test_table"

class TestPageView(tables.DataTableView):
    table_class = TestTable
    template_name = "osdcquery/results.html"

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)
    
    def get_data(self):
        data = []
        number = range(0, 20)
        for i in number:
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
            data.append(NameNum(name, i))
        return data
        

@require_auth
def query_builder(request):
    ''' Main view displays the running query and allows the user to run an
    instance from here '''

    if request.method == "POST":
        form = OsdcQueryForm(request.POST)
        if form.is_valid():
            data = request.POST
            url = "/".join(["/osdcquery/results", data["query_name"], data["generated_query"], "dir=" + data["query_top_dir"]])
            print(url)
            return redirect(url)

    if request.method == "GET":
        form = OsdcQueryForm()
        data = request.GET

    form.set_cloud(request.user)

    #print form.base_fields["cloud"].choices
    #print form.fields
    #print form.fields["cloud"]


    #again forgive this.
    es = pyelasticsearch.ElasticSearch(query_url)
    facet_query = { 
        "fields": ["_id", "analysis_id", "center_name", "files", "upload_date"],
        "query" : { 
            "matchAll" : {} 
            },
        "facets" : {
            "center_name" : { "terms" : {"field" : "center_name", "size": 50}},
            "platform" : {"terms" : {"field" : "platform", "size": 50}},
            "sample_id" : { "terms" : {"field" : "sample_id", "size": 50}},
            "disease_abbr" : {"terms" : {"field" : "disease_abbr", "size":50}},
            "participant_id" : {"terms" : {"field" : "participant_id", "size":50}},
            "analyte_code" : {"terms" : {"field" : "analyte_code", "size": 50}},
            "sample_type" : {"terms" : {"field" : "sample_type", "size": 50}},
            "tss_id" : {"terms" : {"field" : "tss_id", "size": 50}},
            "analysis_id" : {"terms" : {"field" : "analysis_id", "size": 50}},
            "state" : {"terms" : {"field" : "state", "size": 50}},
            "study" : {"terms" : {"field" : "study", "size": 50}},
            "aliquot_id" : {"terms" : {"field" : "aliquot_id", "size": 50}},
            "sample_accession" : {"terms" : {"field" : "sample_accession", "size": 50}},
            "last_modified" : {"terms" : {"field" : "last_modified", "size": 50}},
            "library_strategy" : {"terms" : {"field" : "library_strategy", "size": 50}},
            "filename" : {"terms" : {"field" : "filename", "size": 50}}

            }
        }

    facets = es.search(facet_query, index=query_index, doc_type=query_doc_type)

    choices_dict = {}
    choices_list = []

    for k,v in facets["facets"].items():
        other = v["other"]
        if other == 0:
            choices_dict[k] = []

            for item in v["terms"]:
                choices_dict[k].append(item["term"])

    for k,v in facets["facets"].items():
        other = v["other"]
        if other == 0:
            choices_list.append((k, [item["term"] for item in v["terms"]]))
#
    sorted_choices_dict = {}
    for k, v in choices_dict.items():
        sorted_choices_dict[k] = sorted(v)

    sorted_choices_list = sorted(choices_list, key=lambda tup: tup[0])
#

    #print("CHOICES!!! %s" % choices_dict)
    #sort here for now
    sorted_choices_dict = {}
    for k,v in choices_dict.items():
        sorted_choices_dict[k] = sorted(v)

    qf = QueryFields()
    for field in qf:
        print qf
    
    #print(qf.fields)
    #print("qf type %s" % type(qf))

    return render(request, 'osdcquery/form.html', {
        'form': form,
        'query_fields': qf,
        'choices_dict': sorted_choices_dict
    })

