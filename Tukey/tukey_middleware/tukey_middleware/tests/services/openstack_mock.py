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

''' Runs as a fake nova-api for testing purposes '''

from flask import Flask, request

import json
import time
import datetime
import sys

app = Flask(__name__)

def expiration(token_lifetime):
    '''Returns times stamp of token_lifetime from now
    '''
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    current = time.time()
    return str(datetime.datetime.fromtimestamp(current + token_lifetime).strftime(date_format))

#keystone

@app.route("/v2.0/tokens", methods=["GET","POST"])
def tokens():

    #auth = json.loads(request.data)["auth"]
    if False:#"tenantId" in auth or "tenantName" in auth:
        return '{"access": {"token": {"expires": "%s", "id": "18e59gb40fb14bd599999253dcdafaa8"}, "serviceCatalog": {}, "user": {"username": "test_user", "roles_links": [], "id": "959992c53d244fea80799989c999cd99", "roles": [], "name": "test_user"}}}' % expiration(1000)
    else:
        return '{"access": {"token": {"expires": "%(expiration)s", "id": "24c2f5479de9410c863ae38aa4263631", "tenant": {"description": null, "enabled": true, "id": "65e91ae53f564ad98e7733dc6a20217f", "name": "mgreenway"}}, "serviceCatalog": [{"endpoints": [{"adminURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f", "region": "RegionOne", "internalURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f", "publicURL": "http://%(host)s/v1/65e91ae53f564ad98e7733dc6a20217f"}], "endpoints_links": [], "type": "volume", "name": "volume"}, {"endpoints": [{"adminURL": "http://%(host)s/v1", "region": "RegionOne", "internalURL": "http://%(host)s/v1", "publicURL": "http://%(host)s/v1"}], "endpoints_links": [], "type": "image", "name": "glance"}, {"endpoints": [{"adminURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f", "region": "RegionOne", "internalURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f", "publicURL": "http://%(host)s/v2/65e91ae53f564ad98e7733dc6a20217f"}], "endpoints_links": [], "type": "compute", "name": "nova"}, {"endpoints": [{"adminURL": "http://%(host)s/services/Admin", "region": "RegionOne", "internalURL": "http://%(host)s/services/Cloud", "publicURL": "http://%(host)s/services/Cloud"}], "endpoints_links": [], "type": "ec2", "name": "ec2"}, {"endpoints": [{"adminURL": "http://10.103.105.2:35357/v2.0", "region": "RegionOne", "internalURL": "http://%(host)s/v2.0", "publicURL": "http://%(host)s/v2.0"}], "endpoints_links": [], "type": "identity", "name": "keystone"}], "user": {"username": "mgreenway", "roles_links": [], "id": "95eae2c53d244fea80762689cd97cd1f", "roles": [{"id": "15217113754b4a03806868ae012e575d", "name": "Member"}], "name": "mgreenway"}}}' % {"host": "127.0.0.2:8774", "expiration": expiration(1000)}

@app.route("/v2.0/tenants", methods=["GET","POST"])
def tenants():
    return '{"tenants_links": [], "tenants": [{"enabled": true, "description": null, "name": "test_user", "id": "33391ae53f5000000e7730000a20217f"}]}'


@app.route("/v2/<project_id>/servers/<server_id>", methods=["GET"])
def get_server(project_id, server_id):

    if server_id not in [
        '42cec943-9ca8-444c-9ed7-b36c03681f7a',
        'dae9f67d-7c6d-499f-9df0-0c6bee58400b'
    ]:
        return ("", 404)

    return '''{ "server": {
        "accessIPv4": "",
        "accessIPv6": "",
        "addresses": {
            "private": [
                {
                    "addr": "192.168.0.3",
                    "version": 4
                }
            ]
        },
        "created": "2012-08-20T21:11:09Z",
        "flavor": {
            "id": "1",
            "links": [
                {
                    "href": "http://openstack.example.com/openstack/flavors/1",
                    "rel": "bookmark"
                }
            ]
        },
        "hostId": "65201c14a29663e06d0748e561207d998b343e1d164bfa0aafa9c45d",
        "id": "%s",
        "image": {
            "id": "0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
            "links": [
                {
                    "href": "http://openstack.example.com/openstack/images/0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
                    "rel": "bookmark"
                }
            ]
        },
        "links": [
            {
                "href": "http://openstack.example.com/v2/openstack/servers/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "self"
            },
            {
                "href": "http://openstack.example.com/openstack/servers/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "bookmark"
            }
        ],
        "metadata": {
            "My Server Name": "Apache1"
        },
        "name": "new-server-test",
        "progress": 0,
        "status": "ACTIVE",
        "tenant_id": "openstack",
        "updated": "2012-08-20T21:11:09Z",
        "user_id": "fake" } }''' % server_id

