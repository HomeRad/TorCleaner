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
Pool for server connections.
"""

import time

import wc
import wc.log
import wc.proxy


class ServerPool (object):
    """
    Server connection pool for reusing server connections

    Usage:
    reserve_server to receive a server or None
    unreserve_server to put a server back on the available set

    register_server to add a server (busy)
    unregister_server to remove a server (busy or not)

    register_callback to express an interest in a server
    """

    def __init__ (self):
        """
        Initialize pool data.
        """
        self.smap = {} # {(ipaddr, port) -> {server -> ('available'|'busy')}}
        self.http_versions = {} # {(ipaddr, port) -> http_version}
        self.callbacks = {} # {(ipaddr, port) -> [functions to call]}
        wc.proxy.make_timer(60, self.expire_servers)

    def count_servers (self, addr):
        """
        How many busy server objects connect to this address?
        """
        states = self.smap.get(addr, {}).values()
        return len([x for x in states if x[0] == 'busy'])

    def reserve_server (self, addr):
        """
        Try to return an existing server connection for given addr,
        or return None if on connection is available at the moment.
        """
        wc.log.debug(wc.LOG_PROXY, "pool reserve server %s", addr)
        for server, status in self.smap.get(addr, {}).items():
            if status[0] == 'available':
                # Let's reuse this one
                self.smap[addr][server] = ('busy', )
                wc.log.debug(wc.LOG_PROXY, 'pool reserve %s %s', addr, server)
                return server
        return None

    def unreserve_server (self, addr, server):
        """
        Make given server connection available.
        """
        wc.log.debug(wc.LOG_PROXY, "pool unreserve %s %s", addr, server)
        assert addr in self.smap, '%s missing %s' % (self.smap, addr)
        assert server in self.smap[addr], \
               '%s missing %s' % (self.smap[addr], server)
        assert self.smap[addr][server][0] == 'busy', \
               '%s is not busy but %s' % (server, self.smap[addr][server][0])
        self.smap[addr][server] = ('available', time.time())
        self.invoke_callbacks(addr)

    def register_server (self, addr, server):
        """
        Register the server as being used.
        """
        wc.log.debug(wc.LOG_PROXY, "pool register %s %s", addr, server)
        self.smap.setdefault(addr, {})[server] = ('busy',)

    def unregister_server (self, addr, server):
        """
        Unregister the server and remove it from the pool.
        """
        wc.log.debug(wc.LOG_PROXY, "pool unregister %s %s", addr, server)
        assert addr in self.smap, '%s missing %s' % (self.smap, addr)
        assert server in self.smap[addr], \
               '%s missing %s' % (self.smap[addr], server)
        del self.smap[addr][server]
        if not self.smap[addr]:
            del self.smap[addr]
        self.invoke_callbacks(addr)

    def register_callback (self, addr, callback):
        """
        Callbacks are called whenever a server may be available
        for (addr). It's the callback's responsibility to re-register
        if someone else has stolen the server already.
        """
        self.callbacks.setdefault(addr, []).append(callback)

    def connection_limit (self, addr):
        """
        Keep these limits reasonably high (at least twenty or more)
        since having background downloads with no available servers
        can lead to aborted downloads.
        """
        if self.http_versions.get(addr, (1, 1)) <= (1, 0):
            # For older versions of HTTP, we open lots of connections
            return 60
        else:
            return 40

    def set_http_version (self, addr, http_version):
        """
        Store http version for a given server.
        """
        self.http_versions[addr] = http_version
        self.invoke_callbacks(addr)

    def expire_servers (self):
        """
        Expire server connection that have been unused for too long.
        """
        wc.log.debug(wc.LOG_PROXY, "pool expire servers")
        expire_time = time.time() - 300 # Unused for five minutes
        to_expire = []
        for addr, set in self.smap.items():
            for server, status in set.items():
                if status[0] == 'available' and status[1] < expire_time:
                    # It's old .. let's get rid of it
                    to_expire.append((addr, server))
        for addr, server in to_expire:
            wc.log.debug(wc.LOG_PROXY, "expire %s server %s", addr, server)
            server.close()
            if addr in self.smap:
                assert not self.smap[addr].has_key(server), \
                       "Not expired: %s" % str(self.smap[addr])
        wc.proxy.make_timer(60, self.expire_servers)

    def invoke_callbacks (self, addr):
        """
        Notify whoever wants to know about a server becoming available.
        """
        if addr in self.callbacks:
            callbacks = self.callbacks[addr]
            del self.callbacks[addr]
            for callback in callbacks:
                callback()


# connection pool for persistent server connections
serverpool = ServerPool()
