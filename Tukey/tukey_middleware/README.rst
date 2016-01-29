Tukey Middleware
===============


Architecture
------------

The main components of the tukey Middleware architecture are the outward facing
HTTP API, the authentication and the cloud drivers system.

The cloud driver system are IaaS platform specific implementations of a single
interface which exposes the OpenStack API.  This provides a way for all OSDC
clouds will be to talk to Horizon, the OpenStack dashboard. This means that
drivers for Eucalyptus and EC2 must return "servers" and "images" with
attributes following the format outlined at http://api.openstack.org/


Installation
------------

To install on Ubuntu like clone then cd to directory and::

  $ sudo apt-get install python-virtualenv libpq-dev python-dev pkg-config libfuse-dev memcached swig libffi-dev
  $ virtualenv .venv
  $ source .venv/bin/activate
  $ python setup.py install


ID Quickstart
------------

Run this with the correct id and ip::

    $ curl -XPUT -H'content-type: application/json' --interface 172.16.1.76 localhost:8774/ids/v0/ -d @tools/collection.json
    $ curl -XPUT -H"x-id-auth-token: $(cat ~/.id_service_auth_token)" -H'content-type: application/json' --interface 172.16.1.76 localhost:8774/ids/v0/ -d @tools/collection.json
    $ tools/upload-file.py b0144f1805876f2b903339021d01f6f0 -i 172.16.1.76

To get info about the created id::

    $ curl --interface 172.16.1.76 http://localhost:8774/ids/v0/7becf893ac728ded0d4afb4b949e794b


To upload to the metadata service::

    $ curl -X PUT --interface 172.16.1.76 -H'content-type:xml' -H"x-id-auth-token: $(cat ~/.id_service_auth_token)" localhost:8774/metadata/v0/tcga -d @tools/tcga_metadata.xml

Put it all together::

    $ tools/upload-file.py $(tools/upload-metadata.py tcga tools/tcga_metadata.xml -i 172.16.1.76)

Using the fuse client::

    $ tools/osdcfs.py -d http://172.16.1.76:8774 /mnt/osdcfs/

local::

    $ tools/osdcfs.py -i 172.16.1.160 /mnt/osdcfs/
