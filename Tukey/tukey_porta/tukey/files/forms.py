# forms.py

import logging

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from tukey.files.models import (
    FilesystemUser, File, Group, CollectionFile, GroupUser, Inode, 
    AbstractUser, Collection, Collection2, Collection2Collection,
    Permission
)

LOG = logging.getLogger(__name__)


class CreateGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"), required=True)

    def handle(self, request, data):
        try:
	    user = FilesystemUser.objects.using('files').filter(name=request.user)[0]

            abstract_user = AbstractUser()
            abstract_user.save(using='files')

	    group = Group(parent=abstract_user, name=data['name'], owner=user)
	    group.save()
            messages.success(request,
                _('Your group %s has been created.' %
                    data['name']))
            return group
        except:
            exceptions.handle(request, _('Unable to create new group.'))


class CreateFileForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Filename"), required=True)
    
    location = forms.CharField(max_length="255", label=_("Location"), required=True)

    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
	    inode = Inode()
	    inode.save(using='files')
	    
            file = File(parent=inode,real_location=data['location'], name=data['name'], owner=user)
            file.save()

            messages.success(request,
                _('Your file %s has been registered.' %
                    data['name']))
            return file
        except:
            exceptions.handle(request, _('Unable to register file.'))


class CreateGroupUserForm(forms.SelfHandlingForm):

    user_name = forms.ChoiceField(label=_('User'), required=True)

    group_name = forms.ChoiceField(label=_('Group'), required=True)

    def __init__(self, request, *args, **kwargs):
        self.base_fields['user_name'].choices = [
            (f.id, f.name) for f in  FilesystemUser.objects.using('files').exclude(name=request.user)]
        self.base_fields['group_name'].choices = [
            (g.id, g.name) for g in Group.objects.using('files').filter(owner__name=request.user).all()]
        super(CreateGroupUserForm, self).__init__(request, *args, **kwargs)

    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
	    filesystem_user = FilesystemUser.objects.using('files').filter(id=data['user_name'])[0]
	    group = Group.objects.using('files').filter(id=data['group_name'], owner=user)[0]
            group_user = GroupUser(filesystem_user_ref=filesystem_user, filesystem_group_ref=group ,owner=user)
            group_user.save()
            messages.success(request,
                _('User %s has been added to group %s.' %
                    (data['user_name'], data['group_name'])))
            return group_user
        except:
            exceptions.handle(request, _('Unable to add user to group.'))


class CreateCollectionFileForm(forms.SelfHandlingForm):

    collection_name = forms.ChoiceField(label=_('Collection'), required=True)

    file_name = forms.ChoiceField(label=_('File'), required=True)

    def __init__(self, request, *args, **kwargs):
        self.base_fields['file_name'].choices = [
            (f.id, f.real_location) for f in  File.objects.using('files').filter(owner__name=request.user).all()]
        self.base_fields['collection_name'].choices = [
            (g.id, g.name) for g in Collection.objects.using('files').filter(owner__name=request.user).all()]
        super(CreateCollectionFileForm, self).__init__(request, *args, **kwargs)


    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
            file = File.objects.using('files').filter(id=data['file_name'], owner=user)[0]
            collection = Collection.objects.using('files').filter(id=data['collection_name'], owner=user)[0]
            collection_file = CollectionFile(file_ref=file, collection_ref=collection ,owner=user)
            collection_file.save()

            messages.success(request,
                _('File %s has been added to collection %s.' %
                    (data['file_name'], data['collection_name'])))
            return collection_file
        except:
            exceptions.handle(request, _('Unable to add file to collection.'))

class CreateCollectionForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Collection Name"), required=True)
    

    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
	    inode = Inode()
	    inode.save(using='files')
	    
            collection = Collection(parent=inode, name=data['name'], owner=user)
            collection.save()

            messages.success(request,
                _('Your collection %s has been registered.' %
                    data['name']))
            return collection
        except:
            exceptions.handle(request, _('Unable to register collection.'))

#class EditCollection2Form(forms.SelfHandlingForm):
#    name = forms.CharField(max_length="255", label=_("Name"), required=True)
#
#    def handle(self, request, data):
#        try:
#            messages.success(request,
#                _('Your collection2 %s has been editd.' %
#                    data['name']))
#            return collection2
#        except:
#            exceptions.handle(request, _('Unable to edit new collection2.'))


