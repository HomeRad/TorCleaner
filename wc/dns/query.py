# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003, 2004 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Talk to a DNS server."""

from __future__ import generators

import errno
import select
import socket
import struct
import sys
import time

import wc.dns.exception
import wc.dns.inet
import wc.dns.name
import wc.dns.message
import wc.dns.rdataclass
import wc.dns.rdatatype

class UnexpectedSource(wc.dns.exception.DNSException):
    """Raised if a query response comes from an unexpected address or port."""
    pass

class BadResponse(wc.dns.exception.FormError):
    """Raised if a query response does not respond to the question asked."""
    pass


def _compute_expiration(timeout):
    if timeout is None:
        return None
    else:
        return time.time() + timeout


def _wait_for(ir, iw, ix, expiration):
    if expiration is None:
        timeout = None
    else:
        timeout = expiration - time.time()
        if timeout <= 0.0:
            raise wc.dns.exception.Timeout
    if timeout is None:
        (r, w, x) = select.select(ir, iw, ix)
    else:
        (r, w, x) = select.select(ir, iw, ix, timeout)
    if len(r) == 0 and len(w) == 0 and len(x) == 0:
        raise wc.dns.exception.Timeout

def _wait_for_readable(s, expiration):
    _wait_for([s], [], [s], expiration)


def _wait_for_writable(s, expiration):
    _wait_for([], [s], [s], expiration)


def udp(q, where, timeout=None, port=53, af=None):
    """Return the response obtained after sending a query via UDP.

    @param q: the query
    @type q: wc.dns.message.Message
    @param where: where to send the message
    @type where: string containing an IPv4 or IPv6 address
    @param timeout: The number of seconds to wait before the query times out.
    If None, the default, wait forever.
    @type timeout: float
    @param port: The port to which to send the message.  The default is 53.
    @type port: int
    @param af: the address family to use.  The default is None, which
    causes the address family to use to be inferred from the form of of where.
    If the inference attempt fails, AF_INET is used.
    @type af: int
    @rtype: wc.dns.message.Message object
    """
    wire = q.to_wire()
    if af is None:
        try:
            af = wc.dns.inet.af_for_address(where)
        except:
            af = wc.dns.inet.AF_INET
    if af == wc.dns.inet.AF_INET:
        destination = (where, port)
    elif af == wc.dns.inet.AF_INET6:
        destination = (where, port, 0, 0)
    s = socket.socket(af, socket.SOCK_DGRAM, 0)
    try:
        expiration = _compute_expiration(timeout)
        s.setblocking(0)
        _wait_for_writable(s, expiration)
        s.sendto(wire, destination)
        _wait_for_readable(s, expiration)
        (wire, from_address) = s.recvfrom(65535)
    finally:
        s.close()
    if from_address != destination:
        raise UnexpectedSource
    r = wc.dns.message.from_wire(wire, keyring=q.keyring, request_mac=q.mac)
    if not q.is_response(r):
        raise BadResponse
    return r

def _net_read(sock, count, expiration):
    """Read the specified number of bytes from sock.  Keep trying until we
    either get the desired amount, or we hit EOF.
    A Timeout exception will be raised if the operation is not completed
    by the expiration time.
    """
    s = ''
    while count > 0:
        _wait_for_readable(sock, expiration)
        n = sock.recv(count)
        if n == '':
            raise EOFError
        count -= len(n)
        s +=  n
    return s

def _net_write(sock, data, expiration):
    """Write the specified data to the socket.
    A Timeout exception will be raised if the operation is not completed
    by the expiration time.
    """
    current = 0
    l = len(data)
    while current < l:
        _wait_for_writable(sock, expiration)
        current += sock.send(data[current:])

def _connect(s, address):
    try:
        s.connect(address)
    except socket.error:
        (ty, v) = sys.exc_info()[:2]
        if v[0] != errno.EINPROGRESS and v[0] != errno.EWOULDBLOCK:
            raise ty, v

def tcp(q, where, timeout=None, port=53, af=None):
    """Return the response obtained after sending a query via TCP.

    @param q: the query
    @type q: wc.dns.message.Message object
    @param where: where to send the message
    @type where: string containing an IPv4 or IPv6 address
    @param timeout: The number of seconds to wait before the query times out.
    If None, the default, wait forever.
    @type timeout: float
    @param port: The port to which to send the message.  The default is 53.
    @type port: int
    @param af: the address family to use.  The default is None, which
    causes the address family to use to be inferred from the form of of where.
    If the inference attempt fails, AF_INET is used.
    @type af: int
    @rtype: wc.dns.message.Message object"""

    wire = q.to_wire()
    if af is None:
        try:
            af = wc.dns.inet.af_for_address(where)
        except:
            af = wc.dns.inet.AF_INET
    if af == wc.dns.inet.AF_INET:
        destination = (where, port)
    elif af == wc.dns.inet.AF_INET6:
        destination = (where, port, 0, 0)
    s = socket.socket(af, socket.SOCK_STREAM, 0)
    try:
        expiration = _compute_expiration(timeout)
        s.setblocking(0)
        _connect(s, destination)

        l = len(wire)

        # copying the wire into tcpmsg is inefficient, but lets us
        # avoid writev() or doing a short write that would get pushed
        # onto the net
        tcpmsg = struct.pack("!H", l) + wire
        _net_write(s, tcpmsg, expiration)
        ldata = _net_read(s, 2, expiration)
        (l,) = struct.unpack("!H", ldata)
        wire = _net_read(s, l, expiration)
    finally:
        s.close()
    r = wc.dns.message.from_wire(wire, keyring=q.keyring, request_mac=q.mac)
    if not q.is_response(r):
        raise BadResponse
    return r

