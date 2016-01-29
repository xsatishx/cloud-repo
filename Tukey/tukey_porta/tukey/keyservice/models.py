from django.db import models

class Repository(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=2000)
    prefix = models.CharField(max_length=10, primary_key=True)
    is_active = models.BooleanField()

    def __unicode__(self):
        return self.name   

class Key(models.Model):
    name = models.CharField(max_length=200)
    local_key = models.CharField(max_length=200)
    repository = models.ForeignKey(Repository)
    is_active = models.BooleanField()

    def __unicode__(self):
        return self.name

#class Metadata(models.Model):
#    key = models.ForeignKey(Key)
#    name = models.CharField(max_length=200)
#    value = models.TextField()
    
#    def __unicode__(self):
#        return self.key + ':' + self.name
