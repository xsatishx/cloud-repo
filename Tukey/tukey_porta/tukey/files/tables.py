# tables.py
import logging

from django import template
from django.core import urlresolvers
from django.template.defaultfilters import title
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.templatetags import sizeformat
from horizon.utils.filters import replace_underscores

from tukey.files.models import (
    File, Group, FilesystemUser, GroupUser, CollectionFile,
    AbstractUser, Inode, Permission, Collection, Collection2,
    IsDirectory, Missing
)


LOG = logging.getLogger(__name__)

class DestroyAction(tables.DeleteAction):

    classes = ('btn-danger', 'btn-delete')

    def delete_model(self, user, ids, model):
        user = FilesystemUser.objects.using('files').filter(name=user)[0]
        for id in ids:
            g = model(id=id)#, owner=user)
            g.delete(using='files')

    def _conjugate(self, ignored=None, past=None):
	return self.__class__.name.title()


class DeleteAction(DestroyAction):
    name = "delete"
    action_present = _("Delete")
    action_past = _("Deleted")


class RemoveAction(DestroyAction):
    name = "remove"
    action_present = _("Remove")
    action_past = _("Removed")


class EditAction(tables.LinkAction):
    name = "edit"
    action_present = _("Edit")
    action_past = _("Edited")
    classes = ('btn')


class MultiLink(tables.LinkAction):
    ''' extend this class when you have multiple link items
    per page.
    '''
    classes = ("ajax-modal", "btn-create")

class NewLink(MultiLink):
    ''' name must be different to have multiple link items
    on one page for example the permissions page.
    '''
    name = "new"

class NewGroup(NewLink):
    verbose_name = _("New Group")
    url = "files:create_group"

class NewCollection(NewLink):
    verbose_name = _("New Experimental Unit")
    url = "files:create_collection"

class NewCollection2(NewLink):
    verbose_name = _("New Project")
    url = "files:create_collection2"

class NewPermissionFileUser(NewLink):
    verbose_name = _("Share File")
    url = "files:create_permission_file_user"
    name = "new_permission_file_user"


class ArkKey(NewLink):
    verbose_name = _("Locate From ARK Key")
    url = "files:create_permission_file_user"
    name = 'ark_key'

    classes = ("btn-create")

    def get_link_url(self, datum):
	return "http://console.opensciencedatacloud.org/dev/keyservice/ark:/31807/bn%s/" % datum.name
    

#class NewPermissionFileGroup(MultiLink):
#    name = "new_file_group"
#    verbose_name = _("Share File with Group")
#    url = "files:create_permission_file_group"
#

class NewPermissionCollectionUser(MultiLink):
    name = "new_collection_user"
    verbose_name = _("Share Experimental Unit")
    url = "files:create_permission_collection_user"


#class NewPermissionCollectionGroup(MultiLink):
#    name = "new_collection_group"
#    verbose_name = _("Share Experimental Unit with Group")
#    url = "files:create_permission_collection_group"


class NewPermissionCollection2User(MultiLink):
    name = "new_collection2_user"
    verbose_name = _("Share Project")
    url = "files:create_permission_collection2_user"


#class NewPermissionCollection2Group(MultiLink):
#    name = "new_collection2_group"
#    verbose_name = _("Share Project with Group")
#    url = "files:create_permission_collection2_group"


class NewFile(NewLink):
    verbose_name = _("New File")
    url = "files:create_file"

class NewGroupUser(NewLink):
    verbose_name = _("Add User to Group")
    url = "files:create_group_user"


class NewCollectionFile(NewLink):
    verbose_name = _("Add File to Unit")
    url = "files:create_collection_file"
    name = "new_collection_file"


class NewCollection2Collection(NewLink):
    verbose_name = _("Add Unit to Project")
    url = "files:create_collection2_collection"


class DeleteFile(DeleteAction):
    data_type_singular = _("File")
    data_type_plural = _("Files")

    def delete(self, request, obj_id):
        self.delete_model(request.user, [obj_id], Inode)

    def allowed(self, request, file):
	return get_missing(file) == "not found"


class DeleteGroup(DeleteAction):
    data_type_singular = _("Group")
    data_type_plural = _("Groups")

    def delete(self, request, obj_id):
        self.delete_model(request.user, [obj_id], AbstractUser)


class DeleteCollection(DeleteAction):
    data_type_singular = _("Experimental Unit")
    data_type_plural = _("Experimental Units")

    def delete(self, request, obj_id):
        self.delete_model(request.user, [obj_id], Inode)