class CreateCollection2Form(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Collection of Collections Name"), required=True)

    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
            inode = Inode()
            inode.save(using='files')

            collection2 = Collection2(parent=inode, name=data['name'], owner=user)
            collection2.save()

            messages.success(request,
                _('Your collection2 %s has been registered.' %
                    data['name']))
            return collection2
        except:
            exceptions.handle(request, _('Unable to register collection2.'))


#class EditCollection2CollectionForm(forms.SelfHandlingForm):
#    name = forms.CharField(max_length="255", label=_("Name"), required=True)
#
#    def handle(self, request, data):
#        try:
#            messages.success(request,
#                _('Your collection2_collection %s has been editd.' %
#                    data['name']))
#            return collection2_collection
#        except:
#            exceptions.handle(request, _('Unable to edit new collection2_collection.'))
#

class CreateCollection2CollectionForm(forms.SelfHandlingForm):
    collection2 = forms.ChoiceField(label=_("Collection of Collections"), required=True)

    collection = forms.ChoiceField(label=_("Collection of Files"), required=True)

    def __init__(self, request, *args, **kwargs):
        self.base_fields['collection2'].choices = [
            (f.id, f.name) for f in  Collection2.objects.using('files').filter(owner__name=request.user).all()]
        self.base_fields['collection'].choices = [
            (g.id, g.name) for g in Collection.objects.using('files').filter(owner__name=request.user).all()]
        super(CreateCollection2CollectionForm, self).__init__(request, *args, **kwargs)


    def handle(self, request, data):
        try:
            user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
	    collection2 = Collection2.objects.using('files').filter(id=data['collection2'])[0]
	    collection = Collection.objects.using('files').filter(id=data['collection'])[0]

            collection2_collection = Collection2Collection(collection2_ref=collection2, collection_ref=collection, owner=user)
            collection2_collection.save()

            messages.success(request,
                _('Collecion %s has been added to collection %s.' %
                    (data['collection'], data['collection2'])))
            return collection2_collection
        except:
            exceptions.handle(request, _('Unable to add collection to collection.'))


class CreatePermissionForm(forms.SelfHandlingForm):

    user = forms.ChoiceField(label=_("User/Group"), required=True)

    permissions = forms.ChoiceField(label=_("Write Permission"), required=True)


    def __init__(self, request, *args, **kwargs):
	self.base_fields['permissions'].choices = (('r', "Read Only"),('w', "Read/Write"))
        self.base_fields['user'].choices = get_user_choices(request.user)
        super(CreatePermissionForm, self).__init__(request, *args, **kwargs)


    def handle(self, request, data):
        try:
	    user = FilesystemUser.objects.using('files').filter(name=request.user)[0]
	    inode = Inode.objects.using('files').filter(id=data['inode'])[0]
	    abstract_user = AbstractUser.objects.using('files').filter(id=data['user'])[0]

            permission = Permission(inode_ref=inode, user_ref=abstract_user, owner=user, permissions=data['permissions'])
            permission.save(using='files')

            messages.success(request,
                _('Your files %s have been shared with %s.' %
                    (data['inode'], data['user'])))
            return permission
        except:
            exceptions.handle(request, _('Unable to set permissions.'))


class CreatePermissionFileUserForm(CreatePermissionForm):

    inode = forms.ChoiceField(label=_("File"), required=True)


    def __init__(self, request, *args, **kwargs):
        self.base_fields['inode'].choices = [
            (f.parent.id, f.real_location) for f in  File.objects.using('files').filter(owner__name=request.user).all()]
        super(CreatePermissionFileUserForm, self).__init__(request, *args, **kwargs)

class CreatePermissionCollectionUserForm(CreatePermissionForm):

    inode = forms.ChoiceField(label=_("Collection"), required=True)


    def __init__(self, request, *args, **kwargs):
        self.base_fields['inode'].choices = [
            (f.parent.id, f.name) for f in  Collection.objects.using('files').filter(owner__name=request.user).all()]
        super(CreatePermissionCollectionUserForm, self).__init__(request, *args, **kwargs)


class CreatePermissionCollection2UserForm(CreatePermissionForm):

    inode = forms.ChoiceField(label=_("Collection of Collections"), required=True)

    def __init__(self, request, *args, **kwargs):
        self.base_fields['inode'].choices = [
            (f.parent.id, f.name) for f in  Collection2.objects.using('files').filter(owner__name=request.user)]
        super(CreatePermissionCollection2UserForm, self).__init__(request, *args, **kwargs)


def get_user_choices(user):
    users = [(g.parent.id, 'User: %s' % g.name) for g in FilesystemUser.objects.using('files').exclude(name=user)]

    groups = [(g.parent.id, 'Group: %s' % g.name) for g in Group.objects.using('files').filter(owner__name=user)]

    project_groups = [(g.parent.id, 'Project Group: %s' % g.name) for g in Group.objects.using('files').filter(
        id__in = [ g.filesystem_group_ref.id for g in
            GroupUser.objects.using('files').filter(
                filesystem_user_ref__name=user).exclude(owner_id__in=FilesystemUser.objects.using('files').all())
        ]
    )]

    return users + groups + project_groups