# nova
@app.route("/v2/<project_id>/servers", methods=["POST"])
def create_servers(project_id):
    return '''{
    "server": {
        "adminPass": "MVk5HPrazHcG",
        "id": "42cec943-9ca8-444c-9ed7-b36c03681f7a",
        "links": [
            {
                "href": "http://openstack.example.com/v2/openstack/servers/5bbcc3c4-1da2-4437-a48a-66f15b1b13f9",
                "rel": "self"
            },
            {
                "href": "http://openstack.example.com/openstack/servers/5bbcc3c4-1da2-4437-a48a-66f15b1b13f9",
                "rel": "bookmark"
            }
        ]
    } } '''
#    print >> sys.stderr, json.dumps(server)
#    return json.dumps(server)

@app.route("/v2/<project_id>/servers/<server_id>", methods=["DELETE"])
def delete_server(project_id, server_id):
    return ""

@app.route("/v2/<project_id>/servers/detail", methods=["GET","POST"])
def servers(project_id):
    return '{"servers": [{"OS-EXT-STS:task_state": null, "addresses": {"private": [{"version": 4, "addr": "172.16.1.14"}]}, "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/servers/42cec943-9ca8-444c-9ed7-b36c03681f7a", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/servers/42cec943-9ca8-444c-9ed7-b36c03681f7a", "rel": "bookmark"}], "image": {"id": "72524d81-f5f4-4138-a0b0-5e7ba25a529b", "links": [{"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/images/72524d81-f5f4-4138-a0b0-5e7ba25a529b", "rel": "bookmark"}]}, "OS-EXT-STS:vm_state": "active", "flavor": {"id": "1", "links": [{"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/1", "rel": "bookmark"}]}, "id": "42cec943-9ca8-444c-9ed7-b36c03681f7a", "user_id": "95eae2c53d244fea80762689cd97cd1f", "OS-DCF:diskConfig": "MANUAL", "accessIPv4": "", "accessIPv6": "", "progress": 0, "OS-EXT-STS:power_state": 1, "config_drive": "", "status": "ACTIVE", "updated": "2013-07-08T16:38:54Z", "hostId": "5db26dcae9123b488a0f8d6d4a8a0f26452d1cf41d5aa18dbf486139", "key_name": "", "name": "test", "created": "2013-07-08T16:38:43Z", "tenant_id": "65e91ae53f564ad98e7733dc6a20217f", "metadata": {}}, {"OS-EXT-STS:task_state": null, "addresses": {"private": [{"version": 4, "addr": "172.16.1.9"}]}, "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/servers/dae9f67d-7c6d-499f-9df0-0c6bee58400b", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/servers/dae9f67d-7c6d-499f-9df0-0c6bee58400b", "rel": "bookmark"}], "image": {"id": "72524d81-f5f4-4138-a0b0-5e7ba25a529b", "links": [{"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/images/72524d81-f5f4-4138-a0b0-5e7ba25a529b", "rel": "bookmark"}]}, "OS-EXT-STS:vm_state": "active", "flavor": {"id": "1", "links": [{"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/1", "rel": "bookmark"}]}, "id": "dae9f67d-7c6d-499f-9df0-0c6bee58400b", "user_id": "95eae2c53d244fea80762689cd97cd1f", "OS-DCF:diskConfig": "MANUAL", "accessIPv4": "", "accessIPv6": "", "progress": 0, "OS-EXT-STS:power_state": 1, "config_drive": "", "status": "ACTIVE", "updated": "2013-06-07T15:02:01Z", "hostId": "fc23543a0857d5bdae47aea2cbe6101bdf27d1b605c851b7ee32874c", "key_name": "", "name": "testing", "created": "2013-06-07T15:01:50Z", "tenant_id": "65e91ae53f564ad98e7733dc6a20217f", "metadata": {}}]}'


