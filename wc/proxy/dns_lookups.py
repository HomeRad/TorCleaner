# -*- coding: iso-8859-1 -*-
"""dns lookup routines
For a high level overview of DNS, see
http://www.rad.com/networks/1998/dns/main.html
"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sys
import os
import time
import socket
import re
import pprint
import wc.proxy
import wc.proxy.dns
import wc.proxy.Connection
import wc.ip
from wc.log import *

###################### configuration ########################

class DnsConfig (object):
    """DNS configuration storage"""
    pass


def init_dns_resolver ():
    """initialize this module, filling the DNS config"""
    DnsConfig.nameservers = []
    DnsConfig.search_domains = []
    DnsConfig.search_patterns = ('www.%s.com', 'www.%s.net', 'www.%s.org')
    if os.name=='posix':
        init_dns_resolver_posix()
    elif os.name=='nt':
        init_dns_resolver_nt()
    else:
        # other platforms not supported (what about Mac?)
        pass
    if not DnsConfig.search_domains:
        DnsConfig.search_domains.append('')
    if not DnsConfig.nameservers:
        DnsConfig.nameservers.append('127.0.0.1')
    debug(DNS, "nameservers %s", DnsConfig.nameservers)
    debug(DNS, "search domains %s", DnsConfig.search_domains)
    # re-read config every 10 minutes
    # disabled, there is a reload option in webcleaner
    #make_timer(600, init_dns_resolver)


def init_dns_resolver_posix ():
    "Set up the DnsLookupConnection class with /etc/resolv.conf information"
    if not os.path.exists('/etc/resolv.conf'):
        return
    for line in file('/etc/resolv.conf', 'r').readlines():
        line = line.strip()
        if (not line) or line[0]==';' or line[0]=='#':
            continue
        m = re.match(r'^search\s+(\.?.+)$', line)
        if m:
            for domain in m.group(1).split():
                DnsConfig.search_domains.append('.'+domain.lower())
        m = re.match(r'^nameserver\s+(\S+)\s*$', line)
        if m: DnsConfig.nameservers.append(m.group(1))


def init_dns_resolver_nt ():
    """get DNS config from Windows registry settings"""
    import winreg
    key = None
    try:
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
               r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
    except EnvironmentError:
        try: # for Windows ME
            key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\VxD\MSTCP")
        except EnvironmentError:
            pass
    if key:
        for server in winreg.stringdisplay(key.get("NameServer", "")):
            if server:
                DnsConfig.nameservers.append(str(server))
        for item in winreg.stringdisplay(key.get("SearchList", "")):
            if item:
                DnsConfig.search_domains.append(str(item))
        if not DnsConfig.nameservers:
            # XXX the proper way to test this is to search for
            # the "EnableDhcp" key in the interface adapters...
            for server in winreg.stringdisplay(key.get("DhcpNameServer", "")):
                if server:
                    DnsConfig.nameservers.append(str(server))
            for item in winreg.stringdisplay(key.get("DhcpDomain", "")):
                if item:
                    DnsConfig.search_domains.append(str(item))

    try: # search adapters
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
  r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\DNSRegisteredAdapters")
        for subkey in key.subkeys():
            values = subkey.get('DNSServerAddresses', "")
            for server in winreg.binipdisplay(values):
                if server:
                    DnsConfig.nameservers.append(server)
    except EnvironmentError:
        pass

    try: # search interfaces
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces")
        for subkey in key.subkeys():
            for server in winreg.stringdisplay(subkey.get('NameServer', '')):
                if server:
                    DnsConfig.nameservers.append(server)
    except EnvironmentError:
        pass


init_dns_resolver()

######################################################################

def background_lookup (hostname, callback):
    "Return immediately, but call callback with a DnsResponse object later"
    # Hostnames are case insensitive, so canonicalize for lookup purposes
    debug(DNS, 'background_lookup %r', hostname.lower())
    DnsExpandHostname(hostname.lower(), callback)


class DnsResponse (object):
    """ A DNS answer can be:
        ('found', [ipaddrs])
        ('error', why-str)
        ('redirect', new-hostname)"""

    def __init__ (self, kind, data):
        """initialize response data"""
        self.kind = kind
        self.data = data


    def __repr__ (self):
        """object representation"""
        return "DnsResponse(%s, %s)" % (self.kind, self.data)


    def isError (self):
        """return True if dns response is an error"""
        return self.kind == 'error'


    def isFound (self):
        """return True if dns response is found valid"""
        return self.kind == 'found'


    def isRedirect (self):
        """return True if dns response is a redirection"""
        return self.kind == 'redirect'


has_whitespace = re.compile(r'\s').search

class DnsExpandHostname (object):
    "Try looking up a hostname and its expansions"

    # This routine calls DnsCache to do the individual lookups
    def __init__ (self, hostname, callback):
        self.erroranswer = None # set if one answer failed
        self.hostname = hostname
        self.callback = callback
        self.queries = [hostname] # all queries to be made
        self.answers = {} # Map hostname to DNS answer
        self.delay = 0.2 # How long do we wait before trying another expansion?
        if not dnscache.well_known_hosts.has_key(hostname):
            for domain in DnsConfig.search_domains:
                self.queries.append(hostname + domain)
            if hostname.find('.') < 0 and hostname.find(':') < 0:
                # If there's no dot, we should try expanding patterns
                for pattern in DnsConfig.search_patterns:
                    self.queries.append(pattern % hostname)
            else:
                # But if there is a dot, let's increase the delay
                # because it's very likely that none of the
                # search_domains matter.
                self.delay = 3
        if has_whitespace(hostname):
            # If there's whitespace, it's almost certainly a copy/paste error,
            # so also try the same thing with whitespace removed
            self.queries.append(re.sub(r'\s+', '', hostname))
        if ".." in hostname:
            # another possible typo
            self.queries.append(re.sub(r'\.\.+', '.', hostname))
        self.requests = self.queries[1:] # queries we haven't yet made
        # Issue the primary request
        make_timer(0, lambda h=hostname, s=self:
                   dnscache.lookup(h, s.handle_dns))
        # and then start another request as well
        if self.delay < 1: # (it's likely to be needed)
            make_timer(self.delay, self.handle_issue_request)


    def handle_issue_request (self):
        debug(DNS, 'issue_request')
        # Issue one DNS request, and set up a timer to issue another
        if self.requests and self.callback:
            request = self.requests[0]
            del self.requests[0]
            make_timer(0, lambda r=request, s=self:
                       dnscache.lookup(r, s.handle_dns))

            # XXX: Yes, it's possible that several DNS lookups are
            # being executed at once.  To avoid that, we could check
            # if there's already a timer for this object ..
            if self.requests: make_timer(self.delay, self.handle_issue_request)


    def handle_dns (self, hostname, answer):
        debug(DNS, 'handle_dns %r %s', hostname, answer)
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
                    callback(self.hostname, DnsResponse('redirect', current_query))
                else:
                    callback(self.hostname, answer)
                break
            elif not self.erroranswer:
                self.erroranswer = answer

        if self.callback and not self.queries:
            # Someone's still waiting for an answer, and we
            # are expecting no more answers
            callback, self.callback = self.callback, None
            if self.erroranswer:
                answer = self.erroranswer
            else:
                answer = DnsResponse('error', 'host not expanded')
            callback(self.hostname, answer)

        # Since one DNS request is satisfied, issue another
        self.handle_issue_request()


class DnsCache (object):
    """Provides a lookup function that will either get a value from the cache
    or initiate a DNS lookup, fill the cache, and return that value"""
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
        "Fill DnsCache with /etc/hosts information"
        if os.name=='posix':
            filename = '/etc/hosts'
        elif os.name=='nt':
            # XXX find correct %WINDIR% and place for hosts.sam
            # Win98SE: c:\windows\hosts.sam
            # Win2000: c:\winnt\system32\drivers\etc\hosts
            # WinNT: ???
            # WinXP: ???
            filename = 'c:\\windows\\hosts.sam'
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
        debug(DNS, 'dnscache lookup %r', hostname)
        # see if hostname is already a resolved IP address
        hostname, numeric = wc.ip.expand_ip(hostname)
        if numeric:
            callback(hostname, DnsResponse('found', [hostname]))
            return

        if hostname[-1:] == '.':
            # We should just remove the trailing '.'
            DnsResponse('redirect', hostname[:-1])
            return

        if len(hostname) > 100:
            # It's too long .. assume it's an error
            callback(hostname, DnsResponse('error', 'hostname %r too long'%hostname))
            return
        
        if self.cache.has_key(hostname):
            if time.time() < self.expires[hostname]:
                # It hasn't expired, so return this answer
                debug(DNS, 'cached! %r', hostname)
                callback(hostname, self.cache[hostname])
                return
            elif not self.cache[hostname].isError():
                # It has expired, but we can use the old value for now
                callback(hostname, self.cache[hostname])
                # We *don't* return; instead, we trigger a new cache
                # fill and use a dummy callback
                callback = lambda h,a:None

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
        if not answer.isError():
            self.expires[hostname] = time.time()+self.ValidCacheEntryExpires
        else:
            self.expires[hostname] = time.time()+self.InvalidCacheEntryExpires

        for c in callbacks:
            c(hostname, answer)


class DnsLookupHostname (object):
    "Perform DNS lookup on many nameservers"
    # Use a DnsLookupConnection per nameserver
    
    # We start working with one nameserver per second, as long as we
    # haven't gotten any responses.  For each successive nameserver we
    # set the timeout higher, so that the first nameserver has to try
    # harder.

    def __init__ (self, hostname, callback):
        self.hostname = hostname
        self.callback = callback
        self.nameservers = DnsConfig.nameservers[:]
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
            self.callback(self.hostname, DnsResponse('error', 'no nameserver found host'))
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
                make_timer(1, self.issue_request)


    def handle_dns (self, hostname, answer):
        self.outstanding_requests -= 1
        if not self.callback:
            return
        if not answer.isError():
            self.callback(hostname, answer)
            self.cancel()
        elif not self.outstanding_requests:
            self.issue_request()


class DnsLookupConnection (wc.proxy.Connection.Connection):
    "Look up a name by contacting a single nameserver"
    # Switch from UDP to TCP after some time
    PORT = 53
    TIMEOUT = 2 # Resend the request every second
    accepts_tcp = {} # Map nameserver to 0/1, whether it accepts TCP requests


    def __init__ (self, nameserver, hostname, callback):
        self.hostname = hostname
        self.callback = callback
        self.nameserver = nameserver
        self.retries = 0
        self.conntype = 'udp'
        super(DnsLookupConnection, self).__init__()
        try:
            self.establish_connection()
        except socket.error:
            # We couldn't even connect .. bah!
            callback(hostname, DnsResponse('error', 'could not connect to DNS server'))
            self.callback = None


    def establish_connection (self):
        if self.conntype == 'tcp':
            wc.proxy.create_inet_socket(self, socket.SOCK_STREAM)
            self.connect((self.nameserver, self.PORT))
            make_timer(30, self.handle_connect_timeout)
            # XXX: we have to fill the buffer because otherwise we
            # won't consider this object writable, and we will never
            # call handle_connect.  This needs to be fixed somehow.
            self.send_dns_request()
        else:
            wc.proxy.create_inet_socket(self, socket.SOCK_DGRAM)
            self.connect((self.nameserver, self.PORT))
            self.send_dns_request()


    def __repr__ (self):
        where = ''
        if self.nameserver != DnsConfig.nameservers[0]:
            where = ' @ %s'%self.nameserver
        retry = ''
        if self.retries != 0:
            retry = ' retry #%s'%self.retries
        conntype = ''
        if self.conntype == 'tcp':
            conntype = 'TCP'
        return '<%s %3s  %s%s%s>' % ('dns-lookup', conntype, self.hostname, retry, where)


    def cancel (self):
        if self.callback:
            if self.connected: self.close()
            self.callback = None


    def handle_connect (self):
        # For TCP requests only
        DnsLookupConnection.accepts_tcp[self.nameserver] = 1


    def handle_connect_timeout (self):
        # We're trying to perform a TCP connect
        if self.callback and not self.connected:
            DnsLookupConnection.accepts_tcp[self.nameserver] = 0
            self.callback(self.hostname,
                  DnsResponse('error', 'timed out connecting .. %s' % self))
            self.callback = None
            return


    def send_dns_request (self):
        # Issue the request and set a timeout
        if not self.callback: return # Only issue if we have someone waiting
        msg = wc.proxy.dns.Lib.Mpacker()
        msg.addHeader(0, 0, wc.proxy.dns.Opcode.QUERY, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
        # XXX could send Type.AAAA for IPv6 nameservers, but who decides when
        # to do that? This is the dilemma with IPv6 not having an update
        # solution...
        msg.addQuestion(self.hostname, wc.proxy.dns.Type.A, wc.proxy.dns.Class.IN)
        msg = msg.getbuf()
        if self.conntype == 'tcp':
            self.send_buffer = wc.proxy.dns.Lib.pack16bit(len(msg))+msg
        else:
            self.send_buffer = msg
        make_timer(self.TIMEOUT + 0.2*self.retries, self.handle_timeout)


    def handle_timeout (self):
        # The DNS server hasn't responded to us, or we've lost the
        # packet somewhere, so let's try it again, unless the retry
        # count is too large.  Each time we retry, we increase the
        # timeout (see send_dns_request).
        if not self.callback:
            return # It's already handled, so ignore this
        if not self.connected:
            self.callback(self.hostname, DnsResponse('error', 'timed out connecting'))
            self.callback = None
            return
        self.retries += 1
        if (self.conntype == 'udp' and
            self.accepts_tcp.get(self.nameserver, 1) and
            self.retries == 1):
            # Switch to TCP
            self.TIMEOUT = 20
            self.close()
            self.conntype = 'tcp'
            self.establish_connection()
        elif self.retries < 5:
            self.send_dns_request()
        elif self.conntype == 'udp' and self.retries < 12:
            self.send_dns_request()
        else:
            if self.callback:
                self.callback(self.hostname, DnsResponse('error', 'timed out'))
                self.callback = None
            if self.connected: self.close()


    def process_read (self):
        # Assume that the entire answer comes in one packet
        if self.conntype == 'tcp':
            if len(self.recv_buffer) < 2: return
            header = self.recv_buffer[:2]
            count = wc.proxy.dns.Lib.unpack16bit(header)
            if len(self.recv_buffer) < 2+count: return
            self.read(2) # header
            data = self.read(count)
            try:
                self.socket.shutdown(1)
            except socket.error:
                pass
        else:
            data = self.read(1024)

        msg = wc.proxy.dns.Lib.Munpacker(data)
        (id, qr, opcode, aa, tc, rd, ra, z, rcode,
         qdcount, ancount, nscount, arcount) = msg.getHeader()
        if tc:
            # dont handle truncated packets; try to switch to TCP
            # See http://cr.yp.to/djbdns/notes.html
            if self.conntype == 'tcp':
                # socket.error((84, ''))
                error(PROXY, 'Truncated TCP DNS packet: %s from %s for %r',
                      tc, self.nameserver, self.hostname)
                self.handle_error("dns error")
            else:
                warn(PROXY, 'truncated UDP DNS packet: %s from %s for %r',
                     tc, self.nameserver, self.hostname)
            # we ignore this read, and let the timeout take its course
            return

        if rcode:
            if self.callback:
                callback, self.callback = self.callback, None
                callback(self.hostname,
                         DnsResponse('error', 'not found .. %s' % self))
            self.close()
            return

        for dummy in range(qdcount):
            hostname, _, _ = msg.getQuestion()
            if hostname == self.hostname:
                # This DOES answer the question we asked
                break
        else:
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

        ip_addrs = []
        for dummy in range(ancount):
            name, type, klass, ttl, rdlength = msg.getRRheader()
            mname = 'get%sdata' % wc.proxy.dns.Type.typestr(type)
            if hasattr(msg, mname): data = getattr(msg, mname)()
            else: data = msg.getbytes(rdlength)
            if type == wc.proxy.dns.Type.A:
                ip_addrs.append(data)
            elif type == wc.proxy.dns.Type.AAAA:
                ip_addrs.append(data)
            elif type == wc.proxy.dns.Type.CNAME:
                # XXX: should we do anything with CNAMEs?
                debug(DNS, 'cname record %s=%r', self.hostname, data)
                pass
        # Ignore (nscount) authority records
        # Ignore (arcount) additional records
        if self.callback:
            callback, self.callback = self.callback, None
            if ip_addrs:
                # doh, verisign has a catch-all ip 64.94.110.11 for
                # .com and .net domains
                if self.hostname[-4:] in ('.com','.net') and \
                   '64.94.110.11' in ip_addrs:
                    callback(self.hostname, DnsResponse('error', 'not found'))
                else:
                    callback(self.hostname, DnsResponse('found', ip_addrs))
            else:
                callback(self.hostname, DnsResponse('error', 'not found'))
        self.close()


    def handle_error (self, what):
        super(DnsLookupConnection, self).handle_error(what)
        if self.callback:
            callback, self.callback = self.callback, None
            callback(self.hostname,
                     DnsResponse('error', 'failed lookup .. %s' % self))


    def handle_close (self):
        # If we ever get here, we want to make sure we notify the
        # callbacks so that they don't get stuck
        super(DnsLookupConnection, self).handle_close()
        if self.callback:
            callback, self.callback = self.callback, None
            callback(self.hostname, DnsResponse('error', 'closed with no answer .. %s' % self))


from wc.proxy import make_timer
dnscache = DnsCache()

