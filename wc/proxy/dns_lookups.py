# -*- coding: iso-8859-1 -*-
# Copyright (c) 2000, Amit Patel
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of Amit Patel nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
"""
DNS lookup routines
For a high level overview of DNS, see
http://www.rad.com/networks/1998/dns/main.html
"""

import sys
import os
import platform
import time
import socket
import struct
import re
import pprint

import wc.log
import wc.proxy
import timer
import Connection
import wc.dns.resolver
import wc.dns.rdataclass
import wc.dns.rdatatype
import wc.dns.message


resolver = None

def init_resolver ():
    """
    Initialize DNS resolver config. Must be called on startup.
    Should be called on SIGHUP (config reload).
    """
    global resolver
    resolver = wc.dns.resolver.Resolver()


def background_lookup (hostname, callback):
    """
    Return immediately, but call callback with a DnsResponse object later.
    """
    # Hostnames are case insensitive, so canonicalize for lookup purposes
    assert None == wc.log.debug(wc.LOG_DNS,
        'background_lookup %r', hostname.lower())
    DnsExpandHostname(hostname.lower(), callback)


def coerce_hostname (hostname):
    """
    Assure that hostname is a plain string.
    """
    if isinstance(hostname, unicode):
        # XXX encode?
        hostname = str(hostname)
    elif not isinstance(hostname, str):
        raise ValueError("invalid hostname type %r" % hostname)
    return hostname


class DnsResponse (object):
    """
    A DNS answer can be:
     - ('found', [ipaddrs])
     - ('error', why-str)
     - ('redirect', new-hostname)
    """

    def __init__ (self, kind, data):
        """
        Initialize response data.
        """
        self.kind = kind
        self.data = data

    def __repr__ (self):
        """
        Object representation.
        """
        return "DnsResponse(%s, %s)" % (self.kind, self.data)

    def isError (self):
        """
        Return True if dns response is an error.
        """
        return self.kind == 'error'

    def isFound (self):
        """
        Return True if dns response is found valid.
        """
        return self.kind == 'found'

    def isRedirect (self):
        """
        Return True if dns response is a redirection.
        """
        return self.kind == 'redirect'


has_whitespace = re.compile(r'\s').search

class DnsExpandHostname (object):
    """
    Try looking up a hostname and its expansions.
    """

    # This routine calls DnsCache to do the individual lookups
    def __init__ (self, hostname, callback):
        global resolver
        hostname = coerce_hostname(hostname)
        if has_whitespace(hostname):
            # If there's whitespace, it's a copy/paste error
            hostname = re.sub(r'\s+', '', hostname)
        if ".." in hostname:
            # another possible typo
            hostname = re.sub(r'\.\.+', '.', hostname)
        if wc.ip.is_valid_ip(hostname):
            # it is already an ip adress
            callback(hostname, DnsResponse('found', [hostname]))
            return
        self.erroranswer = None # set if one answer failed
        self.hostname = hostname
        self.callback = callback
        self.queries = [hostname] # all queries to be made
        self.answers = {} # Map hostname to DNS answer
        # How long do we wait before trying another expansion?
        self.delay = 3
        if not dnscache.well_known_hosts.has_key(hostname):
            for domain in resolver.search:
                self.queries.append(hostname + "." + domain.to_text(True))
            if hostname.find('.') < 0:
                # it is likely that search domains matter
                self.delay = 0.2
        self.requests = self.queries[1:] # queries we haven't yet made
        # Issue the primary request
        timer.make_timer(0,
                          lambda: dnscache.lookup(hostname, self.handle_dns))
        # and then start another request as well if it's needed
        if self.delay < 1 and len(self.requests) > 0:
            timer.make_timer(self.delay, self.handle_issue_request)

    def handle_issue_request (self):
        assert None == wc.log.debug(wc.LOG_DNS, 'issue_request')
        # Issue one DNS request, and set up a timer to issue another
        if self.requests and self.callback:
            hostname = self.requests[0]
            del self.requests[0]
            timer.make_timer(0,
                          lambda: dnscache.lookup(hostname, self.handle_dns))
            # XXX: Yes, it's possible that several DNS lookups are
            # being executed at once. To avoid that, we could check
            # if there's already a timer for this object ..
            if self.requests:
                timer.make_timer(self.delay, self.handle_issue_request)

    def handle_dns (self, hostname, answer):
        assert None == wc.log.debug(wc.LOG_DNS,
            'handle_dns %r %s', hostname, answer)
        if not self.callback:
            # Already handled this query
            return

        self.answers[hostname] = answer
        while self.queries and self.answers.has_key(self.queries[0]):
            current_query = self.queries[0]
            del self.queries[0]
            answer = self.answers[current_query]
            if not answer.isError():
                callback, self.callback = self.callback, None
                if self.hostname != current_query:
                    callback(self.hostname,
                             DnsResponse('redirect', current_query))
                else:
                    callback(self.hostname, answer)
                return
            elif not self.erroranswer:
                self.erroranswer = answer

        if not self.queries:
            # Someone's still waiting for an answer, and we
            # are expecting no more answers
            callback, self.callback = self.callback, None
            if self.erroranswer:
                answer = self.erroranswer
            else:
                answer = DnsResponse('error', 'host not expanded')
            callback(self.hostname, answer)
            return

        # Since one DNS request is satisfied, issue another
        self.handle_issue_request()