@app.route("/v2/<project_id>/flavors/<flavor_id>", methods=["GET","POST"])
def get_flavor(project_id, flavor_id):
    if flavor_id not in ['1','2','3','4','5']:
        return ("", 404)
    return ''' { "flavor": {
        "disk": 0,
        "id": "%s",
        "links": [
            {
                "href": "http://openstack.example.com/v2/openstack/flavors/1",
                "rel": "self"
            },
            {
                "href": "http://openstack.example.com/openstack/flavors/1",
                "rel": "bookmark"
            }
        ],
        "name": "m1.tiny",
        "os-flavor-access:is_public": true,
        "ram": 512,
        "vcpus": 1 } }''' % flavor_id

@app.route("/v2/<project_id>/flavors/detail", methods=["GET","POST"])
def flavors(project_id):
    return '{"flavors": [{"vcpus": 1, "disk": 0, "name": "m1.tiny", "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/flavors/1", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/1", "rel": "bookmark"}], "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 0, "ram": 512, "id": "1", "swap": ""}, {"vcpus": 1, "disk": 10, "name": "m1.small", "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/flavors/2", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/2", "rel": "bookmark"}], "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 20, "ram": 2048, "id": "2", "swap": ""}, {"vcpus": 2, "disk": 10, "name": "m1.medium", "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/flavors/3", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/3", "rel": "bookmark"}], "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 40, "ram": 4096, "id": "3", "swap": ""}, {"vcpus": 4, "disk": 10, "name": "m1.large", "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/flavors/4", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/4", "rel": "bookmark"}], "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 80, "ram": 8192, "id": "4", "swap": ""}, {"vcpus": 8, "disk": 10, "name": "m1.xlarge", "links": [{"href": "http://127.0.0.1:8774/v2/65e91ae53f564ad98e7733dc6a20217f/flavors/5", "rel": "self"}, {"href": "http://127.0.0.1:8774/65e91ae53f564ad98e7733dc6a20217f/flavors/5", "rel": "bookmark"}], "rxtx_factor": 1.0, "OS-FLV-EXT-DATA:ephemeral": 160, "ram": 16384, "id": "5", "swap": ""}]}'

@app.route("/v2/<project_id>/os-keypairs/<keypair_name>", methods=["DELETE"])
def delete_keypair(project_id, keypair_name):
    return ("", 202)


