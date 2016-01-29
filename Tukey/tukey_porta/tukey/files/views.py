# views.py

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import tables
from horizon import workflows

from horizon.decorators import require_auth

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _


from tukey.files.models import (
    AbstractUser, FilesystemUser, File, Group, Collection, Collection2,
    Collection2Collection, CollectionFile, GroupUser, Permission
)
from tukey.files.tables import (
    FilesTable, FilesystemUsersTable, GroupsTable, GroupUsersTable, 
    CollectionFilesTable, CollectionsTable, Collection2sTable,
    PermissionsTable, Collection2CollectionsTable, ProjectGroupsTable
)
from tukey.files.forms import (
    CreateGroupForm, CreateGroupUserForm, CreateFileForm, 
    CreateCollectionFileForm, CreateCollectionForm,
    CreateCollection2Form, CreateCollection2CollectionForm,
    CreatePermissionFileUserForm, CreatePermissionCollectionUserForm,
    CreatePermissionCollection2UserForm
)


def show(item):
    print item
    return item

class PaginatedView(tables.DataTableView):

    entries_per_page = 14

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)


    def get_marker(self):
        marker = self.request.GET.get(self.__class__.table_class._meta.pagination_param, None)
        try:
            marker = int(marker)
        except TypeError:
            marker = 0
        except ValueError:
            marker = 0
	return marker


    def get_paginated_data(self, model):
	marker = self.get_marker()
        entry_set = model.objects.using('files').filter(owner__name=self.request.user, id__gt=marker)
        table_name = self.__class__.table_class._meta.name
        setattr(self, "_more_%s" % table_name, entry_set.count() > PaginatedView.entries_per_page)
        data = [entry for entry in entry_set.all()[:PaginatedView.entries_per_page]]

        return data


#    @require_auth
    def get(self, request, *args, **kwargs):
	return require_auth(super(PaginatedView, self).get)(request, *args, **kwargs)

#    @require_auth
    def post(self, request, *args, **kwargs):
        return require_auth(super(PaginatedView, self).post)(request, *args, **kwargs)


# Figrue out how to handle this without duplicating the class some 
# kind of decorator?
class PaginatedMultiView(tables.MultiTableView):

    entries_per_page = 7

    def has_more_data(self, table):
        return getattr(self, "_more_%s" % table.name, False)


    def get_marker(self, table_class):
	# only difference from above class is that there is no table_class so 
	# we need to pass that in
        #marker = self.request.GET.get(self.__class__.table_class._meta.pagination_param, None)
        marker = self.request.GET.get(table_class._meta.pagination_param, None)
        try:
            marker = int(marker)
        except TypeError:
            marker = 0
        except ValueError:
            marker = 0
        return marker


    def get_paginated_data(self, model, table_class, subclass=True):
        marker = self.get_marker(table_class)
	if subclass:
            entry_set = model.objects.using('files').filter(owner__name=self.request.user, parent__id__gt=int(marker))
	else:
	    entry_set = model.objects.using('files').filter(owner__name=self.request.user, id__gt=int(marker))
        table_name = table_class._meta.name
        setattr(self, "_more_%s" % table_name, entry_set.count() > PaginatedMultiView.entries_per_page)
        data = [entry for entry in entry_set.all()[:PaginatedMultiView.entries_per_page]]

        return data

#    @require_auth
    def get(self, request, *args, **kwargs):
        return require_auth(super(PaginatedMultiView, self).get)(request, *args, **kwargs)

#    @require_auth
    def post(self, request, *args, **kwargs):
        return require_auth(super(PaginatedMultiView, self).post)(request, *args, **kwargs)



class FileView(PaginatedMultiView):
    table_classes = FilesTable, CollectionFilesTable

    template_name = 'osdc/files/file.html'

    def get_files_data(self):
        return self.get_paginated_data(File, FilesTable)

    def get_collection_files_data(self):
        return self.get_paginated_data(CollectionFile, CollectionFilesTable, subclass=False)


