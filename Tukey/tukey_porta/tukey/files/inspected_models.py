# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class AbstractUser(models.Model):
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'abstract_user'

class Collection(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, unique=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'collection'

class Collection2(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, unique=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'collection2'

class Collection2Collection(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
    collection2_ref = models.IntegerField(null=True, blank=True)
    collection_ref = models.IntegerField(null=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'collection2_collection'

class CollectionFile(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
    collection_ref = models.IntegerField(null=True, blank=True)
    file_ref = models.IntegerField(null=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'collection_file'

class File(models.Model):
    id = models.IntegerField(primary_key=True)
    real_location = models.CharField(max_length=512, unique=True, blank=True)
    name = models.CharField(max_length=512, unique=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'file'

class FilesystemGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, unique=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'filesystem_group'

class FilesystemGroupFilesystemUser(models.Model):
    id = models.IntegerField(null=True, primary_key=True, blank=True)
    filesystem_user_ref = models.IntegerField(null=True, blank=True)
    filesystem_group_ref = models.IntegerField(null=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'filesystem_group_filesystem_user'

class FilesystemUser(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, unique=True, blank=True)
    class Meta:
        db_table = u'filesystem_user'

class Inode(models.Model):
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'inode'

class Permission(models.Model):
    id = models.IntegerField(primary_key=True)
    inode_ref = models.IntegerField(null=True, blank=True)
    user_ref = models.IntegerField(null=True, blank=True)
    owner = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'permission'

