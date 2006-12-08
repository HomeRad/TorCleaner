# -*- coding: iso-8859-1 -*-
#   Id: asyncore.py,v 2.51 2000/09/07 22:29:26 rushing Exp
#   Author: Sam Rushing <rushing@nightmare.com>

# ======================================================================
# Copyright 1996 by Sam Rushing
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Sam
# Rushing not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# SAM RUSHING DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL SAM RUSHING BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ======================================================================
"""
A modified dispatcher class, taken from python2.3/asyncore.py.
The following changes were made:
 - use new-style object inheritance
 - get rid of __getattr__ cludge
 - add fileno function
 - use True/False
 - use webcleaner logging functions
 - handle_write_event only calls handle_write if there is pending data
 - use a single global socket map
"""

import os
import socket
import select
import errno

import wc.configuration
import wc.log
import timer


# map of sockets
socket_map = {}

# test for IPv6, both in Python build and in kernel build
has_ipv6 = False
if socket.has_ipv6:
    # python has ipv6 compiled in, but the operating system also
    # has to support it.
    try:
        socket.socket(socket.AF_INET6, socket.SOCK_STREAM).close()
        has_ipv6 = True
    except socket.error, msg:
        # only catch these one:
        # socket.error: (97, 'Address family not supported by protocol')
        # socket.error: (10047, 'Address family not supported by protocol')
        if msg[0] not in (97, 10047):
            raise

def create_socket (family, socktype, proto=0):
    """
    Create a socket with given family and type. If SSL context
    is given an SSL socket is created.
    """
    sock = socket.socket(family, socktype, proto=proto)
    # XXX disable custom timeouts for now; enable in Python 2.5
    #sock.settimeout(wc.configuration.config['timeout'])
    socktypes_inet = [socket.AF_INET]
    if has_ipv6:
        socktypes_inet.append(socket.AF_INET6)
    if family in socktypes_inet and socktype == socket.SOCK_STREAM:
        # disable NAGLE algorithm, which means sending pending data
        # immediately, possibly wasting bandwidth but improving
        # responsiveness for fast networks
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sock


