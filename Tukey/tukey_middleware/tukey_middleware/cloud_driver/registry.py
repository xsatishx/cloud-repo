#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

''' Functions for getting the clouds '''

import memcache

from tukey_middleware import utils
from tukey_middleware import local_settings
from tukey_middleware.cloud_driver.login_keypairs import LoginKeypairsDriver
from tukey_middleware.cloud_driver.login_keypairs import AllKeypairsDriver
from tukey_middleware.cloud_driver.osdc_novacluster import OsdcNovacluster
from tukey_middleware.auth.base import TukeyAuthException
from tukey_middleware.auth.token_store import TokenStore


def create_login_driver(cloud_name, driver_instance, login_url):
    ''' create login node ssh key driver from cloud'''
    db_connection_string = local_settings.vm_ip_auth["auth_db_str"]
    fingerprint = local_settings.GPG_FINGERPRINT
    gpg_home_dir = local_settings.GPG_HOME
    gpg_passphrase = local_settings.GPG_PASSPHRASE
    gpg_host_pubkey_filename = "%s/%s.pub" % (local_settings.GPG_PUBKEY_DIR,
            cloud_name)
    host = login_url
    host_passphrase = ""

    return LoginKeypairsDriver(driver_instance.cloud, driver_instance.cloud_id,
            db_connection_string, fingerprint, gpg_home_dir,
            gpg_host_pubkey_filename, gpg_passphrase, host_passphrase, host,
            driver_instance.auth.username())


class CloudRegistry(object):
    ''' Using local_settings.py, the auth_token passed in externally create
    cloud driver objects'''

    DEFAULT_AUTH = "tukey_middleware.auth.keystone_proxy.KeystoneProxy"
    DEFAULT_AUTH_PARAMS = {
        "memcache_client":  {
            "class": "memcache.Client",
             "params": [["localhost:11211"], 0]
        },
        "eucarc_path":  local_settings.EUCARC_BASE + "/users/%s/%s/.euca/eucarc"
        }

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        self.settings = settings
        self.logger = utils.get_logger()
        self.client_format = None

    def _initialize_cloud(self, cloud, name, auth_token):
        ''' Cloud entering is a dictionary and returned is the initialized
        cloud driver '''

        if "auth_driver" in cloud:
            auth_path = cloud["auth_driver"]
        else:
            auth_path = self.DEFAULT_AUTH

        self.logger.debug("getting auth class from %s", auth_path)

        if "auth_driver_parameters" in cloud:
            params = cloud["auth_driver_parameters"]
        else:
            params = self.DEFAULT_AUTH_PARAMS

        if auth_path is not None:
            auth_class = utils.get_class(auth_path).handle_parameters(params)
            auth_instance = auth_class(name, auth_token)
        else:
            auth_instance = None

        if "driver" in cloud:
            driver_path = cloud["driver"]
        elif "access" in cloud:
            has_volume = False
            has_object = False

            for service in cloud["access"]["serviceCatalog"]:
                if service["type"] == "volume":
                    has_volume = True
                if service["type"] == "object-store":
                    has_object = True

            if has_object and has_volume:
                #TODO: replace with volume + object class
                driver_path = ("tukey_middleware.cloud_driver"
                    ".openstack_volumes.OpenStackVolumeDriver")

            elif has_object:
                #TODO: replace with object class
                driver_path = ("tukey_middleware.cloud_driver"
                    ".openstack.OpenStackDriver")

            elif has_volume:
                driver_path = ("tukey_middleware.cloud_driver"
                    ".openstack_volumes.OpenStackVolumeDriver")

            else:
                driver_path = ("tukey_middleware.cloud_driver"
                    ".openstack.OpenStackDriver")
        else:
            driver_path = ("tukey_middleware.cloud_driver"
                ".osdc_euca.OsdcEucaDriver")

        self.logger.debug("getting cloud driver class from %s",
                driver_path)

        driver_class = utils.get_class(driver_path)
        if driver_class == ("tukey_middleware.cloud_driver.openstack."
                "OpenStackDriver"):
            driver_instance = driver_class(auth_instance,
                    client_format=self.client_format)
        else:
            driver_instance = driver_class(auth_instance)


        self.logger.debug("cloud: %s auth SUCCESS %s", cloud,
                auth_token)

        #TODO: for faster selection of ec2/eucalyptus cloud have a special id
        # that we can look at to instantly dismiss or accept requests
        #driver_instance.cloud_id = cloud["id"]

        driver_instance.cloud = cloud.get("cloud", name)
        driver_instance.cloud_id = name

        return driver_instance

    def build_login_driver_by_name(self, cloud_name, token_info, auth_token):
        cloud_name = cloud_name[len("login"):]
        cloud_info = token_info[cloud_name]
        base_driver = self._initialize_cloud(cloud_info, cloud_name,
                auth_token)
        return create_login_driver(cloud_name, base_driver,
            token_info["login" + cloud_name])

    def get_cloud_by_id(self, cloud_name, auth_token):
        try:
            toks = TokenStore(memcache.Client(['127.0.0.1:11211']))
            token_info = toks.get(str(auth_token))

            if cloud_name.startswith("cluster"):
                cloud_name = cloud_name[len("cluster"):]
                cloud_info = token_info[cloud_name]
                base_driver = self._initialize_cloud(cloud_info, cloud_name,
                        auth_token)
                return OsdcNovacluster(base_driver)

            elif cloud_name.startswith("login"):
                return self.build_login_driver_by_name(cloud_name, token_info,
                        auth_token)

            elif cloud_name == "all":
                # This will probably only ever be used for generating pubkeys
                # for all clouds
                # For now we assume that is the case
                drivers = []
                for key, value in token_info.items():
                    try:
                        if key != "__tukey_internal":
                            if key.startswith("login"):
                                drivers.append(self.build_login_driver_by_name(
                                        key, token_info, auth_token))
                            elif value.get("instance_keypairs", False):
                                drivers.append(self._initialize_cloud(value,
                                        key, auth_token))
                    except TukeyAuthException:
                        continue

                return AllKeypairsDriver(drivers)

            else:
                cloud_info = token_info[cloud_name]
        except Exception as exc:
            self.logger.info("Accessing cloud %s without auth_token %s",
                    cloud_name, exc.message)
            cloud_info = self.settings[cloud_name]

        return self._initialize_cloud(cloud_info, cloud_name, auth_token)

    def all_clouds(self, auth_token, client_format=None):
        ''' Return list of cloud_driver objects settings is a dictionary of
        cloud names and their drivers and parameters '''
        self.client_format = client_format
        clouds = []

        toks = TokenStore(memcache.Client(['127.0.0.1:11211']))
        token_info = toks.get(str(auth_token))

        for name, cloud in [(n, c) for n, c in token_info.items()
                if n != '__tukey_internal' and not n.startswith("login")]:
            try:
                driver_instance = self._initialize_cloud(cloud, name,
                        auth_token)
            except TukeyAuthException:
                continue

            clouds.append(driver_instance)
            clouds.append(create_login_driver(name, driver_instance,
                    token_info["login" + name]))

        return clouds
