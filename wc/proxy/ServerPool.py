# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import time
from wc.proxy import make_timer
from wc.log import *

class ServerPool (object):
    """server connection pool for reusing server connections

       Usage:
       reserve_server to receive a server or None
       unreserve_server to put a server back on the available set

       register_server to add a server (busy)
       unregister_server to remove a server (busy or not)

       register_callback to express an interest in a server
    """
    def __init__ (self):
        self.smap = {} # {(ipaddr, port) -> {server -> ('available'|'busy')}}
        self.http_versions = {} # {(ipaddr, port) -> http_version}
        self.callbacks = {} # {(ipaddr, port) -> [functions to call]}
        make_timer(60, self.expire_servers)


    def count_servers (self, addr):
        """How many busy server objects connect to this address?"""
        states = self.smap.get(addr, {}).values()
        return len([x for x in states if x[0]=='busy'])


    def reserve_server (self, addr):
        for server,status in self.smap.get(addr, {}).items():
            if status[0] == 'available':
                # Let's reuse this one
                self.smap[addr][server] = ('busy', )
                debug(PROXY, 'pool reserve %s %s', addr, server)
                return server
        return None


    def unreserve_server (self, addr, server):
        debug(PROXY, "pool unreserve %s %s", addr, server)
        assert addr in self.smap, '%s missing %s' % (self.smap, addr)
        assert server in self.smap[addr], \
               '%s missing %s' % (self.smap[addr], server)
        assert self.smap[addr][server][0] == 'busy', \
               '%s is not busy but %s' % (server, self.smap[addr][server][0])
        self.smap[addr][server] = ('available', time.time())
        self.invoke_callbacks(addr)


    def register_server (self, addr, server):
        """Register the server as being used"""
        debug(PROXY, "pool register %s %s", addr, server)
        self.smap.setdefault(addr, {})[server] = ('busy',)


    def unregister_server (self, addr, server):
        """Unregister the server"""
        debug(PROXY, "pool unregister %s %s", addr, server)
        assert addr in self.smap, '%s missing %s' % (self.smap, addr)
        assert server in self.smap[addr], \
               '%s missing %s' % (self.smap[addr], server)
        del self.smap[addr][server]
        if not self.smap[addr]:
            del self.smap[addr]
        self.invoke_callbacks(addr)


    def register_callback (self, addr, callback):
        # Callbacks are called whenever a server may be available
        # for (addr). It's the callback's responsibility to re-register
        # if someone else has stolen the server already.
        self.callbacks.setdefault(addr, []).append(callback)


    def connection_limit (self, addr):
        """keep these limits reasonably high (at least twenty or more)
           since having background downloads with no available servers
           can lead to aborted downloads"""
        if self.http_versions.get(addr, (1,1)) <= (1,0):
            # For older versions of HTTP, we open lots of connections
            return 60
        else:
            return 40

    def set_http_version (self, addr, http_version):
        self.http_versions[addr] = http_version
        self.invoke_callbacks(addr)


    def expire_servers (self):
        debug(PROXY, "expire servers")
        expire_time = time.time() - 300 # Unused for five minutes
        to_expire = []
        for addr,set in self.smap.items():
            for server,status in set.items():
                if status[0] == 'available' and status[1] < expire_time:
                    # It's old .. let's get rid of it
                    to_expire.append((addr,server))
        for addr,server in to_expire:
            debug(PROXY, "expire %s server %s", addr, server)
            server.close()
            if addr in self.smap:
                assert not self.smap[addr].has_key(server), "Not expired: %s"%str(self.smap[addr])
        make_timer(60, self.expire_servers)


    def invoke_callbacks (self, addr):
        # Notify whoever wants to know about a server becoming available
        if addr in self.callbacks:
            callbacks = self.callbacks[addr]
            del self.callbacks[addr] 
            for callback in callbacks:
                callback()


# connection pool for persistent server connections
serverpool = ServerPool()
