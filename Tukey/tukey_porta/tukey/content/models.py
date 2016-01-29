from django.db import models

class Page(models.Model):
    slug = models.CharField(max_length=500,primary_key=True)
    title = models.CharField(max_length=500, blank=True)
    nav_name = models.CharField(max_length=500, blank=True)
    nav_order = models.IntegerField()
    img = models.CharField(max_length=500, blank=True)
    img_alt = models.CharField(max_length=500, blank=True)
    content = models.TextField()