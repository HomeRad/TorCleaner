# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
SSL client connection.
"""
from . import HttpClient, ClientServerMatchmaker, SslConnection, Allowed
from .. import log, LOG_PROXY
from ..webgui.webconfig import WebConfig


class SslClient(HttpClient.HttpClient, SslConnection.SslConnection):
    """
    Handle SSL server requests, no proxy functionality is here.
    Response data will be encrypted with the WebCleaner SSL server
    certificate. The browser will complain about differing certificate
    domains, which is the price to pay for an SSL gateway.
    Despite having no proxying capabilities, this class is inherited
    from HttpClient.
    """

    def __init__(self, sock, addr):
        super(SslClient, self).__init__(sock, addr)
        self.allow = Allowed.AllowedSslClient()

    def get_default_scheme(self):
        return "https"

    def server_request(self):
        assert self.state == 'receive', \
                      "%s server_request in non-receive state" % self
        log.debug(LOG_PROXY, "%s server_request", self)
        # this object will call server_connected at some point
        ClientServerMatchmaker.ClientServerMatchmaker(
              self, self.request, self.headers, self.content, sslserver=True)

    def handle_local(self, is_public_doc=False):
        assert self.state == 'receive'
        log.debug(LOG_PROXY, '%s handle_local', self)
        form = None
        self.url = "/blocked.html"
        self.headers['Host'] = '%s\r' % self.socket.getsockname()[0]
        WebConfig(self, self.url, form, self.protocol, self.headers).send()

    def mangle_request_headers(self, headers):
        # nothing to do
        pass
