# -*- coding: iso-8859-1 -*-
"""search data stream for virus signatures"""
# Copyright (C) 2004  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import socket, os
from cStringIO import StringIO
from wc import i18n
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, FilterProxyError
from wc.filter.Filter import Filter
from wc.proxy.Connection import RECV_BUFSIZE
from wc.log import *


def strsize (b):
    """return human representation of bytes b"""
    if b<1024:
        return "%d Byte"%b
    b /= 1024.0
    if b<1024:
        return "%.2f kB"%b
    b /= 1024.0
    if b<1024:
        return "%.2f MB"%b
    b /= 1024.0
    return "%.2f GB"


class VirusFilter (Filter):
    """scan for virus signatures in a data stream"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['antivirus']
    # applies to all mime types
    mimelist = []

    # 5 MB maximum file size, everything bigger will generate a proxy error
    MAX_FILE_BYTES = 1024L*1024L*5L


    def filter (self, data, **attrs):
        """write data to scanner and internal buffer"""
        if not attrs.has_key('scanner'):
            return data
        scanner = attrs['scanner']
        buf = attrs['virus_buf']
        size = attrs['virus_buf_size'][0]
        if data:
            if size+len(data) > VirusFilter.MAX_FILE_BYTES:
                self.size_error()
            attrs['virus_buf_size'][0] += len(data)
            scanner.scan(data)
            buf.write(data)
        return ""


    def size_error (self):
        raise FilterProxyError(406, i18n._("Not acceptable"),
                i18n._("Maximum data size (%s) exceeded") % \
                strsize(VirusFilter.MAX_FILE_BYTES))


    def finish (self, data, **attrs):
        """write data to scanner and internal buffer.
           If scanner is clean, return buffered data, else print error
           message and return an empty string."""
        if not attrs.has_key('scanner'):
            return data
        scanner = attrs['scanner']
        buf = attrs['virus_buf']
        size = attrs['virus_buf_size'][0]
        if data:
            if size+len(data) > VirusFilter.MAX_FILE_BYTES:
                self.size_error()
            scanner.scan(data)
            buf.write(data)
        scanner.close()
        for msg in scanner.errors:
            warn(FILTER, "Virus scanner error %r", msg)
        if not scanner.infected:
            data = buf.getvalue()
        else:
            data = ""
            for msg in scanner.infected:
                warn(FILTER, "Found virus %r in %r", msg, attrs['url'])
        buf.close()
        return data


    def getAttrs (self, url, headers):
        """return virus scanner and internal data buffer"""
        d = super(VirusFilter, self).getAttrs(url, headers)
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return d
        conf = get_clamav_conf()
        if conf is not None:
            d['scanner'] = ClamdScanner(conf)
            d['virus_buf'] = StringIO()
            d['virus_buf_size'] = [0]
        return d


class ClamdScanner (object):
    """virus scanner using a clamd daemon process"""

    def __init__ (self, clamav_conf):
        """initialize clamd daemon process sockets"""
        self.infected = []
        self.errors = []
        self.clamav_conf = clamav_conf
        self.sock, host = self.clamav_conf.new_connection()
        self.wsock = self.clamav_conf.new_scansock(self.sock, host)


    def scan (self, data):
        """scan given data for viruses"""
        self.wsock.sendall(data)


    def close (self):
        """get results and close clamd daemon sockets"""
        self.wsock.close()
        data = self.sock.recv(RECV_BUFSIZE)
        while data:
            if "FOUND\n" in data:
                self.infected.append(data)
            if "ERROR\n" in data:
                self.errors.append(data)
            data = self.sock.recv(RECV_BUFSIZE)
        self.sock.close()


_clamav_conf = None
def init_clamav_conf ():
    """initialize clamav configuration"""
    from wc import config
    if not os.path.exists(config['clamavconf']):
        return
    global _clamav_conf
    _clamav_conf = ClamavConfig(config['clamavconf'])


def get_clamav_conf ():
    """get the ClamavConfig instance"""
    return _clamav_conf


def get_sockinfo (host, port=None):
    """return socket.getaddrinfo for given host and port"""
    family, socktype = socket.AF_INET, socket.SOCK_STREAM
    return socket.getaddrinfo(host, port, family, socktype)


class ClamavConfig (dict):
    """clamav configuration wrapper, with clamd connection method"""

    def __init__ (self, filename):
        """parse clamav configuration file"""
        super(ClamavConfig, self).__init__()
        self.parseconf(filename)
        if self.get('ScannerDaemonOutputFormat'):
            raise Exception(i18n._("You have to disable ScannerDaemonOutputFormat"))
        if self.get('TCPSocket') and self.get('LocalSocket'):
            raise Exception(i18n._("Clamd is not configured properly: both TCPSocket and LocalSocket are enabled."))


    def parseconf (self, filename):
        """parse clamav configuration from given file"""
        f = file(filename)
        # yet another config format, sigh
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                # ignore empty lines and comments
                continue
            split = line.split(None, 1)
            if len(split)==1:
                self[split[0]] = True
            else:
                self[split[0]] = split[1]


    def new_connection (self):
        """connect to clamd for stream scanning;
           return connected socket and host"""
        if self.get('LocalSocket'):
            sock = self.create_local_socket()
            host = 'localhost'
        elif self.get('TCPSocket'):
            sock = self.create_tcp_socket()
            host = self.get('TCPAddr', 'localhost')
        else:
            raise Exception(i18n._("You have to enable either TCPSocket or LocalSocket in your Clamd configuration"))
        return sock, host


    def create_local_socket (self):
        """create local socket, connect to it and return socket object"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        addr = self['LocalSocket']
        try:
            sock.connect(addr)
        except socket.error:
            sock.close()
            raise
        return sock


    def create_tcp_socket (self):
        """create tcp socket, connect to it and return socket object"""
        host = self.get('TCPAddr', 'localhost')
        port = int(self['TCPSocket'])
        sockinfo = get_sockinfo(host, port=port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(sockinfo[0][4])
        except socket.error:
            sock.close()
            raise
        return sock


    def new_scansock (self, sock, host):
        """return a connected socket for sending scan data to it"""
        port = None
        try:
            sock.sendall("STREAM")
            port = None
            for i in range(60):
                data = sock.recv(RECV_BUFSIZE)
                i = data.find("PORT")
                if i != -1:
                    port = int(data[i+5:])
                    break
        except socket.error:
            sock.close()
            raise
        if port is None:
            raise Exception(i18n._("Clamd is not ready for stream scanning"))
        sockinfo = get_sockinfo(host, port=port)
        wsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            wsock.connect(sockinfo[0][4])
        except socket.error:
            wsock.close()
            raise
        return wsock

