# use a modified dispatcher class, taken from python2.3/asyncore.py
# - use new-style object inheritance
# - get rid of __getattr__ cludge
# - add fileno function
# - use True/False
# - use webcleaner logging functions
# - handle_write_event only calls handle_write if there is pending data
# - use a single global socket map

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

from wc.log import *
from OpenSSL import SSL
import sys, os, socket
from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
     ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

# map of sockets
socket_map = {}

def create_socket (family, socktype, sslctx=None):
    if sslctx is not None:
        sock = SSL.Connection(sslctx, socket.socket(family, socktype))
    else:
        sock = socket.socket(family, socktype)
        if family==socket.AF_INET and socktype==socket.SOCK_STREAM:
            # disable NAGLE algorithm, which means sending pending data
            # immediately, possibly wasting bandwidth but improving
            # responsiveness for fast networks
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sock


class Dispatcher (object):

    connected = False
    accepting = False
    closing = False
    addr = None

    def __init__ (self, sock=None):
        if sock:
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
        # On some systems (RH10) id() can be a negative number. 
        # work around this.
        MAX = 2L*sys.maxint+1
        return '<%s at %#x>' % (' '.join(status), id(self)&MAX)


    def add_channel (self):
        socket_map[self.fileno()] = self


    def del_channel (self):
        fd = self.fileno()
        if socket_map.has_key(fd):
            del socket_map[fd]


    def create_socket (self, family, socktype, sslctx=None):
        self.family_and_type = family, socktype
        self.socket = create_socket(family, socktype, sslctx=sslctx)
        self.socket.setblocking(0)
        self.add_channel()


    def set_socket (self, sock):
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


    if os.name == 'mac':
        # The macintosh will select a listening socket for
        # write if you let it.  What might this mean?
        def writable (self):
            return not self.accepting
    else:
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


    def connect (self, address):
        self.connected = False
        err = self.socket.connect_ex(address)
        # XXX Should interpret Winsock return values
        if err in (EINPROGRESS, EALREADY, EWOULDBLOCK):
            return
        if err in (0, EISCONN):
            self.addr = address
            self.connected = True
            self.handle_connect()
        else:
            raise socket.error, (err, errorcode[err])


    def accept (self):
        # XXX can return either an address pair or None
        try:
            conn, addr = self.socket.accept()
            return conn, addr
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                pass
            else:
                raise socket.error, why


    def send (self, data):
        try:
            result = self.socket.send(data)
            return result
        except socket.error, why:
            if why[0] == EWOULDBLOCK:
                return 0
            if why[0] in (ECONNRESET, ENOTCONN, ESHUTDOWN):
                self.handle_close()
                return 0
            raise


    def recv (self, buffer_size):
        try:
            data = self.socket.recv(buffer_size)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0.
                self.handle_close()
                return ''
            else:
                return data
        except socket.error, why:
            # winsock sometimes throws ENOTCONN
            if why[0] in (ECONNRESET, ENOTCONN, ESHUTDOWN):
                self.handle_close()
                return ''
            else:
                raise socket.error, why


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
            self.connected = True
            self.handle_read()
        else:
            self.handle_read()


    def handle_write_event (self):
        # getting a write implies that we are connected
        if not self.connected:
            self.handle_connect()
            self.connected = True
        else:
            self.handle_write()


    def handle_expt_event (self):
        self.handle_expt()


    def handle_error (self):
        nil, t, v, tbinfo = compact_traceback()
        # sometimes a user repr method will crash.
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)
        error(PROXY, '%s uncaptured python exception, closing (%s:%s %s)',
                     t, v, tbinfo)
        self.close()


    def handle_expt (self):
        warn(PROXY, '%s unhandled exception', self)


    def handle_read (self):
        warn(PROXY, '%s unhandled read event', self)


    def handle_write (self):
        warn(PROXY, '%s unhandled write event', self)


    def handle_connect (self):
        warn(PROXY, '%s unhandled connect event', self)


    def handle_accept (self):
        warn(PROXY, '%s unhandled accept event', self)


    def handle_close (self):
        warn(PROXY, '%s unhandled close event', self)
        self.close()
