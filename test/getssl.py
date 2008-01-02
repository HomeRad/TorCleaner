#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2008 Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Print headers of an URL.
"""

import httplib
import urlparse
import sys
import socket
import select
import errno
import time

def request1 (url, port):
    """httplib request"""
    parts = urlparse.urlsplit(url)
    host = parts[1]
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection(host)
    h.connect()
    h.putrequest("GET", url, skip_host=0)
    h.endheaders()
    req = h.getresponse()
    if req.status == 302:
        url = req.msg.get('Location')
        print "redirected to", url
        request1(url, port)
    else:
        print "HTTP version", req.version, req.status, req.reason
        print req.msg
        req.read()


def proxyrequest1 (url, port):
    """httplib request"""
    parts = urlparse.urlsplit(url)
    host = parts[1]
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    h = httplib.HTTPSConnection("localhost:%d" % port)
    h.set_debuglevel(1)
    h.connect()
    h.putrequest("GET", url, skip_host=1)
    h.putheader("Host", host)
    h.endheaders()
    req = h.getresponse()
    if req.status == 302:
        url = req.msg.get('Location')
        print "redirected to", url
        proxyrequest1(url, port)
    else:
        print "HTTP version", req.version, req.status, req.reason
        print req.msg
        print req.read()


def proxyrequest2 (url, port):
    """raw request with PyOpenSSL"""
    from wc.proxy.Dispatcher import create_socket
    from wc.proxy.ssl import get_clientctx
    parts = urlparse.urlsplit(url)
    host = parts[1]
    addr = (host, port)
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    while True:
        err = sock.connect_ex(addr)
        if err in (errno.EINPROGRESS, errno.EWOULDBLOCK):
            continue
        elif err in (0, errno.EISCONN, errno.EALREADY):
            break
        else:
            raise socket.error, (err, errno.errorcode[err])
    sslctx = get_clientctx('localconfig')
    import OpenSSL.SSL
    sock = OpenSSL.SSL.Connection(sslctx, sock)
    sock.set_connect_state()
    while True:
        try:
            sock.do_handshake()
            break
        except OpenSSL.SSL.WantReadError:
            time.sleep(0.2)
        except OpenSSL.SSL.WantWriteError:
            time.sleep(0.2)
    sock_write(sock, 'GET %s HTTP/1.1\r\n' % url)
    sock_write(sock, 'Host: %s\r\n' % host)
    sock_write(sock, '\r\n')
    while True:
        try:
            want_read(sock)
        except OpenSSL.SSL.ZeroReturnError:
            # finished
            break
    sock.shutdown()
    sock.close()

def sock_write (sock, data):
    import OpenSSL.SSL
    while True:
        try:
            num_written = sock.write(data)
            print num_written, "bytes written"
            break
        except OpenSSL.SSL.WantReadError:
            want_read(sock)

def want_read (sock):
    import OpenSSL.SSL
    r, w, e = select.select([sock], [], [], 0.2)
    if not r:
        return
    try:
        print repr(sock.read(1024))
    except OpenSSL.SSL.WantReadError:
        pass


def proxyrequest3 (url, port):
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
            print "Error", msg
            break
    _sock.close()


def proxyrequest4 (url, port):
    """raw request with proxy CONNECT protocol"""
    from wc.proxy.Dispatcher import create_socket
    from urllib import splitnport
    parts = urlparse.urlsplit(url)
    host, sslport = splitnport(parts[1], 443)
    #path = urlparse.urlunsplit(('', '', parts[2], parts[3], parts[4]))
    _sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (socket.gethostbyname('localhost'), port)
    _sock.connect(addr)
    _sock.send('CONNECT %s:%d HTTP/1.0\r\n' % (host, sslport))
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
    """
    USAGE: scripts/run.sh test/getssl.py <https url>
    """
    if len(sys.argv) != 2:
        print _main.__doc__.strip()
        sys.exit(1)
    import wc.configuration
    wc.configuration.config = wc.configuration.init("localconfig")
    #port = wc.configuration.config['port']
    sslport = 443
    #sslport = wc.configuration.config['sslport']
    print "Get %s (port %d)" % (sys.argv[1], sslport)
    #request1(sys.argv[1], sslport)
    #proxyrequest1(sys.argv[1], sslport)
    proxyrequest2(sys.argv[1], sslport)
    #proxyrequest3(sys.argv[1], sslport)
    #proxyrequest4(sys.argv[1], port)


if __name__ == '__main__':
    _main()
