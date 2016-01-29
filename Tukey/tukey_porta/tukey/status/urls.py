from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tukey.status.views',
    url(r'^$', 'status_public'),
    url(r"^down/$", direct_to_template, {"template": "status/down.html"}),
)