def xfr(where, zone, rdtype=wc.dns.rdatatype.AXFR, rdclass=wc.dns.rdataclass.IN,
        timeout=None, port=53, keyring=None, keyname=None, relativize=True,
        af=None, lifetime=None):
    """Return a generator for the responses to a zone transfer.

    @param where: where to send the message
    @type where: string containing an IPv4 or IPv6 address
    @param zone: The name of the zone to transfer
    @type zone: wc.dns.name.Name object or string
    @param rdtype: The type of zone transfer.  The default is
    wc.dns.rdatatype.AXFR.
    @type rdtype: int or string
    @param rdclass: The class of the zone transfer.  The default is
    wc.dns.rdatatype.IN.
    @type rdclass: int or string
    @param timeout: The number of seconds to wait for each response message.
    If None, the default, wait forever.
    @type timeout: float
    @param port: The port to which to send the message.  The default is 53.
    @type port: int
    @param keyring: The TSIG keyring to use
    @type keyring: dict
    @param keyname: The name of the TSIG key to use
    @type keyname: wc.dns.name.Name object or string
    @param relativize: If True, all names in the zone will be relativized to
    the zone origin.
    @type relativize: bool
    @param af: the address family to use.  The default is None, which
    causes the address family to use to be inferred from the form of of where.
    If the inference attempt fails, AF_INET is used.
    @type af: int
    @param lifetime: The total number of seconds to spend doing the transfer.
    If None, the default, then there is no limit on the time the transfer may
    take.
    @type lifetime: float
    @rtype: generator of wc.dns.message.Message objects."""

    if isinstance(zone, str):
        zone = wc.dns.name.from_text(zone)
    q = wc.dns.message.make_query(zone, rdtype, rdclass)
    if not keyring is None:
        q.use_tsig(keyring, keyname)
    wire = q.to_wire()
    if af is None:
        try:
            af = wc.dns.inet.af_for_address(where)
        except:
            af = wc.dns.inet.AF_INET
    if af == wc.dns.inet.AF_INET:
        destination = (where, port)
    elif af == wc.dns.inet.AF_INET6:
        destination = (where, port, 0, 0)
    s = socket.socket(af, socket.SOCK_STREAM, 0)
    expiration = _compute_expiration(lifetime)
    _connect(s, destination)
    l = len(wire)
    tcpmsg = struct.pack("!H", l) + wire
    _net_write(s, tcpmsg, expiration)
    done = False
    seen_soa = False
    if relativize:
        origin = zone
        oname = wc.dns.name.empty
    else:
        origin = None
        oname = zone
    tsig_ctx = None
    first = True
    while not done:
        mexpiration = _compute_expiration(timeout)
        if mexpiration is None or mexpiration > expiration:
            mexpiration = expiration
        ldata = _net_read(s, 2, mexpiration)
        (l,) = struct.unpack("!H", ldata)
        wire = _net_read(s, l, mexpiration)
        r = wc.dns.message.from_wire(wire, keyring=q.keyring, request_mac=q.mac,
                                  xfr=True, origin=origin, tsig_ctx=tsig_ctx,
                                  multi=True, first=first)
        tsig_ctx = r.tsig_ctx
        first = False
        if not seen_soa:
            if not r.answer or r.answer[0].name != oname:
                raise wc.dns.exception.FormError
            rrset = r.answer[0]
            if rrset.rdtype != wc.dns.rdatatype.SOA:
                raise wc.dns.exception.FormError
            seen_soa = True
            if len(r.answer) > 1 and r.answer[-1].name == oname:
                rrset = r.answer[-1]
                if rrset.rdtype == wc.dns.rdatatype.SOA:
                    if q.keyring and not r.had_tsig:
                        raise wc.dns.exception.FormError, "missing TSIG"
                    done = True
        elif r.answer and r.answer[-1].name == oname:
            rrset = r.answer[-1]
            if rrset.rdtype == wc.dns.rdatatype.SOA:
                if q.keyring and not r.had_tsig:
                    raise wc.dns.exception.FormError, "missing TSIG"
                done = True
        yield r
    s.close()
