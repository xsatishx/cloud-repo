from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
#    url(r'^$', 'tukey.content.views.index'),
    url(r'^news/$', "tukey.content.views.rss_page", name="news-rss"),
    url(r'^content-admin/$', 'tukey.content.views.content_admin', name="content-admin"),
    #because of '' allowed as index slug
    url(r'^content-admin/edit/(?P<slug>[-\w]*)$', 'tukey.content.views.page_edit', name ="content-admin-edit"),
    url(r'^content-admin/edit/(?P<slug>[-\w]*)/$', 'tukey.content.views.page_edit', name ="content-admin-edit"),
    url(r'^content-admin/add/$', 'tukey.content.views.page_add', name ="content-admin-add"),
    url(r'^content-admin/delete/(?P<slug>[-\w]*)/(?P<confirm>YES)/$', 'tukey.content.views.page_delete', name ="content-admin-delete"),
    url(r'^content-admin/delete/(?P<slug>[-\w]*)$', 'tukey.content.views.page_delete', name ="content-admin-delete"),
    url(r'^(?P<slug>[-\w]*)/$', 'tukey.content.views.page'),
    #temp url for dev tukey
    url(r'^publications$', 'tukey.content.views.publications'),
)
