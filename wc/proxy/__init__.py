# -*- coding: iso-8859-1 -*-
"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import socket, select, asyncore, re
from time import time
# remove asyncore getattr, as this is swallowing AttributeErrors
del asyncore.dispatcher.__getattr__
# add the fileno function
def fileno (self):
    return self.socket.fileno()
asyncore.dispatcher.fileno = fileno
from wc import i18n, ip
from wc.log import *
from LimitQueue import LimitQueue

# test for IPv6, both in Python build and in kernel build
has_ipv6 = False
if socket.has_ipv6:
    try:
        socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        has_ipv6 = True
    except socket.error, msg:
        # only catch this one:
        # socket.error: (97, 'Address family not supported by protocol')
        if msg[0]!=97:
            raise


TIMERS = [] # list of (time, function)

is_http = re.compile(r"(?i)^HTTP/(?P<major>\d+)\.(?P<minor>\d+)$").search

def fix_http_version (protocol):
    """sanitize http protocol version string"""
    return "HTTP/%d.%d"%get_http_version(protocol)


def get_http_version (protocol):
    """return http version number as a tuple"""
    mo = is_http(protocol)
    if mo:
        f = (int(mo.group("major")), int(mo.group("minor")))
        if f > (1,1):
            error(PROXY, i18n._("unsupported HTTP version %s"), f)
            f = (1,1)
        return f
    error(PROXY, i18n._("invalid HTTP version %r"), protocol)
    return (1,0)


def create_inet_socket (dispatch, socktype):
    """create an AF_INET(6) socket object for given dispatcher, testing
    for IPv6 capability and disabling the NAGLE algorithm for TCP sockets
    """
    if has_ipv6:
        family = socket.AF_INET6
    else:
        family = socket.AF_INET
    dispatch.create_socket(family, socktype)
    if socktype==socket.SOCK_STREAM:
        # disable NAGLE algorithm, which means sending pending data
        # immediately, possibly wasting bandwidth but improving
        # responsiveness for fast networks
        dispatch.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


def make_timer (delay, callback):
    "After DELAY seconds, run the CALLBACK function"
    TIMERS.append( (time()+delay, callback) )
    TIMERS.sort()
    debug(PROXY, "%d timers", len(TIMERS))


def run_timers ():
    "Run all timers ready to be run, and return seconds to the next timer"
    # Note that we will run timers that are scheduled to be run within
    # 10 ms.  This is because the select() statement doesn't have
    # infinite precision and may end up returning slightly earlier.
    # We're willing to run the event a few millisecond earlier.
    while TIMERS and TIMERS[0][0] <= time() + 0.01:
        # This timeout handler should be called
        callback = TIMERS[0][1]
        del TIMERS[0]
        callback()
    if TIMERS: return TIMERS[0][0] - time()
    else:      return 60


def periodic_print_status ():
    print status_info()
    make_timer(60, periodic_print_status)


def proxy_poll (timeout=0.0):
    smap = asyncore.socket_map
    if smap:
        r = [ x for x in smap.values() if x.readable() ]
        w = [ x for x in smap.values() if x.writable() ]
        e = smap.values()
        debug(PROXY, "poll smap %s", (r,w,e))
        try:
            (r,w,e) = select.select(r,w,e, timeout)
        except select.error, why:
            if why.args == (4, 'Interrupted system call'):
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                raise
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        for x in e:
            debug(PROXY, "%s handle exception event", x)
            x.handle_expt_event()
        for x in w:
            t = time()
            if x not in e and x.writable():
                debug(PROXY, "%s handle write", x)
                x.handle_write_event()
        for x in r:
            t = time()
            if x not in e and x not in w and x.readable():
                debug(PROXY, "%s handle read", x)
                x.handle_read_event()


def mainloop (handle=None):
    from HttpClient import HttpClient
    from Listener import Listener
    from wc import config
    Listener(config['port'], HttpClient)
    # experimental interactive command line
    #from Interpreter import Interpreter
    #Listener(config['port']+1, Interpreter)
    # periodic statistics (only useful for speed profiling)
    #make_timer(5, transport.http_server.speedcheck_print_status)
    #make_timer(60, periodic_print_socketlist)
    while True:
        # Installing a timeout means we're in a handler, and after
        # dealing with handlers, we come to the main loop, so we don't
        # have to worry about being in asyncore.poll when a timer goes
        # off.
        proxy_poll(timeout=max(0, run_timers()))
        if handle is not None:
            # win32 handle signaling stop
            import win32event
            rc = win32event.WaitForSingleObject(handle, 0)
            if rc==win32event.WAIT_OBJECT_0:
                break


if __name__=='__main__':
    mainloop()
