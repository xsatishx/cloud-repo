Tukey Middleware
================

The tukey middleware serves two main purposes:
 - "multiplex" and combine OpenStack API requests to multiple clouds running various software such as OpenStack, Eucalyptus, EC2 etc.
 - Provide secure centralized access to plugins and core service APIs like metadata, filesharing...


The middleware is a webservice that maps URLs to an underlying Tukey Python API.  The Tukey Python API is an interface for generic cloud actions like listing images and launching instances.  Developers implement drivers for specific cloud software like OpenStack, Eucalyptus, EC2.  A specific tukey middleware installation then registers a list of clouds and the drivers those clouds use as well as basic configuration parameters.  When a request comes in to the OpenStack API the middleware looks at the list of clouds and calls methods the cloud driver instances.

HTTP API
--------

Applications talk to Tukey using HTTP. The Tukey Middleware webservice exposes at least two APIs: the OpenStack API documented at http://api.openstack.org/api-ref.html and its own API for metadata, digital id infrucstructure and user defined plugins.

OpenStack API
~~~~~~~~~~~~~

The main reason Tukey provides the OpenStack API is to talk to the Tukey Portal / Horizon.  The Tukey Portal software is built on Horizon, the OpenStack Dashboard, with modifications to be aware of multiple "clouds".  Tukey-portal displays a cloud name and appends a cloud name to server and keypair creation.  These requests pass normally through Horizon and are then sent to the Middleware.

Example of an OpenStack API request::
    GET /v1.1/b61bf0683335448e8f3f778dec2949be/servers/detail

.. code-block:: python

    from utils import Rest
    from cloud import all_clouds, cloud_by_name

    rest = Rest('v11', __name__)

    @rest.get('/servers/detail')
    def list_servers():
        instances = []

        # we will need this in every request.  I know flask
        # will let us abstract it out
        auth_token = request.headers.get('x-auth-token')

        for cloud in all_clouds(auth_token):
            instances += cloud.list_instances()
        return json.dumps({"servers": instances})

    @rest.post('/servers')
    def launch_server(data):
        server = json.loads(data)
        cloud_name = server["name"].split('-')[0]
        server["name"] = server["name"][len(cloud_name):]

        # returns a driver object of the type and parameters defined
        # in the cloud registry (e.g Adler: {driver: Eucalyptus})
        cloud = cloud_by_name(cloud_name)

        return cloud.launch_instance(server)

    ...


Tukey API
~~~~~~~~~

The "Tukey" API is for Operations that don't need to proxy the OpenStack commands for interaction with Horizon.  We version our APIs similar to OpenStack ( version in URL not version numbers ).  So we can avoid conflicts with the OpenStack URLs the Tukey API is prefixed with ``/tukey``.  Developers can register their new plugins to appear at this path.

Example tukey API::
    GET /tukey/v0.1/metadata/

Plugins/Modules
---------------

There two forms of extension to the tukey middleware.  The first is plugins that extend the non OpenStack Tukey API.  Developers register these plugins with Tukey and can access the Tukey Python API and Tukey-Auth Python API.  An example of plugin URL would be ``/tukey/v0.1/myplugin/``.  The second type of extension is by creating a new cloud driver.


VM IP Authentication
--------------------

VM IP authentication (VIA) means HTTP commands issued from a VM are tied to the
owner of the VM.  This assumes that virtual machines are running on a network
in which IPs cannot be successfully spoofed meaning a packet sent with a wrong
source IP will not make it back to the sender.  OSDC cloud environments satisfy
this requirement.  If your environment does not match this criteria DO NOT USE
VM IP AUTHENTICATION!  VM based auth works by looking at the source IP of
the HTTP request and then looking up that IP against all running VMs to find
the owner of that VM. The service using VIA can then trust that this request was
issued by the owner of the VM.

Users can disable and enable VM based authentication. A use case for disable VIA
would be if you launched a VM and then granted other users in your project
access to the VM.

VM IP Authentication is used by the cifs/glusterfs automount module to serve
a booting instance with the user's username and password.


Tukey Python API
----------------

The Tukey Python API defines an interface for issuing standard cloud commands like listing instances, images and keypairs as well starting and stopping virtual machines.  Developers provide implementations to this interface for each type of cloud they need the middleware to talk to.  Drivers for several cloud software stacks could share lots of code by using a library like libcloud.

.. code-block:: python

    class CloudDriver(object):

        def __init__(self, cloud_name, auth_token, driver_parameters):

            self.auth = TukeyAuth(cloud_name, auth_token)

        def list_servers(self):
            return not_implemented()

        def list_images(self):
            return not_implemented()

        def launch_server(self, data):
            return not_implemented()

    ...

.. code-block:: python

    class OpenStackDriver(CloudDriver):

        def list_servers(self):
            auth = self.auth
            #use credentials to make request


Questionable Practices
----------------------

In order to continue using Tukey Portal as is with the middleware the cluster launch and login node keypair mechanism are defined as cloud drivers:


.. code-block:: python

    class ClusterLaunch(CloudDriver):

        def __init__(self, cloud_name, auth_token, driver_parameters):
           ...
