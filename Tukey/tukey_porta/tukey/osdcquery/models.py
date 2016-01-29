from django.db import models

# Create your models here. 


class TcgaMetadata(object):
    def __init__(self, entries): 
        #self.id = name
        #self.name = name
        self.__dict__.update(entries)

class NameNum(object):
    def __init__(self, name, number=0):
        self.id = name
        self.name = name
        self.number = number
