# -*- coding: iso-8859-1 -*-
"""A modified dispatcher class, taken from python2.3/asyncore.py.
The following changes were made:

- use new-style object inheritance
- get rid of __getattr__ cludge
- add fileno function
- use True/False
- use webcleaner logging functions
- handle_write_event only calls handle_write if there is pending data
- use a single global socket map

"""
# -*- Mode: Python -*-
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

import os
import socket
import errno

import wc
import wc.configuration
import wc.log


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

def create_socket (family, socktype, sslctx=None):
    """Create a socket with given family and type. If SSL context
       is given an SSL socket is created"""
    sock = socket.socket(family, socktype)
    sock.settimeout(wc.configuration.config['timeout'])
    socktypes_inet = [socket.AF_INET]
    if has_ipv6:
        socktypes_inet.append(socket.AF_INET6)
    if family in socktypes_inet and socktype == socket.SOCK_STREAM:
        # disable NAGLE algorithm, which means sending pending data
        # immediately, possibly wasting bandwidth but improving
        # responsiveness for fast networks
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    if sslctx is not None:
        # make SSL socket
        import OpenSSL
        # XXX has SSL its own timeout?
        sock = OpenSSL.SSL.Connection(sslctx, sock)
    return sock


class Dispatcher (object):
    """dispatch socket events to handler functions"""

    connected = False
    accepting = False
    closing = False
    addr = None


    def __init__ (self, sock=None):
        if sock is not None:
            self.set_socket(sock)
            # I think it should inherit this anyway
            self.socket.setblocking(0)
            self.connected = True
            # XXX Does the constructor require that the socket passed
            # be connected?
            try:
                self.addr = sock.getpeername()
            except socket.error:
                # The addr isn't crucial
                pass
        else:
            self.socket = None

    def __repr__ (self):
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
        socket_map[self.fileno()] = self

    def del_channel (self):
        fd = self.fileno()
        if socket_map.has_key(fd):
            del socket_map[fd]

    def get_family (self, ip):
        if ":" in ip and has_ipv6:
            return socket.AF_INET6
        return socket.AF_INET

    def create_socket (self, family, socktype, sslctx=None):
        self.family_and_type = family, socktype
        self.socket = create_socket(family, socktype, sslctx=sslctx)
        self.socket.setblocking(0)
        if socktype == socket.SOCK_STREAM:
            # disable NAGLE algorithm, which means sending pending data
            # immediately, possibly wasting bandwidth but improving
            # responsiveness for fast networks
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.add_channel()

    def set_socket (self, sock):
        family = socket.AF_INET # XXX how to get socket family?
        socktype = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
        self.family_and_type = family, socktype
        self.socket = sock
        self.add_channel()

    def set_reuse_addr (self):
        # try to re-use a server port if possible
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
        return True

    def writable (self):
        return True

    # ==================================================
    # socket object methods.
    # ==================================================

    def fileno (self):
        return self.socket.fileno()

    def listen (self, num):
        self.accepting = True
        if os.name == 'nt' and num > 5:
            num = 1
        return self.socket.listen(num)

    def bind (self, addr):
        self.addr = addr
        return self.socket.bind(addr)

    def connect (self, addr):
        wc.log.debug(wc.LOG_PROXY, '%s connecting', self)
        self.connected = False
        err = self.socket.connect_ex(addr)
        if err != 0:
            strerr = errno.errorcode[err]
            wc.log.debug(wc.LOG_PROXY, '%s connection error %s', self, strerr)
        # XXX Should interpret Winsock return values
        if err in (errno.EINPROGRESS, errno.EALREADY, errno.EWOULDBLOCK):
            wc.proxy.make_timer(0.2, lambda a=addr: self.check_connect(addr))
        elif err in (0, errno.EISCONN):
            self.addr = addr
            self.connected = True
            wc.log.debug(wc.LOG_PROXY, '%s connected', self)
            self.handle_connect()
        else:
            raise socket.error, (err, errno.errorcode[err])
        return err

    def check_connect (self, addr):
        """Check if the connection is etablished.
           See also http://cr.yp.to/docs/connect.html
        """
        wc.log.debug(wc.LOG_PROXY, '%s check connect', self)
        try:
            self.socket.getpeername()
            self.addr = addr
            self.connected = True
            wc.log.debug(wc.LOG_PROXY, '%s connected', self)
            self.handle_connect()
        except socket.error:
            wc.proxy.make_timer(0.2, lambda a=addr: self.check_connect(addr))

    def accept (self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
            return conn, addr
        except socket.error, why:
            if why[0] == errno.EWOULDBLOCK:
                pass
            else:
                raise

    def send (self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why[0] == errno.EWOULDBLOCK:
                return 0
            if why[0] in (errno.ECONNRESET, errno.ENOTCONN, errno.ESHUTDOWN):
                self.handle_close()
                return 0
            raise

    def recv (self, buffer_size):
        try:
            if self.family_and_type[1] == socket.SOCK_DGRAM:
                data, addr = self.socket.recvfrom(buffer_size)
                if addr != self.addr:
                    raise socket.error, (errno.EREMCHG, str(addr))
            else:
                data = self.socket.recv(buffer_size)
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

    def close (self):
        self.del_channel()
        if hasattr(self.socket, "do_handshake"):
            # shutdown ssl socket
            self.socket.shutdown()
        else:
            try:
                self.socket.shutdown(2)
            except socket.error:
                pass
        self.socket.close()

    def handle_read_event (self):
        if self.accepting:
            # for an accepting socket, getting a read implies
            # that we are connected
            if not self.connected:
                self.connected = True
            self.handle_accept()
        elif not self.connected:
            self.handle_connect()
            self.handle_read()
        else:
            self.handle_read()

    def handle_write_event (self):
        # getting a write implies that we are connected
        if not self.connected:
            self.handle_connect()
        else:
            self.handle_write()

    def handle_expt_event (self):
        self.handle_expt()

    def handle_error (self, what):
        wc.log.exception(wc.LOG_PROXY, "%s %s", self, what)

    def handle_expt (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled exception', self)

    def handle_read (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled read event', self)

    def handle_write (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled write event', self)

    def handle_connect (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled connect event', self)

    def handle_accept (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled accept event', self)

    def handle_close (self):
        wc.log.warn(wc.LOG_PROXY, '%s unhandled close event', self)
        self.close()