class DeleteCollection2(DeleteAction):
    name="Delete"
#    data_type_singular = _("Project")
#    data_type_plural = _("Projects")

    data_type_singular = _("Project")
    data_type_plural = _("Projects")

    def delete(self, request, obj_id):
        self.delete_model(request.user, [obj_id], Inode)


class DeletePermission(DeleteAction):
    data_type_singular = _("Permission")
    data_type_plural = _("Permissions")

    def delete(self, request, obj_id):
	print 'The Object ID is:', obj_id
        self.delete_model(request.user, [obj_id], Permission)


class RemoveGroupUser(RemoveAction):
    data_type_singular = _("User from Group")
    data_type_plural = _("Users from Groups")

    def delete(self, request, obj_id):
        self.delete_model(request.user, [obj_id], GroupUser)


class RemoveCollectionFile(RemoveAction):
    data_type_singular = _("File from Collection")
    data_type_plural = _("Files from Collections")

    def delete(self, request, obj_ids):
        self.delete_model(request.user, [obj_ids], CollectionFile)

class RemoveCollection2Collection(RemoveAction):
    data_type_singular = _("Collection from Collection")
    data_type_plural = _("Collections from Collections")

    def handle(self, table, request, obj_ids):
        self.delete_model(request.user, obj_ids, Collection2Collection)


def get_name(item):
    return item.name

def get_ark(item):
    return '"http://console.opensciencedatacloud.org/dev/keyservice/ark:/31807/bn%s/"' % item.name

def file_get_ref_al_location(file):
    return file.real_location


def get_email(user):
    return  user.email


def get_ref_group(item):
    return item.filesystem_group_ref.name


def get_ref_collection(item):
    return item.collection_ref.name

def get_ref_collection2(item):
    return item.collection2_ref.name


def get_ref_user(item):
    return item.filesystem_user_ref.name


def get_ref_file(item):
    return item.file_ref.real_location

def get_user_ref(item):
    return item.user.name

file_models = [(File, "File"), (Collection, "Experimental Unit"), (Collection2, "Project")]
user_models = [(FilesystemUser, "User"), (Group, "Group")]

def get_user_name(item):
    for model, _ in user_models:
	print "The ref is:", item.inode_ref.id
	user_objects = model.objects.using("files").filter(parent_id=item.user_ref.id)
	if len(user_objects) > 0:
	    return user_objects[0].name


def get_inode_name(item):
    for model, _ in file_models:
        file_objects = model.objects.using("files").filter(parent_id=item.inode_ref.id)
        if len(file_objects) > 0:
	    if hasattr(file_objects[0], 'real_location'):
		return file_objects[0].real_location
            return file_objects[0].name


def get_resource_type(item):
    for model, name in file_models:
        user_objects = model.objects.using("files").filter(parent_id=item.inode_ref.id)
        if len(user_objects) > 0:
            return name


def get_group_type(item):
    for model, name in user_models:
        user_objects = model.objects.using("files").filter(parent_id=item.user_ref.id)
        if len(user_objects) > 0:
            return name

def get_file_type(item):
    directories = IsDirectory.objects.using("files").filter(file_ref=item.id)
    if len(directories) > 0:
	return "directory"
    return "file"

def get_missing(item):
    directories = Missing.objects.using("files").filter(file_ref=item.id)
    if len(directories) > 0:
        return "not found"
    return "file exists"

def get_permissions(item):
    if 'w' in item.permissions:
	return "Read/Write"
    return "Read-only"


    
class FilesTable(tables.DataTable):

    #name = tables.Column(get_name,
    #    verbose_name = _("Name"))

    location = tables.Column(file_get_ref_al_location,
        verbose_name = _("Location"))

    file_type = tables.Column(get_file_type,
	verbose_name = _("File Type"))

    missing = tables.Column(get_missing,
	verbose_name = _("File Exists"))


    def get_object_id(self, datum):
        return unicode(datum.parent.id)

    class Meta:
        name = "files"
        verbose_name = _("Files")

	# Add file to collection share file with user/group
	#row_actions = (NewCollectionFile, NewPermissionFileUser, NewPermissionFileGroup)

	# return this in but not for our showin off
        #row_actions = (DeleteFile, )#EditFile)
	table_actions = (DeleteFile, )
	pagination_param = 'file_marker'


class FilesystemUsersTable(tables.DataTable):

    name = tables.Column(get_name,
        verbose_name = _("Name"))

    email = tables.Column(get_email,
        verbose_name = _("Email"))

    class Meta:
        name = "users"
        verbose_name = _("Users")
	pagination_param = 'user_marker'


