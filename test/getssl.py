#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""print headers of an url"""

import httplib
import urlparse
import sys
import socket
from OpenSSL import SSL

def request (url, port):
    """httplib request"""
    parts = urlparse.urlsplit(url)
    host = parts[1]
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection("localhost:%d"%port)
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    if req.status==302:
        url = req.msg.get('Location')
        print "redirected to", url
        request(url, port)
    else:
        print "HTTP version", req.version, req.status, req.reason
        print req.msg
        print req.read()


def rawrequest (url, port):
    """raw request with PyOpenSSL"""
    from wc.proxy.Dispatcher import create_socket
    from wc.proxy.ssl import get_clientctx
    parts = urlparse.urlsplit(url)
    host = parts[1]
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    sock = create_socket(socket.AF_INET, socket.SOCK_STREAM, sslctx=get_clientctx())
    addr = (socket.gethostbyname('localhost'), port)
    sock.connect(addr)
    sock.set_connect_state()
    sock.do_handshake()
    sock.write('GET %s HTTP/1.1\r\n' % url)
    sock.write('Host: %s\r\n' % host)
    sock.write('\r\n')
    while True:
        try:
            print repr(sock.recv(80))
        except SSL.ZeroReturnError:
            # finished
            break
    sock.shutdown()
    sock.close()


def rawrequest2 (url, port):
    """raw request with socket.ssl"""
    from wc.proxy.Dispatcher import create_socket
    parts = urlparse.urlsplit(url)
    host = parts[1]
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    _sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (socket.gethostbyname('localhost'), port)
    _sock.connect(addr)
    sock = socket.ssl(_sock)
    sock.write('GET %s HTTP/1.1\r\n' % url)
    sock.write('Host: %s\r\n' % host)
    sock.write('\r\n')
    while True:
        try:
            print repr(sock.read(80))
        except socket.sslerror, msg:
            print "Oops", msg
            break
    _sock.close()


def rawrequest3 (url, port):
    """raw request with proxy CONNECT protocol"""
    from wc.proxy.Dispatcher import create_socket
    from urllib import splitnport
    parts = urlparse.urlsplit(url)
    host, sslport = splitnport(parts[1], 443)
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    _sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (socket.gethostbyname('localhost'), port)
    _sock.connect(addr)
    _sock.send('CONNECT %s:%d HTTP/1.1\r\n' % (host, sslport))
    _sock.send('User-Agent: getssl\r\n')
    _sock.send('\r\n')
    buf = ""
    while True:
        buf += _sock.recv(1024)
        if "\r\n\r\n" in buf:
            break
    print repr(buf)
    print "initiating SSL handshake"
    sock = socket.ssl(_sock)
    print "write SSL request...",
    sock.write("GET %s HTTP/1.1\r\n" % url)
    sock.write("Host: %s\r\n" % host)
    sock.write("\r\n")
    print " ok."
    while True:
        try:
            print repr(sock.read(80))
        except socket.sslerror, msg:
            # msg should be (6, 'TLS/SSL connection has been closed')
            if msg[0] != 6:
                print "Oops", msg
            break
    _sock.close()


def _main ():
    """USAGE: test/run.sh test/getssl.py <https url>"""
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    import wc
    wc.configuration.config = wc.configuration.Configuration()
    port = config['port']
    sslport = config['sslport']
    request(sys.argv[1], sslport)
    #rawrequest(sys.argv[1], sslport)
    #rawrequest2(sys.argv[1], sslport)
    rawrequest3(sys.argv[1], port)


if __name__=='__main__':
    _main()
