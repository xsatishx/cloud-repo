from django.db import models

class DataSet(models.Model):
    #since we're using postgres it would be nice to use the uuid field, but for now just make it a char field
    #for the public data, going to use the slug as the key, but also going to create a uuid for future use
    slug = models.SlugField(max_length=200, primary_key=True)
    #every data set has to have a title
    title = models.CharField(max_length=200)
    key = models.CharField(max_length=36)
    prefix = models.CharField(max_length=10)

class Key(models.Model):
    key_name = models.CharField(max_length=1000, primary_key=True)
    public = models.BooleanField()

class KeyValue(models.Model):
    dataset = models.ForeignKey(DataSet)
    key = models.ForeignKey(Key)
    value = models.TextField(blank=True)