class GroupsTable(tables.DataTable):

    name = tables.Column(get_name,
        verbose_name = _("Name"))

    def get_object_id(self, datum):
        return unicode(datum.parent.id)

    class Meta:
        name = "groups"
        verbose_name = _("My Groups")
        row_actions = (DeleteGroup, )#EditGroup)
	table_actions = (NewGroup, DeleteGroup)
	pagination_param = 'group_marker'

class ProjectGroupsTable(tables.DataTable):
    name = tables.Column(get_name,
        verbose_name = _("Name"))

    def get_object_id(self, datum):
        return unicode(datum.parent.id)

    class Meta:
        name = "project_groups"
        verbose_name = _("Project Groups")
        pagination_param = 'project_group_marker'


class CollectionsTable(tables.DataTable):

    name = tables.Column(get_name,
        verbose_name = _("Name"))

    def get_object_id(self, datum):
        return unicode(datum.parent.id)

    class Meta:
        name = "collections"
        verbose_name = _("Experimental Units")
        row_actions = (ArkKey, DeleteCollection,)# EditCollection)
	table_actions = (NewCollection, DeleteCollection)
	pagination_param = 'collection_marker'


class Collection2sTable(tables.DataTable):

    name = tables.Column(get_name,
        verbose_name = _("Name"))


    def get_object_id(self, datum):
        return unicode(datum.parent.id)

    class Meta:
        name = "collection2s"
        verbose_name = _("Projects")
        row_actions = (DeleteCollection2,)# EditCollection2)
	table_actions = (NewCollection2, DeleteCollection2)
	pagination_param = 'collection2_marker'


class PermissionsTable(tables.DataTable):

    resource_type = tables.Column(get_resource_type,
	verbose_name = _("Resource Type"))

    file_name = tables.Column(get_inode_name,
        verbose_name = _("Resource Name"))

    group_type = tables.Column(get_group_type,
	verbose_name = _("Account Type"))

    user_name = tables.Column(get_user_name,
	verbose_name = _("Account Name"))

    permissions = tables.Column(get_permissions,
	verbose_name = _("Permissions"))

    def get_object_id(self, datum):
	return unicode(datum.id)

    def get_object_display(self, datum):
	return "%s with %s." % (datum.inode_ref.id, datum.user_ref.id)
	

    class Meta:
        name = "permissions"
        verbose_name = _("Permissions")
        row_actions = (DeletePermission,)# EditPermission)
	table_actions = (NewPermissionFileUser, NewPermissionCollectionUser, NewPermissionCollection2User, DeletePermission)
	pagination_param = 'permission_marker'


class GroupUsersTable(tables.DataTable):

    user_name = tables.Column(get_ref_user,
        verbose_name = _("User"))
        
    group_name = tables.Column(get_ref_group,
        verbose_name = _("Group"))

    def get_object_id(self, datum):
        return unicode(datum.id)

    def get_object_display(self, datum):
	return "%s from %s" % (get_ref_user(datum),get_ref_group(datum))

    class Meta:
        name = "group_users"
        verbose_name = _("Users in Groups")
        row_actions = (RemoveGroupUser,)# EditGroupUser,)
	table_actions = (NewGroupUser, RemoveGroupUser)
	pagination_param = 'group_user_marker'

        
class CollectionFilesTable(tables.DataTable):

    collection_name = tables.Column(get_ref_collection,
        verbose_name = _("Experimental Unit"))
        
    file_name = tables.Column(get_ref_file,
        verbose_name = _("File"))

    def get_object_id(self, datum):
        return unicode(datum.id)

    def get_object_display(self, datum):
        return "%s from %s" % (get_ref_file(datum),get_ref_collection(datum))

    class Meta:
        name = "collection_files"
        verbose_name = _("Files in Experimental Units")
        row_actions = (RemoveCollectionFile,)#EditCollectionFile,)
	table_actions = (NewCollectionFile, RemoveCollectionFile)
	pagination_param = 'collection_file_marker'


class Collection2CollectionsTable(tables.DataTable):

    collection2_name = tables.Column(get_ref_collection2,
        verbose_name = _("Project"))
        
    collection_name = tables.Column(get_ref_collection,
        verbose_name = _("Experimental Unit"))

    class Meta:
        name = "collection2_collections"
        verbose_name = _("Experimental Units in Projects")
        row_actions = (RemoveCollection2Collection,)# EditCollection2Collection)
	table_actions = (NewCollection2Collection, RemoveCollection2Collection)
	pagination_param = 'collection2_collection_marker'

