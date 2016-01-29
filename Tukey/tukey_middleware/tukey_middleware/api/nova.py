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
''' HTTP API definitions for compatibility with the Nova OpenStack API
http://api.openstack.org/api-ref.html '''


import base64
import flask
import json
import memcache
import psycopg2

from novaclient import exceptions as nova_exceptions
from tukey_middleware import local_settings
from tukey_middleware.auth.token_store import TokenStore
from utils import Rest

rest = Rest('nova', __name__)


@rest.after_request
def add_mimetype(response):
    response.headers["content-type"] = "application/json"
    return response


@rest.get('/servers/detail')
def list_servers():
    servers = rest.api_manager.list_for_all("servers",
        lambda cloud: cloud.list_instances())
    return servers

@rest.put('/servers/<server_id>')
def update_server(data, server_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_instance(server_id))
    cloud.update_instance(server_id,
            name=json.loads(data)["server"]["name"])
    return ""

@rest.get('/servers/<server_id>')
def get_server(server_id):
    return rest.api_manager.get_item("server",
            lambda cloud: cloud.get_instance(server_id))


@rest.get('/servers/<server_id>/os-security-groups')
def get_server_security_groups(server_id):
    groups = rest.api_manager.get_item("security_groups",
        lambda cloud: cloud.get_instance_security_groups(server_id))
    return groups


@rest.get('/os-keypairs')
def list_keypairs():
    keypairs_json = rest.api_manager.list_for_all("keypairs",
            lambda cloud: cloud.list_keypairs())
    return keypairs_json


@rest.get('/flavors/detail')
def list_flavors():
    return rest.api_manager.list_for_all("flavors",
            lambda cloud: cloud.list_sizes())


@rest.get('/flavors/<flavor_id>')
def get_flavor(flavor_id):
    # the . throws things off
    full_flavor_id = flask.request.path.split('/')[-1]
    return rest.api_manager.get_item("flavor",
        lambda cloud: cloud.get_size(full_flavor_id))


@rest.get('/os-security-groups')
def list_security_groups():
    return rest.api_manager.list_for_all("security_groups",
        lambda cloud: cloud.list_security_groups())


@rest.get('/os-floating-ips')
def list_floating_ips():
    return rest.api_manager.list_for_all("floating_ips",
        lambda cloud: cloud.list_floating_ips())


@rest.get('/os-quota-sets/<project_id>')
def list_quota_sets(project_id):
    quota_set = {}
    for cloud in rest.api_manager.all_clouds():
        quotas = cloud.list_quotas()
        if quotas:
            # the index is the cloud name and "cloud" is cloud_id instead
            # of cloud i need to fix this in the portal
            quota_set[cloud.cloud] = quotas
            quota_set[cloud.cloud]["cloud"] = cloud.cloud_id

    return json.dumps({"quota_set": quota_set})


@rest.get('/os-simple-tenant-usage/<project_id>')
def list_simple_tenant_usage(project_id):

    #TODO: move this to the database
    resources = {
        'cloud': {
            'adler': 'OSDC-Adler',
            'tcga': 'Bionimbus-PDC',
            'pdc': 'Bionimbus-PDC',
            'sullivan': 'OSDC-Sullivan',
            'atwood': 'atwood',
            'goldberg': 'goldberg',
            'cobb': 'cobb'
        },
        'hadoop': {
            name.replace('-','_').lower(): name for name in [
                'OCC-Y', 'OCC-LVOC-HADOOP', 'skidmore']
        }
    }

    toks = TokenStore(memcache.Client(['127.0.0.1:11211']))
    token_info = toks.get(str(flask.g.auth_token))

    username = token_info["__tukey_internal"]["access"]["user"]["username"]

    conn_str = "".join(["dbname='", local_settings.USAGE_DB_NAME, "' user='",
            local_settings.USAGE_DB_USERNAME, "' host='",
            local_settings.USAGE_DB_HOST, "' password='",
            local_settings.USAGE_DB_PASSWORD, "' port=",
            str(local_settings.USAGE_DB_PORT)])

    db_connection = psycopg2.connect(conn_str)

    from tukey_middleware.cloud_driver.osdc_euca import OsdcUsage

    start = flask.request.args.get('start')
    stop = flask.request.args.get('end')

    #TODO: instead pass in a connection string
    osdc_usage = OsdcUsage(db_connection, resources)
    tenant_usage = osdc_usage.list_usages(start, stop, str(username))

    return json.dumps({"tenant_usage": tenant_usage})


