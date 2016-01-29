from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns("",
    url(r"^$", views.query_builder, name="query_builder"),
    url(r"^results/(?P<query_name>.+)/(?P<query>.+)/dir=(?P<top_dir>.+)$", views.TcgaTableView.as_view(), name="query_results"),
    url(r"^test/$", views.TestPageView.as_view(), name="test_results"),
)
