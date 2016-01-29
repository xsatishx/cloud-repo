from .client import Client


class HTTPClient(Client):

    def __init__(self, uri, *args, **kwargs):
        super(HTTPClient, self).__init__(uri, *args, **kwargs)
