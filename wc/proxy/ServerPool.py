import time
from wc.proxy import make_timer
from wc import i18n
from wc.debug import *

class ServerPool:
    """server connection pool for reusing server connections

       Usage:
       reserve_server to receive a server or None
       unreserve_server to put a server back on the available set

       register_server to add a server (busy)
       unregister_server to remove a server (busy or not)

       register_callback to express an interest in a server
    """
    def __init__ (self):
        self.map = {} # {(ipaddr, port) -> {server -> ('available'|'busy')}}
        self.http_versions = {} # {(ipaddr, port) -> http_version}
        self.callbacks = {} # {(ipaddr, port) -> [functions to call]}
        make_timer(60, self.expire_servers)

    def count_servers (self, addr):
        "How many server objects connect to this address?"
        return len(self.map.get(addr, {}))


    def reserve_server (self, addr):
        for server,status in self.map.get(addr, {}).items():
            if status[0] == 'available':
                # Let's reuse this one
                self.map[addr][server] = ('busy', )
                debug(BRING_IT_ON, 'reserve_server', addr, server)
                return server
        return None


    def unreserve_server (self, addr, server):
        assert self.map.has_key(addr), '%s missing %s' % (self.map, addr)
        assert self.map[addr].has_key(server), \
               '%s missing %s' % (self.map[addr], server)
        assert self.map[addr][server][0] == 'busy'
        self.map[addr][server] = ('available', time.time())
        self.invoke_callbacks(addr)


    def register_server (self, addr, server):
        "Register the server as being used"
        if not self.map.has_key(addr):
            self.map[addr] = {}
        self.map[addr][server] = ('busy',)


    def unregister_server (self, addr, server):
        "Unregister the server"
        assert self.map.has_key(addr), '%s missing %s' % (self.map, addr)
        assert self.map[addr].has_key(server), \
               '%s missing %s' % (self.map[addr], server)
        del self.map[addr][server]
        if not self.map[addr]: del self.map[addr]
        self.invoke_callbacks(addr)


    def register_callback (self, addr, callback):
        # Callbacks are called whenever a server may be available
        # for (addr).  It's the callback's responsibility to re-register
        # if someone else has stolen the server already.
        if not self.callbacks.has_key(addr):
            self.callbacks[addr] = []
        self.callbacks[addr].append(callback)


    def connection_limit (self, addr):
        if self.http_versions.get(addr, 1.1) <= 1.0:
            # For older versions of HTTP, we open lots of connections
            return 6
        else:
            return 2


    def set_http_version (self, addr, http_version):
        self.http_versions[addr] = http_version
        self.invoke_callbacks(addr)


    def expire_servers (self):
        expire_time = time.time() - 300 # Unused for five minutes
        to_expire = []
        for addr,set in self.map.items():
            for server,status in set.items():
                if status[0] == 'available' and status[1] < expire_time:
                    # It's old .. let's get rid of it
                    to_expire.append(server)
        for server in to_expire:
            server.close()
        make_timer(60, self.expire_servers)


    def invoke_callbacks (self, addr):
        # Notify whoever wants to know about a server becoming available
        if self.callbacks.has_key(addr):
            callbacks = self.callbacks[addr]
            del self.callbacks[addr] 
            for callback in callbacks:
                callback()

