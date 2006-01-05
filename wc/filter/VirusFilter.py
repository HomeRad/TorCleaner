# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
Search data stream for virus signatures.
"""

import socket
import os
import cStringIO as StringIO

import wc
import wc.configuration
import wc.strformat
import wc.log
import wc.filter
import wc.filter.Filter
from wc.proxy.Dispatcher import create_socket


class VirusFilter (wc.filter.Filter.Filter):
    """
    Scan for virus signatures in a data stream.
    """

    enable = True

    # 5 MB maximum file size, everything bigger will generate a proxy error
    MAX_FILE_BYTES = 1024L*1024L*5L

    def __init__ (self):
        """
        Init stages and mimes.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ['antivirus']
        super(VirusFilter, self).__init__(stages=stages, rulenames=rulenames)

    def filter (self, data, attrs):
        """
        Write data to scanner and internal buffer.
        """
        if not attrs.has_key('virus_scanner'):
            return data
        scanner = attrs['virus_scanner']
        buf = attrs['virus_buf']
        size = attrs['virus_buf_size'][0]
        data_length = len(data)
        if size+data_length > VirusFilter.MAX_FILE_BYTES:
            self.size_error()
        attrs['virus_buf_size'][0] += data_length
        scanner.scan(data)
        buf.write(data)
        return ""

    def size_error (self):
        """
        Raise an exceptionto cause a 406 HTTP return code.
        """
        wc.log.warn(wc.LOG_FILTER, "Virus filter size exceeded.")
        raise wc.filter.FilterProxyError((406, _("Not acceptable"),
                _("Maximum data size (%s) exceeded") % \
                wc.strformat.strsize(VirusFilter.MAX_FILE_BYTES)))

    def finish (self, data, attrs):
        """
        Write data to scanner and internal buffer.
        If scanner is clean, return buffered data, else print error
        message and return an empty string.
        """
        if not attrs.has_key('virus_scanner'):
            assert wc.log.debug(wc.LOG_FILTER, "No virus scanner found.")
            return data
        scanner = attrs['virus_scanner']
        buf = attrs['virus_buf']
        size = attrs['virus_buf_size'][0]
        if data:
            if size+len(data) > VirusFilter.MAX_FILE_BYTES:
                self.size_error()
            scanner.scan(data)
            buf.write(data)
        scanner.close()
        for msg in scanner.errors:
            wc.log.warn(wc.LOG_FILTER, "Virus scanner error %r", msg)
        if scanner.infected:
            data = ""
            for msg in scanner.infected:
                wc.log.warn(wc.LOG_FILTER, "Found virus %r in %r",
                            msg, attrs['url'])
        else:
            data = buf.getvalue()
        buf.close()
        return data

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        Return virus scanner and internal data buffer.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(VirusFilter, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        if not rules:
            return
        conf = get_clamav_conf()
        if conf is not None:
            attrs['virus_scanner'] = ClamdScanner(conf)
            attrs['virus_buf'] = StringIO.StringIO()
            attrs['virus_buf_size'] = [0]


class ClamdScanner (object):
    """
    Virus scanner using a clamd daemon process.
    """

    def __init__ (self, clamav_conf):
        """
        Initialize clamd daemon process sockets.
        """
        self.infected = []
        self.errors = []
        self.sock, self.host = clamav_conf.new_connection()
        self.sock_rcvbuf = \
             self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        self.wsock = self.new_scansock()

    def new_scansock (self):
        """
        Return a connected socket for sending scan data to it.
        """
        port = None
        try:
            self.sock.sendall("STREAM")
            port = None
            for i in range(60):
                data = self.sock.recv(self.sock_rcvbuf)
                i = data.find("PORT")
                if i != -1:
                    port = int(data[i+5:])
                    break
        except socket.error:
            self.sock.close()
            raise
        if port is None:
            raise Exception(_("Clamd is not ready for stream scanning"))
        sockinfo = get_sockinfo(self.host, port=port)
        wsock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            wsock.connect(sockinfo[0][4])
        except socket.error:
            wsock.close()
            raise
        return wsock

    def scan (self, data):
        """
        Scan given data for viruses.
        """
        self.wsock.sendall(data)

    def close (self):
        """
        Get results and close clamd daemon sockets.
        """
        self.wsock.close()
        data = self.sock.recv(self.sock_rcvbuf)
        while data:
            if "FOUND\n" in data:
                self.infected.append(data)
            if "ERROR\n" in data:
                self.errors.append(data)
            data = self.sock.recv(self.sock_rcvbuf)
        self.sock.close()


_clamav_conf = None
def init_clamav_conf (conf):
    """
    Initialize clamav configuration.
    """
    if not conf:
        # clamav was not configured
        return
    if os.path.exists(conf):
        global _clamav_conf
        _clamav_conf = ClamavConfig(conf)
    else:
        wc.log.warn(wc.LOG_FILTER, "No ClamAV config file found at %r.", conf)


def get_clamav_conf ():
    """
    Get the ClamavConfig instance.
    """
    return _clamav_conf


def get_sockinfo (host, port=None):
    """
    Return socket.getaddrinfo for given host and port.
    """
    family, socktype = socket.AF_INET, socket.SOCK_STREAM
    return socket.getaddrinfo(host, port, family, socktype)


class ClamavConfig (dict):
    """
    Clamav configuration wrapper, with clamd connection method.
    """

    def __init__ (self, filename):
        """
        Parse clamav configuration file.
        """
        super(ClamavConfig, self).__init__()
        self.parseconf(filename)
        if self.get('ScannerDaemonOutputFormat'):
            raise Exception(
                        _("You have to disable ScannerDaemonOutputFormat"))
        if self.get('TCPSocket') and self.get('LocalSocket'):
            raise Exception(_("Clamd is not configured properly: " \
                              "both TCPSocket and LocalSocket are enabled."))

    def parseconf (self, filename):
        """
        Parse clamav configuration from given file.
        """
        f = file(filename)
        # yet another config format, sigh
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                # ignore empty lines and comments
                continue
            split = line.split(None, 1)
            if len(split) == 1:
                self[split[0]] = True
            else:
                self[split[0]] = split[1]

    def new_connection (self):
        """
        Connect to clamd for stream scanning.

        @return: tuple (connected socket, host)
        """
        if self.get('LocalSocket'):
            host = 'localhost'
            sock = self.create_local_socket()
        elif self.get('TCPSocket'):
            host = self.get('TCPAddr', 'localhost')
            sock = self.create_tcp_socket(host)
        else:
            raise Exception(_("You have to enable either TCPSocket " \
                              "or LocalSocket in your Clamd configuration"))
        return sock, host

    def create_local_socket (self):
        """
        Create local socket, connect to it and return socket object.
        """
        sock = create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        addr = self['LocalSocket']
        try:
            sock.connect(addr)
        except socket.error:
            sock.close()
            raise
        return sock

    def create_tcp_socket (self, host):
        """
        Create tcp socket, connect to it and return socket object.
        """
        port = int(self['TCPSocket'])
        sockinfo = get_sockinfo(host, port=port)
        sock = create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(sockinfo[0][4])
        except socket.error:
            sock.close()
            raise
        return sock
