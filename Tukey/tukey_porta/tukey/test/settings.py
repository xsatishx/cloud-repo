from settings import *



# how can I force this to take an alternate url on this

# Becuase of how Horizon handles the ports of its 
# services we may need to turn of the actually 
# server and just run the test services while this 
# we want to test things

# However this may not be the case and all information
# about the ports and hosts comes fomr the service catalog
# if that is the case make sure that we give back a service
# catalog of all the testing services.


OPENSTACK_HOST = "localhost"


OPENSTACK_KEYSTONE_URL = "http://%s:5555/v2.0" % OPENSTACK_HOST