class GroupView(PaginatedMultiView):
    table_classes = ProjectGroupsTable, GroupsTable, GroupUsersTable

    template_name = 'osdc/files/group.html'

    def get_groups_data(self):
        return self.get_paginated_data(Group, GroupsTable)

    def get_group_users_data(self):
        return self.get_paginated_data(GroupUser, GroupUsersTable, subclass=False)

    def get_project_groups_data(self):
        marker = self.get_marker(ProjectGroupsTable)

	entry_set =  Group.objects.using('files').filter(
	    id__in = [ g.filesystem_group_ref.id for g in 
		GroupUser.objects.using('files').filter(
		    filesystem_user_ref__name=self.request.user, filesystem_group_ref__gt=int(marker)
		).exclude(owner_id__in=FilesystemUser.objects.using('files').all())
	    ]
	)

        table_name = ProjectGroupsTable._meta.name
        setattr(self, "_more_%s" % table_name, entry_set.count() > PaginatedMultiView.entries_per_page)
        data = [entry for entry in entry_set.all()[:PaginatedMultiView.entries_per_page]]

        return data



class CollectionView(PaginatedMultiView):
    table_classes = CollectionsTable, Collection2sTable, Collection2CollectionsTable

    template_name = 'osdc/files/collection.html'

    def get_collections_data(self):
        return self.get_paginated_data(Collection, CollectionsTable)

    def get_collection2s_data(self):
	return self.get_paginated_data(Collection2, Collection2sTable)

    def get_collection2_collections_data(self):
	return self.get_paginated_data(Collection2Collection, Collection2CollectionsTable, subclass=False)


#class Collection2View(PaginatedView):
#    table_class = Collection2sTable
#
#    template_name = 'osdc/files/collection2.html'
#
#    def get_data(self):
#        return self.get_paginated_data(Collection2)
#

class PermissionView(PaginatedView):
    table_class = PermissionsTable

    template_name = 'osdc/files/permission.html'

    def get_data(self):
        return self.get_paginated_data(Permission)

#
#    def get_data(self, model):
#        marker = self.get_marker()
#        entry_set = model.objects.using('files').filter(owner__name=self.request.user, id__gt=marker)
#	user_models = [("User", FilesystemUser), ("Group", Group)]
#	file_models = [("File", File), ("Collection", Collection),("Collection of Collections", Collection2)]
#	for um in user_models:
#	    um_entries
#        table_name = self.__class__.table_class._meta.name
#        setattr(self, "_more_%s" % table_name, entry_set.count() > PaginatedView.entries_per_page)
#        data = [entry for entry in entry_set.all()[:PaginatedView.entries_per_page]]
#
#        return data



class CollectionFileView(PaginatedView):
    table_class = CollectionFilesTable

    template_name = 'osdc/files/collection_file.html'

    def get_data(self):
        return self.get_paginated_data(CollectionFile)


#class GroupUserView(PaginatedView):
#    table_class = GroupUsersTable
#
#    template_name = 'osdc/files/group_user.html'
#
#    def get_data(self):
#        return self.get_paginated_data(GroupUser)
#
#
class CreateGroupView(forms.ModalFormView):
    form_class = CreateGroupForm
    template_name = 'osdc/files/create_group.html'
    context_object_name = 'group'
    success_url = reverse_lazy("files:group")


class CreateGroupUserView(forms.ModalFormView):
    form_class = CreateGroupUserForm
    template_name = 'osdc/files/create_group_user.html'
    context_object_name = 'group_user'
    success_url = reverse_lazy("files:group")


class CreateCollectionFileView(forms.ModalFormView):
    form_class = CreateCollectionFileForm
    template_name = 'osdc/files/create_collection_file.html'
    context_object_name = 'collection_file'
    success_url = reverse_lazy("files:file")

    
class CreateFileView(forms.ModalFormView):
    form_class = CreateFileForm
    template_name = 'osdc/files/create_file.html'
    context_object_name = 'file'
    success_url = reverse_lazy("files:file")