@app.route("/v2/<project_id>/os-keypairs", methods=["POST"])
def create_keypairs(project_id):
    # TODO: need to find out why printing to stdout is not showing up until
    # after we restart the service
    if json.loads(request.data)["keypair"]["name"] == "exists":
        return ("",409)
    else:
        returning = '{"keypair": {"public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDqNbgKUIErnVbOU08tGfX6IUv1QHV6HfcP5ODLCE22Hy4fd3djPiZbFvLIjyXn2eoyX60LSfAuMpjgaGp4IybWdPXh+ShvKxZ+b1sGLZrmHZQ0azTvpyFS4FPiTCmqUBWrXw8UzcnMpzXo98myeJzka9HIazymk7wLk1OvlnGhIw== nova@kg14-compute-3\\n", "private_key": "-----BEGIN RSA PRIVATE KEY-----\\nMIICXQIBAAKBgQDqNbgKUIErnVbOU08tGfX6IUv1QHV6HfcP5ODLCE22Hy4fd3dj\\nPiZbFvLIjyXn2eoyX60LSfAuMpjgaGp4IybWdPXh+ShvKxZ+b1sGLZrmHZQ0azTv\\npyFS4FPiTCmqUBWrXw8UzcnMpzXo98myeJzka9HIazymk7wLk1OvlnGhIwIDAQAB\\nAoGBAKk8f+wUGAJoAt28HS494BwKC1UAauL+3BPEExsiuOSsyys5rC8uLZEMmAqM\\nRZuvPyd/Mw9BMihvr0AYszZ0UA6tOmnN+/LOhkw9x0ZLTG44IeRSGPqvzIcaWW2+\\nG1vaXiTmP6GUrq6GjtkHQiK9Sb/TEt9F1lISfd6q8da2Gz5hAkEA9vFeKOBFJnNh\\naRyJKQoMbQfy9M7YVfD1s02nkPX6iVLRiEC1OljDHr79e2gmgFEF8ybDm8XIWTy2\\nAhgEEXhdLQJBAPLMy+duXlVfhnAznIJgwGimORgimZ2nV5TbdS6UI2M9Pl1HjVRX\\nyQuU6fBwSHx6VPEYl/9UfL7gX79f8fgLCY8CQFf3r6U8DyYdYAwDoFDARaDpfgD7\\nVlF3Hu+asCCRn4gfuoihFG4OhKOFQeMePOjk9AukOXZaRH6Vg/jG+VwH1pkCQQCj\\ncKDBxVXS+l6xIMz2JtLenyZHzOLDcWZPWftjw2ye3RciC4xjfkRje3aO18azpFWR\\nhhCrW+AtTTSmyptDcYqZAkA7tI6mKHEuttI5Ag/s3xEj8zb9wBL+Ta8tkaXk4qKq\\n171YDHU3TxbH8Qh+vYsqGp+oqV9xCSKz6dJM++Kj2s6t\\n-----END RSA PRIVATE KEY-----\\n", "user_id": "b2a5dbdefb3b49d191ae6bfd088360c1", "name": "%s", "fingerprint": "8b:23:a3:bc:f9:93:74:a3:1d:62:a6:29:2d:62:18:ce"}}'# % json.loads(request.data)["keypair"]["name"]
        return returning

@app.route("/v2/<project_id>/os-keypairs", methods=["GET"])
def keypairs(project_id):

    return '{"keypairs": [{"keypair": {"public_key": "ssh-dss AAAAB3NzaC1kc3MAAACBALVBl8bm7kgLlRtejtC2cuoGxr2E6Rw3bizTOcg9Ofq2vfL6JFWLfv/rJiXxEfZqIwJFNnTitOzfOYuibDeqxpzzRW7my1qdB59dmQsHUw1zNCVEOZ8EKDeTv/9bj+R1IC4H4/lSE+lspkCIU77K4JxD7G27KBHrQ8MHo0D4h9Z3AAAAFQDEWQeyuouThN+NpPGB7ompeQQgNQAAAIB5eeBiWHb4BtW3mjSZH2DyukKv8TuV/p6SqGuUcPHdh5Qe8qB0uzaLxIfIOA/i98lVdf2oLPgTDeAL+6e/RyQPlB5Li6PvDI6/n+LcLRlIr57/PyhdpPA3dRhcYFgJeRHUApCE+yOiff4gweYS7CgppaBl8LiK8KjRlYSFuSxCUAAAAIEAkcvE+av5rXARgRPyPudV9ZzRJRKE/Fz4c4ixUiyYVbS94aABYoeFWdyqBybknwUQCMqaW0eTkxDhsXjjxD9OVwGWG5nhQ5u0qzmJHGkEcpMeU39hxpvkPq2exFsQ1Ryp2qHMgMhz5fswVliWq6zJp4bR0dA8ces5jWc0b1tldfM=", "name": "test_key", "fingerprint": "38:01:28:7b:b3:92:44:71:d0:9a:ac:0b:da:84:63:53"}}]}'

# floating ips
@app.route("/v2/<project_id>/os-floating-ips", methods=["GET","POST"])
def floating_ips(project_id):

    return '{"floating_ips": []}'

# security groups
@app.route("/v2/<project_id>/os-security-groups", methods=["GET","POST"])
def security_groups(project_id):

    return '{"security_groups": [{"rules": [], "tenant_id": "b61bf0683335448e8f3f778dec2949be", "id": 12, "name": "default", "description": "default"}]}'

# quotas
@app.route("/v2/<project_id>/os-quota-sets/<tenant_id>", methods=["GET","POST"])
def quotas(project_id, tenant_id):
    return '{"quota_set": {"metadata_items": 128, "injected_file_content_bytes": 10240, "injected_files": 5, "gigabytes": 1000, "ram": 66536, "floating_ips": 10, "security_group_rules": 20, "instances": 10, "volumes": 10, "cores": 16, "id": "b61bf0683335448e8f3f778dec2949be", "security_groups": 10}}'

