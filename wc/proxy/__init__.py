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
Fourth incarnation of Amit's web proxy

Used and modified by Bastian Kleineidam for WebCleaner
"""

import select
import time

import wc
import wc.log
import wc.configuration


def readable_socket (sock, timeout=0.5):
    """
    Check if socket is readable.
    @param sock: the socket to check
    @type sock: socket object of file descriptor suitable for select() call
    @param timeout: how long to wait for readable data; if timeout is None
      or negative the function blocks; a zero timeout only polls for data
    @type timeout: number or None
    @return: True if data can be read from socket
    @rtype: bool
    """
    try:
        if timeout is None or timeout < 0.0:
            return select.select([sock], [], [])[0]
        return select.select([sock], [], [], timeout)[0]
    except select.error:
        return False


TIMERS = [] # list of (time, function)

def make_timer (delay, callback):
    """
    After DELAY seconds, run the CALLBACK function.
    """
    wc.log.debug(wc.LOG_PROXY, "Adding %s to %d timers", callback, len(TIMERS))
    TIMERS.append( (time.time()+delay, callback) )
    TIMERS.sort()


MAX_TIMEOUT = 60
def run_timers ():
    """
    Run all timers ready to be run, and return seconds to the next timer.
    """
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
    """
    Look for sockets with pending data and call the appropriate
    connection handlers.
    """
    handlerCount = 0
    if wc.proxy.Dispatcher.socket_map:
        e = wc.proxy.Dispatcher.socket_map.values()
        r = [x for x in e if x.readable()]
        w = [x for x in e if x.writable()]
        wc.log.debug(wc.LOG_PROXY, "select with %f timeout", timeout)
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
            t = time.time()
            x.handle_expt_event()
            handlerCount += 1
            _slow_check(x, t, 'eslow')
        for x in w:
            wc.log.debug(wc.LOG_PROXY, "poll handle write %s", x)
            # note: do not put the following "if" in a list filter
            if not x.writable():
                wc.log.debug(wc.LOG_PROXY, "not writable %s", x)
                continue
            t = time.time()
            x.handle_write_event()
            handlerCount += 1
            _slow_check(x, t, 'wslow')
        for x in r:
            wc.log.debug(wc.LOG_PROXY, "poll handle read %s", x)
            # note: do not put the following "if" in a list filter
            if not x.readable():
                wc.log.debug(wc.LOG_PROXY, "not readable %s", x)
                continue
            t = time.time()
            x.handle_read_event()
            handlerCount += 1
            _slow_check(x, t, 'rslow')
    return handlerCount


def _slow_check (x, t, stype):
    """
    Check if processing of connection x took too much time and print a
    warning.
    """
    if time.time()-t > 2:
        wc.log.warn(wc.LOG_PROXY, '%s %4.1fs %s', stype, (time.time()-t), x)


def mainloop (handle=None, abort=None):
    """
    Proxy main loop, handles requests forever.
    """
    import wc.proxy.HttpClient
    import wc.proxy.Listener
    host = str(wc.configuration.config['bindaddress'])
    port = wc.configuration.config['port']
    wc.proxy.Listener.Listener(host, port, wc.proxy.HttpClient.HttpClient)
    if wc.configuration.config['sslgateway'] and wc.HasSsl:
        import wc.proxy.SslClient
        import wc.proxy.ssl
        port = wc.configuration.config['sslport']
        sslctx = wc.proxy.ssl.get_serverctx(wc.configuration.config.configdir)
        wc.proxy.Listener.Listener(host, port, wc.proxy.SslClient.SslClient,
                                   sslctx=sslctx)
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
    wc.log.info(wc.LOG_PROXY, "%s stopped", wc.AppName)
