SSH Key Service
===============

Setup
-----

Setting up the service can be simple::
    $ cd ssh_key_service
    $ vi ssh_key_service/local_settings.py # add settings for your GPG config
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ python setup.py install
    $ python ssh_key_service/key_server.py HOST PORT

The above assumes that you already have GPG setup on the server and the
tukey_middleware deployment has the GPG setup's public key.

If this is not the case then set up GPG and generate a public key. The public
key should be put in `"%s/%s.pub" % (local_settings.GPG_PUBKEY_DIR, cloud_name)`

Client
------

The client code lives at `tukey_middleware/cloud_driver/login_keypairs.py`

Server
------

The server code lives at `tukey_middleware/ssh_key_service/key_server.py`