class DnsCache (object):
    """
    Provides a lookup function that will either get a value from the cache
    or initiate a DNS lookup, fill the cache, and return that value.
    """
    # lookup() can create zero or one DnsLookupHostname objects

    ValidCacheEntryExpires = 1800
    InvalidCacheEntryExpires = 0 # dont cache errors

    def __init__ (self):
        self.cache = {} # hostname to DNS answer
        self.expires = {} # hostname to cache expiry time
        self.pending = {} # hostname to [callbacks]
        self.well_known_hosts = {} # hostname to 1, if it's from /etc/hosts
        self.read_localhosts()

    def __repr__ (self):
        return pprint.pformat(self.cache)

    def read_localhosts (self):
        """
        Fill DnsCache with /etc/hosts information.
        """
        if os.name == 'posix':
            filename = '/etc/hosts'
        elif os.name == 'nt':
            windir = os.environ.get('WINDIR', 'c:\\windows')
            release = platform.release()
            if release in ('95', '98', 'Me', 'postMe'):
                # c:\windows\hosts.sam
                filename = os.path.join(windir, "hosts.sam")
            else:
                # Win2000, WinNT, WinXP c:\winnt\system32\drivers\etc\hosts
                filename = os.path.join(windir, 'system32', 'drivers',
                                        'etc', 'hosts')
        else:
            return
        if not os.path.exists(filename):
            return
        for line in open(filename, 'r').readlines():
            line = line.strip()
            if (not line) or line[0]=='#':
                continue
            i = line.find('#')
            if i >= 0:
                line = line[:i] # Comments
            fields = line.split()
            # The first one is the IP address, and then the rest are names
            # These hosts don't expire from our cache
            for name in fields[1:]:
                name = name.lower()
                self.well_known_hosts[name] = 1
                self.cache[name] = DnsResponse('found', [fields[0]])
                self.expires[name] = sys.maxint

    def lookup (self, hostname, callback):
        assert None == wc.log.debug(wc.LOG_DNS,
            'dnscache lookup %r', hostname)
        if hostname[-1:] == '.':
            # We should just remove the trailing '.'
            DnsResponse('redirect', hostname[:-1])
            return

        if self.cache.has_key(hostname):
            if time.time() < self.expires[hostname]:
                # It hasn't expired, so return this answer
                assert None == wc.log.debug(wc.LOG_DNS,
                    'cached! %r', hostname)
                callback(hostname, self.cache[hostname])
                return
            elif not self.cache[hostname].isError():
                # It has expired, but we can use the old value for now
                callback(hostname, self.cache[hostname])
                # We *don't* return; instead, we trigger a new cache
                # fill and use a dummy callback
                callback = lambda h, a: None

        if self.pending.has_key(hostname):
            # Add this guy to the list of interested parties
            self.pending[hostname].append(callback)
            return
        else:
            # Create a new lookup object
            self.pending[hostname] = [callback]
            DnsLookupHostname(hostname, self.handle_dns)

    def handle_dns (self, hostname, answer):
        assert self.pending.has_key(hostname)
        callbacks = self.pending[hostname]
        del self.pending[hostname]
        assert (not answer.isFound() or len(answer.data) > 0), \
               'Received empty DNS lookup .. should be error? %s' % (answer,)
        self.cache[hostname] = answer
        curtime = time.time()
        if answer.isError():
            self.expires[hostname] = curtime+self.InvalidCacheEntryExpires
        else:
            self.expires[hostname] = curtime+self.ValidCacheEntryExpires
        for c in callbacks:
            c(hostname, answer)


