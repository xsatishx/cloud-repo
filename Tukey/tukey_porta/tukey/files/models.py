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
    id = models.AutoField(primary_key=True)
    class Meta:
        db_table = u'abstract_user'

class FilesystemUser(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(AbstractUser)
    name = models.CharField(max_length=512, unique=True)
    class Meta:
        db_table = u'filesystem_user'

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(AbstractUser)
    name = models.CharField(max_length=512, unique=True)
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'filesystem_group'

class GroupUser(models.Model):
    id = models.AutoField(primary_key=True)
    filesystem_group_ref = models.ForeignKey(Group, db_column='filesystem_group_ref')
    filesystem_user_ref = models.ForeignKey(FilesystemUser, db_column='filesystem_user_ref', related_name='+')
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
	db_table = u'filesystem_group_filesystem_user'
	unique_together = (("filesystem_group_ref", "filesystem_user_ref"),)

class Inode(models.Model):
    id = models.AutoField(primary_key=True)
    class Meta:
        db_table = u'inode'

class File(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Inode, null=False, blank=True)
    real_location = models.CharField(max_length=512, unique=True)
    name = models.CharField(max_length=512, unique=True)
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'file'


class Missing(models.Model):
    id = models.AutoField(primary_key=True)
    file_ref = models.ForeignKey(File, db_column='file_ref')
    class Meta:
	db_table = u'missing'


class IsDirectory(models.Model):
    id = models.AutoField(primary_key=True)
    file_ref = models.ForeignKey(File, db_column='file_ref')
    class Meta:
        db_table = u'is_directory'


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Inode)
    name = models.CharField(max_length=512, unique=True)
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'collection'

class Collection2(models.Model):
    id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Inode)
    name = models.CharField(max_length=512, unique=True)
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'collection2'

class Collection2Collection(models.Model):
    id = models.AutoField(primary_key=True)
    collection2_ref = models.ForeignKey(Collection2, db_column='collection2_ref')
    collection_ref = models.ForeignKey(Collection, db_column='collection_ref')
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'collection2_collection'
        unique_together = (("collection2_ref", "collection_ref"),)

class CollectionFile(models.Model):
    id = models.AutoField(primary_key=True)
    collection_ref = models.ForeignKey(Collection, db_column='collection_ref')
    file_ref = models.ForeignKey(File, db_column='file_ref')
    owner = models.ForeignKey(FilesystemUser)
    class Meta:
        db_table = u'collection_file'
        unique_together = (("collection_ref", "file_ref"),)

class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    inode_ref = models.ForeignKey(Inode, db_column='inode_ref')
    user_ref = models.ForeignKey(AbstractUser, db_column='user_ref')
    owner = models.ForeignKey(FilesystemUser, db_column='owner')
    permissions = models.CharField(max_length=512)
    class Meta:
        db_table = u'permission'
        unique_together = (("inode_ref", "user_ref"),)