class Dispatcher (object):
    """
    Dispatch socket events to handler functions.
    """

    def __init__ (self, sock=None, socktype=None):
        """
        Initialize connection.

        @param sock: connected socket
        @type sock: socket.socket or None
        """
        self.connected = False
        self.accepting = False
        self.closing = False
        self.addr = None
        self.socket = None
        self._fileno = -1
        if sock is not None:
            self.set_socket(sock, socktype)
            # I think it should inherit this anyway
            self.socket.setblocking(0)
            self.connected = True
            self.addr = sock.getpeername()

    def __repr__ (self):
        """
        Connection info string.
        """
        status = [self.__class__.__module__+"."+self.__class__.__name__]
        if self.accepting and self.addr:
            status.append('listening')
        elif self.connected:
            status.append('connected')
        if self.addr is not None:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
        return '<%s at %#x>' % (' '.join(status), id(self))

    def add_channel (self):
        """
        Add this connection to the socket map.
        """
        socket_map[self.fileno()] = self

    def del_channel (self):
        """
        Delete this connection from socket map.
        """
        fd = self.fileno()
        if socket_map.has_key(fd):
            del socket_map[fd]

    def get_family (self, ip):
        """
        Get socket family for ip.

        @return: socket.AF_INET or socket.AF_INET6
        @rtype: int
        """
        if ":" in ip and has_ipv6:
            return socket.AF_INET6
        return socket.AF_INET

    def create_socket (self, family, socktype):
        """
        Create a new socket.
        """
        self.set_socket(create_socket(family, socktype), socktype)

    def set_socket (self, sock, socktype):
        """
        Set new socket.
        """
        sock.setblocking(0)
        self.socket = sock
        self.socktype = socktype
        self._fileno = sock.fileno()
        self.socket_rcvbuf = \
             sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        self.socket_sndbuf = \
             sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        self.add_channel()

    def set_reuse_addr (self):
        """
        Try to re-use a server port if possible.
        """
        try:
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR,
                self.socket.getsockopt(socket.SOL_SOCKET,
                                       socket.SO_REUSEADDR) | 1
                )
        except socket.error:
            pass

    # ==================================================
    # predicates for select()
    # these are used as filters for the lists of sockets
    # to pass to select().
    # ==================================================

    def readable (self):
        """
        Check if connection is readable.

        @return: True
        @rtype: bool
        """
        return True

    def writable (self):
        """
        Check if connection is writable.

        @return: True
        @rtype: bool
        """
        return True

    # ==================================================
    # socket object methods.
    # ==================================================

    def fileno (self):
        """
        Get socket file number.

        @return: socket file number
        @rtype: int
        """
        return self._fileno

    def listen (self, num):
        """
        Let the socket listen to a port.

        @param num: port number
        @type num: int
        @return: result of socket.listen() call
        """
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 1
        return self.socket.listen(num)

    def bind (self, addr):
        """
        Bind the socket to an address.

        @param addr: the (host, port) address to bind to
        @type addr: tuple (string, int)
        @return: result of socket.bind() call
        """
        self.addr = addr
        return self.socket.bind(addr)

    def connect (self, addr):
        """
        Try to connect to a host. If connecting is in progress (indicated
        by EINPROGRESS or EWOULDBLOCK), try again sometime later.
        Calls handle_connect() if already connected.

        @param addr: (host, port) address
        @type addr: tuple (string, int)
        @raise: socket.error on error
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s connecting', self)
        self.connected = False
        self.connect_checks = 0
        err = self.socket.connect_ex(addr)
        if err != 0:
            strerr = os.strerror(err)
            assert None == wc.log.debug(wc.LOG_PROXY,
                '%s connection error %d (%s)', self, err, strerr)
        if err in (errno.EINPROGRESS, errno.EWOULDBLOCK):
            # Connection is in progress, check the connect condition later.
            def recheck ():
                self.check_connect(addr)
            timer.make_timer(0.2, recheck)
        elif err in (0, errno.EISCONN):
            # Connected!
            self.addr = addr
            self.connected = True
            assert None == wc.log.debug(wc.LOG_PROXY, '%s connected', self)
            self.handle_connect()
        else:
            # Note that EALREADY is handled as an error. We don't want
            # to connect to an already-connected socket.
            raise socket.error((err, errno.errorcode[err]))
        return err

    def check_connect (self, addr):
        """
        Check if the connection is etablished.
        See also http://cr.yp.to/docs/connect.html and connect(2) manpage.
        """
        assert None == wc.log.debug(wc.LOG_PROXY, '%s check connect', self)
        self.connect_checks += 1
        if self.connect_checks >= 50:
            assert None == wc.log.debug(wc.LOG_PROXY,
                '%s connect timed out', self)
            self.handle_close()
            return
        def recheck ():
            self.check_connect(addr)
        try:
            (r, w, e) = select.select([], [self.fileno()], [], 0.2)
        except select.error, why:
            # not yet ready
            assert None == wc.log.debug(wc.LOG_PROXY,
                         '%s connect not ready %s', self, str(why))
            timer.make_timer(0.2, recheck)
            return
        if self.fileno() not in w:
            # not yet ready
            assert None == wc.log.debug(wc.LOG_PROXY, '%s not writable', self)
            timer.make_timer(0.2, recheck)
            return
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err == 0:
            self.addr = addr
            self.connected = True
            assert None == wc.log.debug(wc.LOG_PROXY, '%s connected', self)
            self.handle_connect()
        elif err in (errno.EINPROGRESS, errno.EWOULDBLOCK):
            assert None == wc.log.debug(wc.LOG_PROXY,
                '%s connect status in progress/would block', self)
            timer.make_timer(0.2, recheck)
        else:
            strerr = os.strerror(err)
            wc.log.info(wc.LOG_PROXY, '%s connect error %s', self, strerr)
            self.handle_error(_("Connect error %s.") % strerr)

    def accept (self):
        """
        Accept a new connection on the socket.

        @return: a pair (socket, addr) or None if accepting would block
        @rtype tuple or None
        @raise: socket.error on error
        """
        # XXX can return either an address pair or None
        try:
            return self.socket.accept()
        except socket.error, why:
            if why[0] == errno.EWOULDBLOCK:
                pass
            else:
                raise

    def send (self, data, flags=0):
        """
        Send given data on socket.

        @param data: data to send
        @type data: string
        @return: result of socket.send() call
        @raise: socket.error on error
        """
        try:
            result = self.socket.send(data, flags)
            return result
        except socket.error, why:
            if why[0] == errno.EWOULDBLOCK:
                return 0
            if why[0] in (errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN):
                self.handle_close()
                return 0
            raise

    def recv (self, buffer_size, flags=0):
        """
        Try to receive up to given buffer_size bytes from the socket.

        @return: received data
        @rtype: string
        """
        try:
            data = self.recv_bytes(buffer_size, flags=flags)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return ''
            else:
                return data
        except socket.error, why:
            # winsock sometimes throws errno.ENOTCONN
            if why[0] in (errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN):
                self.handle_close()
                return ''
            else:
                raise

    def recv_bytes (self, buffer_size, flags=0):
        """
        Receive up to given buffer_size bytes from the socket.

        @return: received data
        @rtype: string
        @raise: socket.error on error
        """
        if self.socktype != socket.SOCK_DGRAM:
            data = self.socket.recv(buffer_size, flags)
        else:
            data, addr = self.socket.recvfrom(buffer_size)
            if addr != self.addr:
                # answer was for someone else
                raise socket.error((errno.EREMCHG, str(addr)))
        return data

    def close (self):
        """
        Close the socket.
        """
        self.del_channel()
        if hasattr(self.socket, "do_handshake"):
            # shutdown ssl socket
            self.socket.shutdown()
        else:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
        self.socket.close()

    def handle_read_event (self):
        """
        Handle a read by calling handle_read().
        """
        if self.accepting:
            # for an accepting socket, getting a read implies
            # that we are connected
            if not self.connected:
                self.connected = True
            self.handle_accept()
        elif self.connected:
            self.handle_read()
        else:
            self.handle_connect()
            self.handle_read()

    def handle_write_event (self):
        """
        Handle write event by calling handle_write() or if not yet
        connected handle_connect().
        """
        # getting a write implies that we are connected
        if self.connected:
            self.handle_write()
        else:
            self.handle_connect()

    def handle_expt_event (self):
        """
        Handle exception event. Default is to call handle_expt().
        """
        self.handle_expt()

    def handle_error (self, what):
        """
        Handle error. Default is to log an error message.
        """
        wc.log.exception(wc.LOG_PROXY, "%s %s", self, what)

    def handle_expt (self):
        """
        Handle socket exception. Default is to log a warning with the error.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled exception', self)

    def handle_read (self):
        """
        Handle read event. Should be overridden in subclass.
        Logs a warning as default.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled read event', self)

    def handle_write (self):
        """
        Handle write event. Should be overridden in subclass.
        Logs a warning as default.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled write event', self)

    def handle_connect (self):
        """
        Handle connect event. Should be overridden in subclass.
        Logs a warning as default.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled connect event', self)

    def handle_accept (self):
        """
        Handle accept event. Should be overridden in subclass.
        Logs a warning as default.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled accept event', self)

    def handle_close (self):
        """
        Handle close event. Logs a warning and closes the socket as default.
        """
        wc.log.warn(wc.LOG_PROXY, '%s unhandled close event', self)
        self.close()
