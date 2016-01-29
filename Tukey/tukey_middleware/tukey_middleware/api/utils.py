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

#  Adapted from https://github.com/stackforge/savanna/


import flask
import json
import mimetypes
import socket
import traceback

from novaclient import exceptions as nova_exceptions
from cinderclient import exceptions as cinder_exceptions
from tukey_middleware import utils


TENANT_CLIENTS = ["python-novaclient", "python-cinderclient"]

def set_api_manager(blueprint, registry, logger=utils.get_logger()):
    blueprint.registry = registry
    blueprint.api_manager = ApiManager(registry, logger)
    return blueprint


class ApiManager(object):
    '''  Collection of utility methods for converting
    from the code API to the HTTP API '''

    def __init__(self, registry, logger):
        self.registry = registry
        self.logger = logger

    def tag(self, item, cloud):
        try:
            item["cloud_id"] = cloud.cloud_id
            item["cloud"] = cloud.cloud
        except TypeError as e:
            item = [dict(i.items() + {"cloud_id": cloud.cloud_id,
                "cloud": cloud.cloud}.items())
                    for i in item]
        return item

    def _list_tagged(self, items, cloud):
        for i in items:
            i = self.tag(i, cloud)
        return items

    def list_for_all(self, name, callback):
        '''run method on each cloud then aggregate the results'''
        resources = []
        for cloud in self.registry.all_clouds(flask.g.auth_token):
            try:
                self.logger.debug("listing all for the cloud %s", cloud)
                resources += self._list_tagged(callback(cloud), cloud)
            except socket.error as sock_err:
                self.logger.warn("socket error %s connecting to %s" %
                        (sock_err, cloud))

        items = json.dumps({name: resources})
        return items

    def name_and_cloud_from_name(self, cloud_and_name):
        cloud = cloud_and_name.split('-')[0]
        name = cloud_and_name[len(cloud) + 1:]
        return name, cloud

    def do_action(self, name, item, callback):
        item["name"], cloud_name = self.name_and_cloud_from_name(item["name"])
        cloud = self.registry.get_cloud_by_id(cloud_name, flask.g.auth_token)
        resources = callback(cloud, item)
        return json.dumps({name: resources})

    def get_item(self, name, callback):
        item = None
        for cloud in self.registry.all_clouds(flask.g.auth_token):
            try:
                item = callback(cloud)
                if item:
                    return json.dumps({name: self.tag(item, cloud)})
            except (nova_exceptions.NotFound, cinder_exceptions.NotFound):
                pass
        raise nova_exceptions.NotFound(404)

    def all_clouds(self):
        return self.registry.all_clouds(flask.g.auth_token)

    def get_cloud_by_id(self, cloud_name):
        return self.registry.get_cloud_by_id(cloud_name, flask.g.auth_token)

    def get_cloud_from_item(self, callback):
        item = None
        for cloud in self.registry.all_clouds(flask.g.auth_token):
            try:
                item = callback(cloud)
                if item:
                    return cloud
            except (nova_exceptions.NotFound, cinder_exceptions.NotFound):
                pass
        raise nova_exceptions.NotFound(404)


class Rest(flask.Blueprint):

    def get(self, rule, status_code=200):
        return self._mroute('GET', rule, status_code)

    def post(self, rule, status_code=200):
        return self._mroute('POST', rule, status_code)

    def put(self, rule, status_code=200):
        return self._mroute('PUT', rule, status_code)

    def delete(self, rule, status_code=200):
        return self._mroute('DELETE', rule, status_code)

    def _mroute(self, methods, rule, status_code=None, **kw):
        if type(methods) is str:
            methods = [methods]
        return self.route(rule, methods=methods, status_code=status_code, **kw)


    def route(self, rule, **options):
        status = options.pop('status_code', None)
        file_upload = options.pop('file_upload', False)

        def decorator(func):
            endpoint = options.pop('endpoint', func.__name__)

            def handler(**kwargs):
                # extract response content type
                resp_type = flask.request.accept_mimetypes
                type_suffix = kwargs.pop('resp_type', None)
                if type_suffix:
                    suffix_mime = mimetypes.guess_type("res." + type_suffix)[0]
                    if suffix_mime:
                        resp_type = datastructures.MIMEAccept(
                            [(suffix_mime, 1)])
                flask.request.resp_type = resp_type
                flask.request.file_upload = file_upload

                # update status code
                if status:
                    flask.request.status_code = status

                try:
                    if flask.request.headers["user-agent"] in TENANT_CLIENTS:
                        kwargs.pop("tenant_id")
                except KeyError:
                    kwargs.pop("tenant_id")

                try:
                    flask.g.auth_token = flask.request.headers['X-Auth-Token']
                except Exception:
                    return flask.abort(401)

                if flask.request.method in ['POST', 'PUT']:
                    kwargs['data'] = flask.request.data

                try:
                    return func(**kwargs)
                except nova_exceptions.ClientException as exc:

                    return json.dumps({"error": {"message": exc.message,
                            "code": exc.http_status}}), exc.http_status
                except Exception as e:
                    # Something happened that we didn't expect at all this will
                    # likely need to be debugged and fixed. Let's make sure that
                    # people can see this error without having to look too hard.
                    error_message = traceback.format_exc()
                    print error_message
                    logger = utils.get_logger()
                    logger.error(error_message)

            self.add_url_rule(rule, endpoint, handler, **options)
            f_rule = "/<tenant_id>" + rule
            self.add_url_rule(f_rule, endpoint, handler, **options)
            ext_rule = f_rule + '.<resp_type>'
            self.add_url_rule(ext_rule, endpoint, handler, **options)

            return func

        return decorator