@app.route("/v2/<project_id>/images/<image_id>", methods=["DELETE"])
def delete_image(project_id, image_id):
    return ""

@app.route("/v1/images/<image_id>", methods=["GET", "HEAD"])
def glance_get_image(image_id):
    return (get_image(None, image_id), 200, {"x-image-meta-name": "test"})


@app.route("/v2/<project_id>/images/<image_id>", methods=["GET"])
def get_image(project_id, image_id):

    if image_id not in [
        '0a97a0b3-ee4f-4041-aa0b-b7febb4d5072',
        '754367b0-4fcb-446b-b3b9-da7eefc0399f',
        'd892dfaf-2a5a-4084-bcaa-948e1acf932e'
    ]:
        return ("", 404)

    return '''{ "image": {
        "id": "%s",
        "name": "image-1",
        "updated": "2010-10-10T12:00:00Z",
        "created": "2010-08-10T12:00:00Z",
        "tenant_id": "12345",
        "user_id": "joe",
        "status": "SAVING",
        "progress": 80,
        "minDisk": 5,
        "minRam": 256,
        "links": [
            {
                "rel": "self",
                "href": "http://servers.api.openstack.org/v2/1234/images/52415800-8b69-11e0-9b19-734f5736d2a2"
            },
            {
                "rel": "bookmark",
                "href": "http://servers.api.openstack.org/1234/images/52415800-8b69-11e0-9b19-734f5736d2a2"
            }
        ],
        "OS-DCF:diskConfig": "AUTO" } }''' % image_id


# for the glance
@app.route("/v1/images/detail", methods=["GET"])
def glance_images():
    return (images(None), 200, {'content-type': 'application/json'})