@rest.delete('/servers/<server_id>')
def delete_server(server_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_instance(server_id))
    cloud.delete_instance(server_id)
    return ""


@rest.delete('/servers/<server_id>/os-volume_attachments/<volume_id>')
def detach_volume(server_id, volume_id):
    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_instance(server_id))
    cloud.detach_volume(server_id, volume_id)
    return ""


@rest.post('/servers/<server_id>/os-volume_attachments')
def attach_volume(data, server_id):

    volume_data = json.loads(data)["volumeAttachment"]

    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_instance(server_id))
    cloud.attach_volume(server_id, volume_data["volumeId"], volume_data["device"])

    return ""


@rest.delete('/servers/cluster<cloud>-<string(length=36):server_id>')
def delete_cluster(cloud, server_id):
    rest.api_manager.do_action("", {"name": "cluster%s-%s" % (cloud,
            server_id)},
            lambda c, k: c.delete_instance(server_id))
    return ("", 202)


@rest.post('/servers/<server_id>/action')
def server_action(data, server_id):

    action_data = json.loads(data)
    action = action_data.keys()[0]

    cloud = rest.api_manager.get_cloud_from_item(
        lambda cloud: cloud.get_instance(server_id))

    if action == "createImage":
        result = cloud.create_image(server_id, action_data[action]["name"],
                metadata=action_data[action]["metadata"])
        @flask.after_this_request
        def add_headers(response):
            response.headers['Location'] = "/v1/images/%s" % result
            return response
        return result

    elif action == "os-getConsoleOutput":
        return json.dumps({"output":
                cloud.get_log(server_id, action_data[action]["length"])})

    elif action == "changePassword":
        #TODO: implement
        return cloud.change_password(server_id)

    elif action == "reboot":
        cloud.reboot_instance(server_id,
                reboot_type=action_data[action]["type"])
    elif action == "rebuild":
        cloud.rebuild(server_id)

    elif action == "resize":
        cloud.resize(server_id)

    elif action == "confirmResize":
        cloud.confirm_resize(server_id)

    elif action == "revertResize":
        cloud.revert_resize(server_id)

    elif action == "pause":
        cloud.pause_instance(server_id)

    elif action == "unpause":
        cloud.unpause_instance(server_id)

    elif action == "suspend":
        cloud.suspend_instance(server_id)

    elif action == "unsuspend":
        cloud.unsuspend_instance(server_id)

    else:
        return ("%s not supported" % action, 400)

    return ""


@rest.post('/servers')
def launch_server(data):
    server_data = json.loads(data)["server"]
    del server_data["name"]
    del server_data["imageRef"]
    del server_data["flavorRef"]
    # i don't know for sure but it looks to be user_data not userdata
    if "user_data" in server_data and server_data["user_data"]:
        server_data["userdata"] = base64.b64decode(server_data["user_data"])

    return rest.api_manager.do_action("server", json.loads(data)["server"],
        lambda c, s: c.launch_instances(s["name"], s["imageRef"], s["flavorRef"],
        **server_data))


@rest.delete('/os-keypairs/<keypair_name>')
def delete_keypair(keypair_name):
    rest.api_manager.do_action("", {"name": keypair_name},
        lambda c, k: c.delete_keypair(k["name"]))
    return ("", 202)


@rest.post('/os-keypairs')
def create_keypair(data):
    return rest.api_manager.do_action("keypair", json.loads(data)["keypair"],
            lambda c, k: c.import_keypair(k["name"],
                public_key=k["public_key"])
            if "public_key" in k else c.create_keypair(k["name"]))
