from django.conf.urls import patterns, include, url

urlpatterns = patterns('tukey.datasets.views',
    url(r'^$', 'datasets_list_index', name='datasets_list_index'),
    url(r'^(?P<dataset_id>[-\w]+)/$', 'dataset_detail', name='dataset_detail'),                   
    #url(r'^datasets_admin/$', 'datasets_admin', name='datasets_admin_index'), 
    #url(r'^datasets_admin/add/$', 'datasets_admin_add', name='datasets_admin_add'),
    #url(r'^datasets_admin/add_keyvalue/(?P<dataset_id>\w*)/$', 'datasets_admin_add_kv', name='datasets_admin_add_kv'),
    #url(r'^datasets_admin/update/(?P<dataset_id>\w*)/$', 'datasets_admin_update', name='datasets_admin_update'),
    #url(r'^datasets_admin/delete/(?P<dataset_id>\w*)/$', 'datasets_admin_delete', name='datasets_admin_delete'),
    url(r'^keyword/(?P<keyword_filter>[ \w]*)/$', 'datasets_list_index', name='datasets_keyword'),              
    #url(r'^dataset/(?P<dataset_id>\w+)/$', 'dataset_detail', name='dataset_detail'), 
)
