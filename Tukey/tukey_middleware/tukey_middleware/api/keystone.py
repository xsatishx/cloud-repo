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
''' HTTP API definitions for compatibility with the Keystone OpenStack API
http://api.openstack.org/api-ref.html '''

import datetime
import flask
import json
import keystoneclient
import memcache
import sqlalchemy
import time

from flask import Blueprint
from keystoneclient.v2_0 import Client as keystone_client
from keystoneclient.apiclient.exceptions import AuthorizationFailure
from tukey_middleware import utils
from tukey_middleware.local_settings import vm_ip_auth as settings
from tukey_middleware.auth.token_store import TokenStore
from tukey_middleware.local_settings import LOCAL_PORT as LOCAL_PORT

rest = Blueprint('keystone', __name__)


@rest.after_request
def add_mimetype(response):
    ''' all responses will be application/json '''
    response.headers["content-type"] = "application/json"
    return response

def expiration(token_lifetime):
    '''Returns times stamp of token_lifetime from now
    '''
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    current = time.time()
    return str(datetime.datetime.fromtimestamp(
            current + token_lifetime).strftime(date_format))


def service_catalog_entry(admin_url, region, internal_url, public_url,
        service_type, name):
    ''' format an service catalog entry '''
    return {
        "endpoints": [
            {
                "adminURL": admin_url,
                "region": region,
                "internalURL": internal_url,
                "publicURL": public_url
            }
        ],
        "endpoints_links": [],
        "type": service_type,
        "name": name}


def format_tenant(tenant_name, tenant_id):
    ''' format an enabled tenant with no description'''
    return {
        "enabled": True,
        "description": None,
        "name": tenant_name,
        "id": tenant_id
    }


