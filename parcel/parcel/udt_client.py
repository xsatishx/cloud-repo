from .client import Client
from .cparcel import lib
from .log import get_logger

import urlparse

# Logging
log = get_logger('client')


class UDTClient(Client):

    def __init__(self, proxy_host, proxy_port, remote_uri,
                 external_proxy=False, *args, **kwargs):
        if not remote_uri.startswith('http'):
            remote_uri = 'https://{}'.format(remote_uri)
        if not external_proxy:
            # Create a local UDT proxy that translates TCP to UDT
            self.start_proxy_server(proxy_host, proxy_port, remote_uri)
        local_uri = self.construct_local_uri(
            proxy_host, proxy_port, remote_uri)
        super(UDTClient, self).__init__(local_uri, *args, **kwargs)

    def construct_local_uri(self, proxy_host, proxy_port, remote_uri):
        """Given proxy settings and remote_uri, construct the uri where the
        proxy request will be sent

        """
        p = urlparse.urlparse(remote_uri)
        scheme = p.scheme or 'https'
        local_uri = '{}://{}:{}{}'.format(
            scheme, proxy_host, proxy_port, p.path)
        return local_uri

    def start_proxy_server(self, proxy_host, proxy_port, remote_uri):
        """Bind proxy.

        """

        p = urlparse.urlparse(remote_uri)
        port = p.port or 9000
        log.info('Binding proxy server {}:{} -> {}:{}'.format(
            str(proxy_host), str(proxy_port), str(p.hostname), str(port)))
        proxy = lib.tcp2udt_start(
            str(proxy_host), str(proxy_port), str(p.hostname), str(port))
        assert proxy == 0, 'Proxy failed to start'
