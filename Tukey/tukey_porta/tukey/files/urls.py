#from django.conf.urls import patterns, include, url
#
#urlpatterns = patterns('files.views',
#    url(r'^$', 'files'),
#)
from django.conf.urls.defaults import patterns, url

from horizon.decorators import require_auth


from .views import (
    FileView, GroupView, CollectionFileView, CreateGroupView,
    CreateGroupUserView, CreateFileView, CreateCollectionFileView,
    CollectionView, PermissionView, CreateCollectionView, 
    CreateCollection2CollectionView, CreateCollection2View, 
    CreatePermissionFileUserView, CreatePermissionCollectionUserView,
    CreatePermissionCollection2UserView
)


urlpatterns = patterns('files.views',
    url(r'^$', FileView.as_view(), name='file'),
    url(r'^file/$', FileView.as_view(), name='file'),
    url(r'^group/$', GroupView.as_view(), name='group'),
    url(r'^collection/$', CollectionView.as_view(), name='collection'),
#    url(r'^collection2/$', Collection2View.as_view(), name='collection2'),
    url(r'^permission/$', PermissionView.as_view(), name='permission'),
#    url(r'^group_user/$', GroupUserView.as_view(), name='group_user'),
    url(r'^collection_file/$', CollectionFileView.as_view(), name='collection_file'),
    # creation urls
    url(r'^create_group/$', CreateGroupView.as_view(), name='create_group'),
    url(r'^create_group_user/$', CreateGroupUserView.as_view(), name='create_group_user'),
    url(r'^create_collection_file/$', CreateCollectionFileView.as_view(), name='create_collection_file'),
    url(r'^create_file/$', CreateFileView.as_view(), name='create_file'),
    url(r'^create_collection/$', CreateCollectionView.as_view(), name='create_collection'),
    url(r'^create_collection2/$', CreateCollection2View.as_view(), name='create_collection2'),
    url(r'^create_permission_file_user/$', CreatePermissionFileUserView.as_view(), name='create_permission_file_user'),
 #   url(r'^create_permission_file_group/$', CreatePermissionFileGroupView.as_view(), name='create_permission_file_group'),
    url(r'^create_permission_collection_user/$', CreatePermissionCollectionUserView.as_view(), name='create_permission_collection_user'),
 #   url(r'^create_permission_collection_group/$', CreatePermissionCollectionGroupView.as_view(), name='create_permission_collection_group'),
    url(r'^create_permission_collection2_user/$', CreatePermissionCollection2UserView.as_view(), name='create_permission_collection2_user'),
#    url(r'^create_permission_collection2_group/$', CreatePermissionCollection2GroupView.as_view(), name='create_permission_collection2_group'),
    url(r'^create_collection2_collection/$', CreateCollection2CollectionView.as_view(), name='create_collection2_collection'),
#    url(r'^(?P<id>[^/]+)/edit_collection2_collection/$', EditCollection2CollectionView.as_view(), name='edit_collection2_collection'),
#    url(r'^(?P<id>[^/]+)/edit_group/$', EditGroupView.as_view(), name='edit_group'),
#    url(r'^(?P<id>[^/]+)/edit_collection/$', EditCollectionView.as_view(), name='edit_collection'),
#    url(r'^(?P<id>[^/]+)/edit_file/$', EditFileView.as_view(), name='edit_file'),
#    url(r'^(?P<id>[^/]+)/edit_group_user/$', EditGroupUserView.as_view(), name='edit_group_user'),
#    url(r'^(?P<id>[^/]+)/edit_collection_file/$', EditCollectionFileView.as_view(), name='edit_collection_file'),
#    url(r'^(?P<id>[^/]+)/edit_collection2/$', EditCollection2View.as_view(), name='edit_collection2'),
#    url(r'^(?P<id>[^/]+)/edit_permission/$', EditPermissionView.as_view(), name='edit_permission'),
)


#urlpatterns = patterns('',
#    url(r'^$',
#        ListView.as_view(
#            queryset=FilesystemUser.objects.using('files').all(),
#            context_object_name='users',
#            template_name='osdc/files/files.html'),
#        name='files'),


#    url(r'^(?P<pk>\d+)/$',
#        DetailView.as_view(
#            model=Poll,
#            template_name='polls/detail.html'),
#        name='poll_detail'),
#    url(r'^(?P<pk>\d+)/results/$',
#        DetailView.as_view(
#            model=Poll,
#            template_name='polls/results.html'),
#        name='poll_results'),
#    url(r'^(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),

#)
