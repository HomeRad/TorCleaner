# -*- coding: iso-8859-1 -*-
"""base and utility classes for Proxy testing"""

import sys
import threading
import time
import os
import wc
import tests.StandardTest
import tests.proxy.HttpServer
import tests.proxy.HttpClient


_lock = None
_abort = False

def _acquireLock ():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    global _lock
    if not _lock:
        _lock = threading.RLock()
    if _lock:
        _lock.acquire()


def _releaseLock ():
    """Release the module-level lock acquired by calling _acquireLock()."""
    if _lock:
        _lock.release()


def abort (val=None):
    global _abort
    _acquireLock()
    if val is not None:
        _abort = val
    _releaseLock()
    return _abort


class ProxyTest (tests.StandardTest.StandardTest):
    """Base class for all tests involving a started WebCleaner Proxy.
       After the proxy is started, http clients submit configurable
       request data and check the result validity"""

    def addTest (self, request,
                 client_class=tests.proxy.HttpClient.LogHttpClient,
                 server_class=tests.proxy.HttpServer.LogHttpServer,
                 handler_class=tests.proxy.HttpServer.LogRequestHandler):
        self.proxytests.append((request, client_class,
                                server_class, handler_class))

    def init (self):
        """Starts proxy server."""
        if self.showAll:
            self.log = sys.stdout
        else:
            self.log = file("servertests.txt", 'a')
        self.proxytests = []
        confdir = os.path.join('tests', 'proxy', 'config')
        self.proxyconfig = wc.Configuration(confdir=confdir)
        self.startProxy()

    def shutdown (self):
        """Stop proxy, close log"""
        self.stopProxy()
        if not self.showAll:
            self.log.close()

    def startProxy (self):
        """start proxy"""
        port = self.proxyconfig['port']
        self.log.write("starting WebCleaner proxy on port %d\n"%port)
        confdir = self.proxyconfig.configdir
        kwargs = {"abort": abort, 'filelogs': False, 'confdir': confdir}
        self.proxythread = threading.Thread(target=wc.wstartfunc, kwargs=kwargs)
        self.proxythread.start()
        # wait until proxy is started
        time.sleep(2)

    def stopProxy (self):
        self.log.write("stopping WebCleaner proxy\n")
        abort(True)
        time.sleep(1)

    def testProxy (self):
        """proxy test with client/server request"""
        for proxytest in self.proxytests:
            request = proxytest[0]
            client_class = proxytest[1]
            server_class = proxytest[2]
            handler_class = proxytest[3]
            self.log.write("running test %r\n"%request.name())
            try:
                tests.proxy.HttpServer.startServer(self.log,
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
                tests.proxy.HttpServer.stopServer(self.log)