@rest.route('/tokens', methods=('GET', 'POST'))
def token_request():
    ''' Intercept a token request and use that to talk to multiple clouds
    based on values stored in the database.

    request data format will be:

    {"auth": {"passwordCredentials": {
        "password": "tukeyPassword",
        "username": "method identifier"
    }}}

    tukeyPassword is a password shared between the middleware and the portal to
    prevent anyone from talking to the middleware and impersonating users.

    method can be shibboleth or openid.
    identifier is looked up in the tukey auth db which stores users openstack
    credentials. Those credentials are used to talk to the Keystone service
    for each cloud. The auth tokens from each keystone request are stored in
    memcached with one of the tokens used as the key and returned back to
    Horizon. '''

    token_store = TokenStore(memcache.Client(['127.0.0.1:11211']))
    logger = utils.get_logger()

    try:
        token_id = flask.request.headers["x-auth-token"]
        token_info = token_store.get(str(token_id))
        return json.dumps(token_info["__tukey_internal"])
    except KeyError:
        pass

    pw_creds = json.loads(flask.request.data)["auth"]["passwordCredentials"]

    # string equality in Python is probably a side-channel vector
    if pw_creds["password"] != settings["shared_password"]:
        return ("Wrong credentials", 401)

    method, userid = pw_creds["username"].split()

    user_info_query = '''
        select username, password, cloud_name, display_name, auth_url, login_url,
            instance_keypairs.cloud_id
        from
        login join
        login_enabled on login.id = login_enabled.login_id join
        login_identifier on login.userid = login_identifier.userid join
        login_identifier_enabled on login_identifier.id =
            login_identifier_enabled.login_identifier_id join
        login_method on login_method.method_id = login_identifier.method_id
            join
        cloud on cloud.cloud_id = login.cloud_id
            left outer join
        instance_keypairs on instance_keypairs.cloud_id = cloud.cloud_id
        where login_method.method_name='%(method)s'
            and LOWER(login_identifier.identifier)=LOWER('%(id)s');
    ''' % {"method": method, "id": userid}

    engine = sqlalchemy.create_engine(settings["auth_db_str"])
    with engine.begin() as connection:
        results = connection.execute(sqlalchemy.text(user_info_query))

    roles = []
    info_by_cloud = {}
    tenant = None

    endpoints = {}

    for (_username, password, cloud, display_name, auth_url, login_url,
            instance_keypairs) in results:
        if auth_url:
            try:
                try:
                    ksc = keystone_client(auth_url=auth_url, username=_username,
                        password=password)
                except keystoneclient.apiclient.exceptions.Unauthorized:
                    # this should be a valid username so let Horizon know
                    logger.info(("Cloud %s Keystone at %s ",
                            "rejected username password: %s %s"), cloud,
                            auth_url, _username, password)
                    # this is probably not the best or clearest, just different
                    flask.abort(403)

                tenants = [t for t in ksc.tenants.list() if t.enabled]

                if len(tenants) < 1:
                    logger.info("Cloud %s username: %s has no tenants", cloud,
                            _username)
                    continue

                for tenant in tenants:
                    if tenant.name == _username:
                        break

                token_response = ksc.get_raw_token_from_identity_service(
                        auth_url, username=_username, password=password,
                        tenant_name=tenant.name)

                try:
                    # this should work if keystoneclient version <= 0.6.0
                    response, raw_token = token_response
                    response_status = response.status_code
                except ValueError:
                    # this should work if keystoneclient version >= 0.7.0
                    raw_token = token_response
                    response_status = 200

                # handle changes between 0.6.0 and 0.7.0
                if "access" not in raw_token:
                    raw_token = {"access": raw_token}

                if response_status != 200:
                    logger.info(("Cloud %s Keystone at %s ",
                            "rejected username: %s with status code: %s"),
                            cloud, auth_url, _username, response_status)
                    flask.abort(403)

                # add enpoints
                for endpoint in raw_token["access"]["serviceCatalog"]:
                    endpoints[endpoint["type"]] = endpoint["name"]

                token_id = ksc.auth_token
                user_id = ksc.user_id
                username = _username
                raw_token["cloud"] = display_name
                if instance_keypairs:
                    raw_token["instance_keypairs"] = True
                info_by_cloud[cloud] = raw_token
                info_by_cloud["login" + cloud] = login_url

                roles += raw_token["access"]["user"]["roles"]
                raw_token["cloud"] = display_name
            except AuthorizationFailure:
                logger.info("Keystone failed for %s", cloud)
        else:
            info_by_cloud[cloud] = {"username": _username,
                    "cloud": display_name,
                    "instance_keypairs": True if instance_keypairs else False}
            info_by_cloud["login" + cloud] = login_url

    if tenant is None:
        logger.info("Login failed for %s using method %s", userid, method)
        flask.abort(401)

    region = "RegionOne"
    host, port = "localhost", LOCAL_PORT

    allowed_services = ['compute', 'image', 'volume', 'object-store']

    # glance assumes that it is at /v1 so we will give it that
    #service_paths = {k: K for k in allowed_services}
    #service_paths["image"] = "v1"

    services = [("http://%s:%s/%s/%s" % (host, port, service, tenant.id),
                    service, service_name)
            for service, service_name in endpoints.items()
                if service in allowed_services]

    services += [("http://%s:%s/v2.0" % (host, port), "identity", "keystone")]

    catalog = {
        "access": {
            "token": {
                "expires": expiration(43200),
                "id": token_id,
                "tenant": format_tenant(tenant.name, tenant.id)
            },
            "serviceCatalog": [
                service_catalog_entry(url, region, url, url, service_type, name)
                    for url, service_type, name in services] + [
                service_catalog_entry(
                        "http://%s:%s/services/Admin" % (host, port), region,
                        "http://%s:%s/services/Cloud" % (host, port),
                        "http://%s:%s/services/Cloud" % (host, port), "ec2",
                        "ec2")],
            "user": {
                "username": username,
                "roles_links": [],
                "id": user_id,
                "roles": roles,
                "name": username
            }},
            "path": "", "host": host, "port": port}

    info_by_cloud["__tukey_internal"] = catalog

    # TODO:
    # see what the shortest expiration is in the set of expirations
    # then set the returned expiration to that and make sure that
    # the memcache expiration is greater than that but has a value so
    # that memcached entries don't fill everything up

    token_store.set(str(token_id), info_by_cloud, 172800)
    logger.info("Login succeeded for %s using method %s" % (userid, method))

    return json.dumps(catalog)


@rest.route('/tenants', methods=('GET', 'POST'))
def tenant_request():
    ''' Request for just the tenant info. This request assumes that /tokens
    was accessed and created the entry in memcached '''

    try:
        token_id = flask.request.headers["x-auth-token"]
    except KeyError:
        flask.abort(401)

    toks = TokenStore(memcache.Client(['127.0.0.1:11211']))
    token_info = toks.get(str(token_id))

    tenants = {
        "tenants_links": [],
        "tenants": [
           token_info["__tukey_internal"]["access"]["token"]["tenant"]
        ]
    }
    return json.dumps(tenants)