@app.route("/v2/<project_id>/images/detail", methods=["GET"])
def images(project_id):
    return '''{ "images": [ {
            "status": "ACTIVE",
            "updated": "2013-07-17T15:00:26Z",
            "links": [{
                    "href": "http://10.103.114.3:8774/v2/eabcd8f7d78846b9b531e685d835a36a/images/d892dfaf-2a5a-4084-bcaa-948e1acf932e",
                    "rel": "self"
                },
                {
                    "href": "http://10.103.114.3:8774/eabcd8f7d78846b9b531e685d835a36a/images/d892dfaf-2a5a-4084-bcaa-948e1acf932e",
                    "rel": "bookmark"
                },
                {
                    "href": "http://10.103.114.3:9292/eabcd8f7d78846b9b531e685d835a36a/images/d892dfaf-2a5a-4084-bcaa-948e1acf932e",
                    "type": "application/vnd.openstack.image",
                    "rel": "alternate"
                }
            ],
            "id": "d892dfaf-2a5a-4084-bcaa-948e1acf932e",
            "name": "subordinate_v22",
            "created": "2013-07-17T14:56:00Z",
            "minDisk": 0,
            "server": {
                "id": "68620d71-0dc1-4241-ba29-c57407f3c365",
                "links": [
                    {
                        "href": "http://10.103.114.3:8774/v2/servers/68620d71-0dc1-4241-ba29-c57407f3c365",
                        "rel": "self"
                    },
                    {
                        "href": "http://10.103.114.3:8774/servers/68620d71-0dc1-4241-ba29-c57407f3c365",
                        "rel": "bookmark"
                    }
                ]
            },
            "progress": 100,
            "minRam": 0,
            "metadata": {
                "instance_uuid": "68620d71-0dc1-4241-ba29-c57407f3c365",
                "image_location": "snapshot",
                "image_state": "available",
                "user_id": "c7abe460872e4434b13f2c55d642bfb1",
                "image_type": "snapshot",
                "ramdisk_id": null,
                "kernel_id": null,
                "owner_id": "448d7c0ea9954b57b8aeaea8f93ace25"
            }
        },
        {
            "status": "SAVING",
            "updated": "2013-07-17T14:50:54Z",
            "links": [
                {
                    "href": "http://10.103.114.3:8774/v2/eabcd8f7d78846b9b531e685d835a36a/images/754367b0-4fcb-446b-b3b9-da7eefc0399f",
                    "rel": "self"
                },
                {
                    "href": "http://10.103.114.3:8774/eabcd8f7d78846b9b531e685d835a36a/images/754367b0-4fcb-446b-b3b9-da7eefc0399f",
                    "rel": "bookmark"
                },
                {
                    "href": "http://10.103.114.3:9292/eabcd8f7d78846b9b531e685d835a36a/images/754367b0-4fcb-446b-b3b9-da7eefc0399f",
                    "type": "application/vnd.openstack.image",
                    "rel": "alternate"
                }
            ],
            "id": "754367b0-4fcb-446b-b3b9-da7eefc0399f",
            "name": "namenode_image",
            "created": "2013-07-17T14:50:54Z",
            "minDisk": 0,
            "server": {
                "id": "38e56ca4-7990-47ea-bb83-908f795de241",
                "links": [
                    {
                        "href": "http://10.103.114.3:8774/v2/servers/38e56ca4-7990-47ea-bb83-908f795de241",
                        "rel": "self"
                    },
                    {
                        "href": "http://10.103.114.3:8774/servers/38e56ca4-7990-47ea-bb83-908f795de241",
                        "rel": "bookmark"
                    }
                ]
            },
            "progress": 25,
            "minRam": 0,
            "metadata": {
                "image_type": "snapshot",
                "instance_uuid": "38e56ca4-7990-47ea-bb83-908f795de241",
                "user_id": "c7abe460872e4434b13f2c55d642bfb1"
            }
        },
        {
            "status": "ACTIVE",
            "updated": "2013-07-17T14:28:58Z",
            "links": [
                {
                    "href": "http://10.103.114.3:8774/v2/eabcd8f7d78846b9b531e685d835a36a/images/0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
                    "rel": "self"
                },
                {
                    "href": "http://10.103.114.3:8774/eabcd8f7d78846b9b531e685d835a36a/images/0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
                    "rel": "bookmark"
                },
                {
                    "href": "http://10.103.114.3:9292/eabcd8f7d78846b9b531e685d835a36a/images/0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
                    "type": "application/vnd.openstack.image",
                    "rel": "alternate"
                }
            ],
            "id": "0a97a0b3-ee4f-4041-aa0b-b7febb4d5072",
            "name": "hadoop_subordinate4",
            "created": "2013-07-17T14:27:04Z",
            "minDisk": 0,
            "server": {
                "id": "e5beeb57-e2b6-4253-8d65-7a0effe58c93",
                "links": [
                    {
                        "href": "http://10.103.114.3:8774/v2/servers/e5beeb57-e2b6-4253-8d65-7a0effe58c93",
                        "rel": "self"
                    },
                    {
                        "href": "http://10.103.114.3:8774/servers/e5beeb57-e2b6-4253-8d65-7a0effe58c93",
                        "rel": "bookmark"
                    }
                ]
            },
            "progress": 100,
            "minRam": 0,
            "metadata": {
                "instance_uuid": "e5beeb57-e2b6-4253-8d65-7a0effe58c93",
                "image_location": "snapshot",
                "image_state": "available",
                "user_id": "c7abe460872e4434b13f2c55d642bfb1",
                "image_type": "snapshot",
                "ramdisk_id": null,
                "kernel_id": null,
                "owner_id": "8918feb7e13c4fa48a52eb66d14d749b"
            } } ] }'''

# usage
@app.route("/v2/<project_id>/os-simple-tenant-usage", methods=["GET","POST"])
def usage(project_id):
    ''' Might need to change the tenant id to the testing tenant '''
    return '''{
    "tenant_usages": [
        {
            "total_memory_mb_usage": 0.03304106666666667,
            "total_vcpus_usage": 0.000010755555555555555,
            "start": "2013-07-15 19:15:14.297817",
            "tenant_id": "04d63bf492e549eb913800b2628ec771",
            "stop": "2013-07-15 19:15:14.298059",
            "total_hours": 0.0000013444444444444444,
            "total_local_gb_usage": 0.000026888888888888887
        }] }'''


if __name__ == "__main__":
    app.run(host='127.2', debug=True, port=8774)

