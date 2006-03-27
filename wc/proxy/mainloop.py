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

import select

import wc.log
import wc.configuration
import wc.proxy.timer
import wc.proxy.HttpClient
import wc.proxy.Listener
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
        assert wc.log.debug(wc.LOG_PROXY, "select with %f timeout", timeout)
        try:
            (r, w, e) = select.select(r, w, e, timeout)
        except select.error, why:
            if why.args == (4, 'Interrupted system call'):
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                raise
        assert wc.log.debug(wc.LOG_PROXY, "poll result %s", (r, w, e))
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        for x in e:
            assert wc.log.debug(wc.LOG_PROXY, "%s poll handle exception", x)
            x.handle_expt_event()
            handlerCount += 1
        for x in w:
            assert wc.log.debug(wc.LOG_PROXY, "poll handle write %s", x)
            # note: do not put the following "if" in a list filter
            if not x.writable():
                assert wc.log.debug(wc.LOG_PROXY, "not writable %s", x)
                continue
            x.handle_write_event()
            handlerCount += 1
        for x in r:
            assert wc.log.debug(wc.LOG_PROXY, "poll handle read %s", x)
            # note: do not put the following "if" in a list filter
            if not x.readable():
                assert wc.log.debug(wc.LOG_PROXY, "not readable %s", x)
                continue
            x.handle_read_event()
            handlerCount += 1
    return handlerCount


def mainloop (handle=None):
    """
    Proxy main loop, handles requests forever.
    """
    # XXX why do I have to import wc again - python bug?
    import wc
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
    class Abort (Exception):
        pass
    try:
        if handle is not None:
            import win32event
            def abort_check ():
                # win32 handle signaling stop
                rc = win32event.WaitForSingleObject(handle, 0)
                if rc == win32event.WAIT_OBJECT_0:
                    raise Abort()
                # regularly check for abort
                wc.proxy.timer.make_timer(5, abort_check)
            abort_check()
        while True:
            # Installing a timeout means we're in a handler, and after
            # dealing with handlers, we come to the main loop, so we don't
            # have to worry about being in asyncore.poll when a timer goes
            # off.
            proxy_poll(timeout=max(0, wc.proxy.timer.run_timers()))
    except Abort:
        pass
    wc.log.info(wc.LOG_PROXY, "%s stopped", wc.AppName)
