from django.conf.urls import patterns, include, url

urlpatterns = patterns('tukey.keyservice.views',
    url(r'^$', 'keyservice', name='keyservice_index'),
    url(r'^(?P<key>\w+:/[\w/\-]+)/metadata$','keyservice_meta'),
    url(r'^add_repository/$', 'add_repository'),
    url(r'^add_key/$', 'add_key'),      
    url(r'^request/$','keyservice_request'),
    url(r'^(?P<key>\w+:/[\w/\-\?]+)/$', 'keyservice_lookup'), 
    url(r'^(?P<key>.*)/$', 'keyservice_invalid'),         	    
)
