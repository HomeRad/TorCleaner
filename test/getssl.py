#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""print headers of an url"""

import httplib, urlparse, sys, os, socket
from OpenSSL import SSL

def request (url):
    parts = urlparse.urlsplit(url)
    host = parts[1]
    port = 8443
    if os.environ.get("WC_DEVELOPMENT", 0):
        port += 1
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection("localhost:%s"%port)
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    if req.status==302:
        url = req.msg.get('Location')
        print "redirected to", url
        return request(url)
    return req


def rawrequest (url):
    from wc.proxy.Dispatcher import create_socket
    from wc.proxy.ssl import get_clientctx
    parts = urlparse.urlsplit(url)
    host = parts[1]
    port = 8443
    if os.environ.get("WC_DEVELOPMENT", 0):
        port += 1
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    sock = create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=get_clientctx())
    addr = (socket.gethostbyname('localhost'), port)
    sock.connect(addr)
    sock.set_connect_state()
    sock.do_handshake()
    sock.write('GET %s HTTP/1.1\r\n' % url)
    sock.write('Host: %s\r\n' % host)
    sock.write('Content-Length: 0\r\n')
    sock.write('\r\n')
    while True:
        try:
            print sock.recv(1024)
        except SSL.ZeroReturnError, msg:
            # finished
            break
    sock.shutdown()
    sock.close()


def rawrequest2 (url):
    from wc.proxy.Dispatcher import create_socket
    parts = urlparse.urlsplit(url)
    host = parts[1]
    port = 8443
    if os.environ.get("WC_DEVELOPMENT", 0):
        port += 1
    path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    _sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (socket.gethostbyname('localhost'), port)
    _sock.connect(addr)
    sock = socket.ssl(_sock)
    sock.write('GET %s HTTP/1.1\r\n' % url)
    sock.write('Host: %s\r\n' % host)
    sock.write('Content-Length: 0\r\n')
    sock.write('\r\n')
    while True:
        try:
            print sock.read(1024)
        except socket.sslerror, msg:
            break
    _sock.close()


def _main ():
    """USAGE: test/getssl.py <https url>"""
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    #req = request(sys.argv[1])
    #print "HTTP version", req.version, req.status, req.reason
    #print req.msg
    #print req.read()
    rawrequest(sys.argv[1])


if __name__=='__main__':
    _main()