class DnsLookupHostname (object):
    """
    Perform DNS lookup on many nameservers.
    """
    # Use a DnsLookupConnection per nameserver

    # We start working with one nameserver per second, as long as we
    # haven't gotten any responses.  For each successive nameserver we
    # set the timeout higher, so that the first nameserver has to try
    # harder.

    def __init__ (self, hostname, callback):
        global resolver
        self.hostname = hostname
        self.callback = callback
        self.nameservers = resolver.nameservers[:]
        self.requests = []
        self.outstanding_requests = 0
        self.issue_request()

    def cancel (self):
        if self.callback:
            self.callback = None
            # Now let's go through and tell all the lookup operations
            # that there's no need to contact us
            for r in self.requests:
                if r.callback == self.handle_dns:
                    r.cancel()
                    self.outstanding_requests -= 1
                assert r.callback is None
            assert self.outstanding_requests == 0

    def issue_request (self):
        if not self.callback:
            return
        if not self.nameservers and not self.outstanding_requests:
            self.callback(self.hostname,
                          DnsResponse('error', 'no nameserver found host'))
            self.callback = None
        elif self.nameservers:
            nameserver = self.nameservers[0]
            del self.nameservers[0]
            # We keep a list of all the requests so we can cancel their
            # DNS lookup when any one of them answers
            self.requests.append(
                DnsLookupConnection(nameserver, self.hostname,
                                    self.handle_dns))
            self.outstanding_requests += 1
            self.requests[-1].TIMEOUT = self.outstanding_requests * 2
            if self.nameservers:
                # Let's create another one soon
                timer.make_timer(1, self.issue_request)

    def handle_dns (self, hostname, answer):
        self.outstanding_requests -= 1
        if not self.callback:
            return
        if not answer.isError():
            self.callback(hostname, answer)
            self.cancel()
        elif self.outstanding_requests == 0:
            self.issue_request()

# Map {nameserver (string) -> whether it accepts TCP requests (bool)}
dns_accepts_tcp = {}

