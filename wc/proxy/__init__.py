# -*- coding: iso-8859-1 -*-
"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import socket, select, re, time
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
    if False: #has_ipv6:
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
    """after DELAY seconds, run the CALLBACK function"""
    debug(PROXY, "Adding %s to %d timers", callback, len(TIMERS))
    TIMERS.append( (time.time()+delay, callback) )
    TIMERS.sort()


def run_timers ():
    "Run all timers ready to be run, and return seconds to the next timer"
    # Note that we will run timers that are scheduled to be run within
    # 10 ms.  This is because the select() statement doesn't have
    # infinite precision and may end up returning slightly earlier.
    # We're willing to run the event a few millisecond earlier.
    while TIMERS and TIMERS[0][0] <= time.time() + 0.01:
        # This timeout handler should be called
        callback = TIMERS[0][1]
        del TIMERS[0]
        callback()
    if TIMERS: return TIMERS[0][0] - time.time()
    else:      return 60


def periodic_print_status ():
    print status_info()
    make_timer(60, periodic_print_status)


from Dispatcher import socket_map
def proxy_poll (timeout=0.0):
    handlerCount = 0
    if socket_map:
        r = [ x for x in socket_map.itervalues() if x.readable() ]
        w = [ x for x in socket_map.itervalues() if x.writable() ]
        e = socket_map.values()
        debug(PROXY, "select with %f timeout:", timeout)
        for x in e:
            debug(PROXY, "  %s", x)
        try:
            (r,w,e) = select.select(r,w,e, timeout)
        except select.error, why:
            if why.args == (4, 'Interrupted system call'):
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                raise
        debug(PROXY, "poll result %s", (r,w,e))
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        for x in e:
            debug(PROXY, "%s poll handle exception", x)
            x.handle_expt_event()
            handlerCount += 1
        for x in w:
            if x in e or not x.writable():
                continue
            t = time.time()
            debug(PROXY, "%s poll handle write", x)
            x.handle_write_event()
            handlerCount += 1
            _slow_check(x, t, 'wslow')
        for x in r:
            if x in e or x in w or not x.readable():
                continue
            t = time.time()
            debug(PROXY, "%s poll handle read", x)
            x.handle_read_event()
            handlerCount += 1
            _slow_check(x, t, 'rslow')
    return handlerCount


def _slow_check (x, t, stype):
    """check if processing of connection x took too much time
       and print a warning"""
    if time.time()-t > 2:
        warn(PROXY, '%s %4.1fs %s', stype, (time.time()-t), x)


def mainloop (handle=None):
    from HttpClient import HttpClient
    from Listener import Listener
    from wc import config
    Listener(config['port'], HttpClient)
    if config['sslgateway']:
        from ssl import serverctx
        from SslClient import SslClient
        Listener(config['sslport'], SslClient, sslctx=serverctx)
    # experimental interactive command line
    #from Interpreter import Interpreter
    #Listener(config['cmdport'], Interpreter)
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

