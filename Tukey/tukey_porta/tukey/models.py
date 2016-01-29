from django.contrib.auth.models import AnonymousUser

class UnregisteredUser(AnonymousUser):

    def __init__(self, method, identifier):
	self.method=method
	self.identifier = identifier	
