# -*- coding: iso-8859-1 -*-
"""base and utility classes for Proxy testing"""

import unittest, os, sys, threading, time
import wc
import HttpServer, HttpClient
from wc.log import *
from wc.update import update_filter, update_ratings

class ProxyTest (unittest.TestCase):
    """Base class for all tests involving a started WebCleaner Proxy.
       After the proxy is started, http clients submit configurable
       request data and check the result validity"""

    def __init__ (self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName=methodName)
        #self.log = file("proxytest.txt", 'w')
        self.log = sys.stdout
        self.proxytests = []
        self.proxyconfig = wc.Configuration()

    def addTest (self, request,
                 client_class=HttpClient.LogHttpClient,
                 server_class=HttpServer.LogHttpServer,
                 handler_class=HttpServer.LogRequestHandler):
        self.proxytests.append((request, client_class,
                                server_class, handler_class))

    def setUp (self):
        """Starts proxy server."""
        self.startProxy()

    def tearDown (self):
        """Stop proxy, close log"""
        self.stopProxy()
        #self.log.close()

    def startProxy (self):
        port = self.proxyconfig['port']
        self.log.write("starting WebCleaner proxy on port %d\n"%port)
        kwargs = {'stoppable': True}
        self.proxythread = threading.Thread(target=wc.wstartfunc, kwargs=kwargs)
        self.proxythread.start()
        # wait until proxy is started
        running = False
        while not running:
            running = hasattr(wc.config, "get_abort")
            if not running:
                self.log.write("wait until proxy is started\n")
                time.sleep(1)

    def stopProxy (self):
        self.log.write("stopping proxy")
        wc.config.set_abort(True)
        time.sleep(1)
        self.log.write(".\n")

    def testProxy (self):
        """send request through proxy to server"""
        for proxytest in self.proxytests:
            request = proxytest[0]
            client_class = proxytest[1]
            server_class = proxytest[2]
            handler_class = proxytest[3]
            self.log.write("running test %r\n"%request.name())
            serverthread = None
            try:
                serverthread = HttpServer.startServer(self.log,
                                           server_class=server_class,
                                           handler_class=handler_class)
                client = client_class(self.log, self.proxyconfig)
                # send request
                client.doRequest(request)
                # read response
                client.doResponse()
                # check test
                result, msg = request.check_response(client.response)
                if result!=request.SUCCESS:
                    raise self.failureException, msg
            finally:
                # stop server
                HttpServer.stopServer(self.log)