#class EditGroupView(forms.ModalFormView):
#    form_class = EditGroupForm
#    template_name = 'osdc/files/edit_group.html'
#    context_object_name = 'group'
#    success_url = reverse_lazy("files:group")
#
#    def get_object(self):
#        if not hasattr(self, "_object"):
#            try:
#                self._object = Group.objects.using('files').filter(id=self.kwargs['id'])[0]
#            except:
#                msg = _('Unable to retrieve group.')
#                redirect = reverse('files:group')
#                exceptions.handle(self.request, msg, redirect=redirect)
#        return self._object
#
#    def get_context_data(self, **kwargs):
#        context = super(EditGroupView, self).get_context_data(**kwargs)
#        context['group'] = self.get_object()
#        return context
#
#    def get_initial(self):
#        group = self.get_object()
#        return {'id': self.kwargs['id'],
#                'name': group.name}
#
#
#class EditGroupUserView(forms.ModalFormView):
#    form_class = EditGroupUserForm
#    template_name = 'osdc/files/edit_group_user.html'
#    context_object_name = 'group_user'
#    success_url = reverse_lazy("files:group")
#
#
#class EditCollectionFileView(forms.ModalFormView):
#    form_class = EditCollectionFileForm
#    template_name = 'osdc/files/edit_collection_file.html'
#    context_object_name = 'collection_file'
#    success_url = reverse_lazy("files:collection_file")
#
#
#class EditFileView(forms.ModalFormView):
#    form_class = EditFileForm
#    template_name = 'osdc/files/edit_file.html'
#    context_object_name = 'file'
#    success_url = reverse_lazy("files:file")
#
#
#class EditCollectionView(forms.ModalFormView):
#    form_class = EditCollectionForm
#    template_name = 'osdc/files/edit_collection.html'
#    context_object_name = 'collection'
#    success_url = reverse_lazy("files:collection")
#
#
class CreateCollectionView(forms.ModalFormView):
    form_class = CreateCollectionForm
    template_name = 'osdc/files/create_collection.html'
    context_object_name = 'collection'
    success_url = reverse_lazy("files:collection")


#class EditCollection2View(forms.ModalFormView):
#    form_class = EditCollection2Form
#    template_name = 'osdc/files/edit_collection2.html'
#    context_object_name = 'collection2'
#    success_url = reverse_lazy("files:collection")
#

class CreateCollection2View(forms.ModalFormView):
    form_class = CreateCollection2Form
    template_name = 'osdc/files/create_collection2.html'
    context_object_name = 'collection2'
    success_url = reverse_lazy("files:collection")


#class EditCollectionFileView(forms.ModalFormView):
#    form_class = EditCollectionFileForm
#    template_name = 'osdc/files/edit_collection_file.html'
#    context_object_name = 'collection_file'
#    success_url = reverse_lazy("files:collection_file")
#
#
class CreateCollectionFileView(forms.ModalFormView):
    form_class = CreateCollectionFileForm
    template_name = 'osdc/files/create_collection_file.html'
    context_object_name = 'collection_file'
    success_url = reverse_lazy("files:file")


#class EditCollection2CollectionView(forms.ModalFormView):
#    form_class = EditCollection2CollectionForm
#    template_name = 'osdc/files/edit_collection2_collection.html'
#    context_object_name = 'collection2_collection'
#    success_url = reverse_lazy("files:collection")
#
#
class CreateCollection2CollectionView(forms.ModalFormView):
    form_class = CreateCollection2CollectionForm
    template_name = 'osdc/files/create_collection2_collection.html'
    context_object_name = 'collection2_collection'
    success_url = reverse_lazy("files:collection")


#class EditPermissionView(forms.ModalFormView):
#    form_class = EditPermissionForm
#    template_name = 'osdc/files/edit_permission.html'
#    context_object_name = 'permission'
#    success_url = reverse_lazy("files:permission")
#
#
class CreatePermissionView(forms.ModalFormView):
    context_object_name = 'permission'
    success_url = reverse_lazy("files:permission")

class CreatePermissionFileUserView(CreatePermissionView):
    form_class = CreatePermissionFileUserForm
    template_name = 'osdc/files/create_permission_file_user.html'

#class CreatePermissionFileGroupView(CreatePermissionView):
#    form_class = CreatePermissionFileGroupForm
#    template_name = 'osdc/files/create_permission_file_group.html'
#
#class CreatePermissionCollectionGroupView(CreatePermissionView):
#    form_class = CreatePermissionCollectionGroupForm
#    template_name = 'osdc/files/create_permission_collection_group.html'
#

class CreatePermissionCollectionUserView(CreatePermissionView):
    form_class = CreatePermissionCollectionUserForm
    template_name = 'osdc/files/create_permission_collection_user.html'

class CreatePermissionCollection2UserView(CreatePermissionView):
    form_class = CreatePermissionCollection2UserForm
    template_name = 'osdc/files/create_permission_collection2_user.html'

#class CreatePermissionCollection2GroupView(CreatePermissionView):
#    form_class = CreatePermissionCollection2GroupForm
#    template_name = 'osdc/files/create_permission_collection2_group.html'
#
