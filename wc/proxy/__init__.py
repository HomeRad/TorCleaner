# -*- coding: iso-8859-1 -*-
"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

import socket
import select
import re
import time
import wc
import wc.log


TIMERS = [] # list of (time, function)

is_http = re.compile(r"(?i)^HTTP/(?P<major>\d+)\.(?P<minor>\d+)$").search


def fix_http_version (protocol):
    """sanitize http protocol version string"""
    return "HTTP/%d.%d" % get_http_version(protocol)


def get_http_version (protocol):
    """return http version number as a tuple"""
    mo = is_http(protocol)
    if mo:
        f = (int(mo.group("major")), int(mo.group("minor")))
        if f > (1, 1):
            wc.log.error(wc.LOG_PROXY, _("unsupported HTTP version %s"), f)
            f = (1, 1)
        return f
    wc.log.error(wc.LOG_PROXY, _("invalid HTTP version %r"), protocol)
    return (1, 0)


def make_timer (delay, callback):
    """after DELAY seconds, run the CALLBACK function"""
    wc.log.debug(wc.LOG_PROXY, "Adding %s to %d timers", callback, len(TIMERS))
    TIMERS.append( (time.time()+delay, callback) )
    TIMERS.sort()


MAX_TIMEOUT = 60
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
    if TIMERS:
        return min(TIMERS[0][0] - time.time(), MAX_TIMEOUT)
    else:
        return MAX_TIMEOUT


import wc.proxy.Dispatcher

def proxy_poll (timeout=0.0):
    """look for sockets with pending data and call the appropriate
       connection handlers"""
    handlerCount = 0
    if wc.proxy.Dispatcher.socket_map:
        r = [x for x in wc.proxy.Dispatcher.socket_map.itervalues()
             if x.readable()]
        w = [x for x in wc.proxy.Dispatcher.socket_map.itervalues()
             if x.writable()]
        e = wc.proxy.Dispatcher.socket_map.values()
        wc.log.debug(wc.LOG_PROXY, "select with %f timeout:", timeout)
        for x in e:
            wc.log.debug(wc.LOG_PROXY, "  %s", x)
        try:
            (r, w, e) = select.select(r, w, e, timeout)
        except select.error, why:
            if why.args == (4, 'Interrupted system call'):
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                raise
        wc.log.debug(wc.LOG_PROXY, "poll result %s", (r, w, e))
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        for x in e:
            wc.log.debug(wc.LOG_PROXY, "%s poll handle exception", x)
            x.handle_expt_event()
            handlerCount += 1
        for x in w:
            # note: do _not_ put this if in a list filter
            if not x.writable():
                continue
            t = time.time()
            wc.log.debug(wc.LOG_PROXY, "%s poll handle write", x)
            x.handle_write_event()
            handlerCount += 1
            _slow_check(x, t, 'wslow')
        for x in r:
            # note: do _not_ put this if in a list filter
            if not x.readable():
                continue
            t = time.time()
            wc.log.debug(wc.LOG_PROXY, "%s poll handle read", x)
            x.handle_read_event()
            handlerCount += 1
            _slow_check(x, t, 'rslow')
    return handlerCount


def _slow_check (x, t, stype):
    """check if processing of connection x took too much time
       and print a warning"""
    if time.time()-t > 2:
        wc.log.warn(wc.LOG_PROXY, '%s %4.1fs %s', stype, (time.time()-t), x)



def mainloop (handle=None, abort=None):
    """proxy main loop, handles requests forever"""
    import wc.proxy.HttpClient
    import wc.proxy.Listener
    import wc.proxy.SslClient
    import wc.proxy.ssl
    wc.proxy.Listener.Listener(wc.config['port'],
                               wc.proxy.HttpClient.HttpClient)
    if wc.config['sslgateway']:
        wc.proxy.Listener.Listener(wc.config['sslport'],
                 wc.proxy.SslClient.SslClient,
                 sslctx=wc.proxy.ssl.get_serverctx(wc.config.configdir))
    # experimental interactive command line
    #from Interpreter import Interpreter
    #Listener(wc.config['cmdport'], Interpreter)
    # periodic statistics (only useful for speed profiling)
    #make_timer(5, transport.http_server.speedcheck_print_status)
    #make_timer(60, periodic_print_socketlist)
    if abort is not None:
        # regular abort check every second
        global MAX_TIMEOUT
        MAX_TIMEOUT = 1
    while True:
        # Installing a timeout means we're in a handler, and after
        # dealing with handlers, we come to the main loop, so we don't
        # have to worry about being in asyncore.poll when a timer goes
        # off.
        proxy_poll(timeout=max(0, run_timers()))
        if abort is not None and abort():
            break
        if handle is not None:
            # win32 handle signaling stop
            import win32event
            rc = win32event.WaitForSingleObject(handle, 0)
            if rc == win32event.WAIT_OBJECT_0:
                break