class DnsLookupConnection (Connection.Connection):
    """
    Look up a name by contacting a single nameserver..
    """
    # Switch from UDP to TCP after some time
    PORT = 53
    TIMEOUT = 2 # Resend the request every second

    def __init__ (self, nameserver, hostname, callback):
        self.hostname = hostname
        self.callback = callback
        self.nameserver = nameserver
        self.retries = 0
        self.tcp = False
        super(DnsLookupConnection, self).__init__()
        try:
            self.establish_connection()
        except socket.error:
            # We couldn't even connect .. bah!
            e = sys.exc_info()[1]
            assert None == wc.log.debug(wc.LOG_DNS,
                                "%s connect error %s", self, str(e))
            callback(hostname,
                     DnsResponse('error', 'could not connect to DNS server'))
            self.callback = None

    def establish_connection (self):
        family = self.get_family(self.nameserver)
        if self.tcp:
            self.create_socket(family, socket.SOCK_STREAM)
            self.connect((self.nameserver, self.PORT))
        else:
            self.create_socket(family, socket.SOCK_DGRAM)
            self.connect((self.nameserver, self.PORT))
        timer.make_timer(30, self.handle_connect_timeout)

    def __repr__ (self):
        where = ''
        if self.nameserver != resolver.nameservers[0]:
            where = ' @ %s' % self.nameserver
        retry = ''
        if self.retries != 0:
            retry = ' retry #%s' % self.retries
        if self.tcp:
            conntype = 'TCP'
        else:
            conntype = ''
        return '<%s %d %3s  %s%s%s>' % \
          ('dns-lookup', self.fileno(), conntype, self.hostname, retry, where)

    def cancel (self):
        if self.callback:
            if self.connected:
                self.close()
            self.callback = None

    def handle_connect (self):
        if self.tcp:
            dns_accepts_tcp[self.nameserver] = True
        try:
            self.send_dns_request()
        except wc.dns.exception.DNSException:
            if self.callback:
                e = sys.exc_info()[1]
                assert None == wc.log.debug(wc.LOG_DNS,
                                    "%s DNS error %s", self, str(e))
                self.callback(self.hostname,
                              DnsResponse('error', 'DNS error %s' % str(e)))
                self.callback = None
                self.close()

    def handle_connect_timeout (self):
        # We're trying to perform a TCP connect
        if self.callback and not self.connected:
            dns_accepts_tcp[self.nameserver] = False
            self.callback(self.hostname,
                  DnsResponse('error', 'timed out connecting .. %s' % self))
            self.callback = None

    def send_dns_request (self):
        # Issue the request and set a timeout
        if not self.callback:
            # Only issue if we have someone waiting
            return

        self.rdtype = wc.dns.rdatatype.A
        self.rdclass = wc.dns.rdataclass.IN
        self.query = wc.dns.message.make_query(
                                    self.hostname, self.rdtype, self.rdclass)
        if resolver.keyname is not None:
            self.query.use_tsig(resolver.keyring, resolver.keyname)
        self.query.use_edns(resolver.edns, resolver.ednsflags,
                            resolver.payload)
        assert None == wc.log.debug(wc.LOG_DNS, "%s sending DNS query %s",
                     self, wc.strformat.indent(self.query))
        wire = self.query.to_wire()
        if self.tcp:
            l = len(wire)
            self.send_buffer = struct.pack("!H", l) + wire
        else:
            self.send_buffer = wire
        timer.make_timer(self.TIMEOUT + 0.2*self.retries,
                            self.handle_timeout)

    def handle_timeout (self):
        # The DNS server hasn't responded to us, or we've lost the
        # packet somewhere, so let's try it again, unless the retry
        # count is too large.  Each time we retry, we increase the
        # timeout (see send_dns_request).
        if not self.callback:
            return # It's already handled, so ignore this
        if not self.connected:
            assert None == wc.log.debug(wc.LOG_DNS,
                "%s DNS connect timeout", self)
            self.callback(self.hostname,
                          DnsResponse('error', 'timed out connecting'))
            self.callback = None
            return
        self.retries += 1
        if (not self.tcp) and \
           dns_accepts_tcp.get(self.nameserver, True) and \
           self.retries == 2:
            assert None == wc.log.debug(wc.LOG_DNS,
                "%s switching to TCP", self)
            self.TIMEOUT = 20
            self.close()
            self.tcp = True
            self.establish_connection()
        elif self.retries < 5:
            self.send_dns_request()
        elif not self.tcp and self.retries < 12:
            self.send_dns_request()
        else:
            assert None == wc.log.debug(wc.LOG_DNS, "%s DNS timeout", self)
            if self.callback:
                self.callback(self.hostname,
                              DnsResponse('error', 'timed out'))
                self.callback = None
            if self.connected:
                self.close()

    def process_read (self):
        if not self.callback:
            self.close()
        # Assume that the entire answer comes in one packet
        if self.tcp:
            if len(self.recv_buffer) < 2:
                return
            header = self.recv_buffer[:2]
            (l,) = struct.unpack("!H", header)
            if len(self.recv_buffer) < 2+l:
                return
            self.read(2) # header
            wire = self.read(l)
            try:
                self.socket.shutdown(socket.SHUT_WR)
            except socket.error:
                pass
        else:
            wire = self.read(1024)
        try:
            response = wc.dns.message.from_wire(
                 wire, keyring=self.query.keyring, request_mac=self.query.mac)
        except StandardError:
            wc.log.exception(wc.LOG_DNS, "%s corrupt response %r to query %s",
                             self, wire, wc.strformat.indent(self.query))
            self.handle_error("DNS error: invalid DNS response")
            return
        if not self.query.is_response(response):
            # Oops, this doesn't answer the right question.  This can
            # happen because we're using UDP, and UDP replies might end
            # up in the wrong place: open conn A, send question to A,
            # timeout, send question to A, receive answer, close our
            # object, then open a new conn B, send question to B,
            # but get the OLD answer to A as a reply.  This doesn't happen
            # with TCP but then TCP is slower.

            # Anyway, if this is the answer to a different question,
            # we ignore this read, and let the timeout take its course
            return
        assert None == wc.log.debug(wc.LOG_DNS, "%s got DNS response %s",
                     self, wc.strformat.indent(response))
        # check truncate flag
        if (response.flags & wc.dns.flags.TC) != 0:
            # don't handle truncated packets; try to switch to TCP
            # See http://cr.yp.to/djbdns/notes.html
            if self.tcp:
                # socket.error((84, ''))
                wc.log.info(wc.LOG_DNS,
                            '%s truncated TCP DNS packet from %s',
                            self, self.nameserver)
                self.handle_error("DNS error: truncated TCP packet")
            else:
                wc.log.info(wc.LOG_DNS,
                            '%s truncated UDP DNS packet from %s',
                            self, self.nameserver,)
            # we ignore this read, and let the timeout take its course
            return

        if response.rcode() != wc.dns.rcode.NOERROR:
            callback, self.callback = self.callback, None
            msg = 'not found in response %s' % response
            callback(self.hostname, DnsResponse('error', msg))
            self.close()
            return
        try:
            # construct answer
            name = wc.dns.name.from_text(self.hostname)
            answer = wc.dns.resolver.Answer(
                                   name, self.rdtype, self.rdclass, response)
            assert None == wc.log.debug(wc.LOG_DNS, "%s DNS answer %s",
                         self, wc.strformat.indent(answer))
        except wc.dns.resolver.NoAnswer:
            wc.log.info(wc.LOG_DNS, "%s no answer", self)
            callback, self.callback = self.callback, None
            callback(self.hostname,
                     DnsResponse('error', 'not found with %s' % self))
            self.close()
            return
        ip_addrs = [rdata.address for rdata in answer
                    if hasattr(rdata, "address")]
        callback, self.callback = self.callback, None
        if ip_addrs:
            # Verisign had a catch-all IP 64.94.110.11 for invalid
            # .com and .net domains.
            # This is disabled and left as an example what to do
            # in such cases.
            #if self.hostname[-4:] in ('.com','.net') and \
            #   '64.94.110.11' in ip_addrs:
            #    callback(self.hostname, DnsResponse('error', 'not found'))
            #else:
            callback(self.hostname, DnsResponse('found', ip_addrs))
        else:
            msg = 'not found in answer %s' % answer
            callback(self.hostname, DnsResponse('error', msg))
        self.close()

    def handle_error (self, what):
        super(DnsLookupConnection, self).handle_error(what)
        if self.callback:
            callback, self.callback = self.callback, None
            msg = 'failed lookup in %s' % self
            callback(self.hostname, DnsResponse('error', msg))

    def handle_close (self):
        # If we ever get here, we want to make sure we notify the
        # callbacks so that they don't get stuck
        super(DnsLookupConnection, self).handle_close()
        if self.callback:
            callback, self.callback = self.callback, None
            msg = 'closed with no answer .. %s' % self
            callback(self.hostname, DnsResponse('error', msg))


dnscache = DnsCache()
