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

from .. import log, LOG_PROXY, configuration, HasSsl, AppName
from . import timer, HttpClient, Listener, Dispatcher


def proxy_poll(timeout=None):
    """
    Look for sockets with pending data and call the appropriate
    connection handlers.
    """
    handlerCount = 0
    if Dispatcher.socket_map:
        e = Dispatcher.socket_map.values()
        r = [x for x in e if x.readable()]
        w = [x for x in e if x.writable()]
        if timeout is None:
            log.debug(LOG_PROXY, "select without timeout")
        else:
            log.debug(LOG_PROXY, "select with %f timeout", timeout)
        try:
            (r, w, e) = select.select(r, w, e, timeout)
        except select.error, why:
            if why.args[0] == 4: # 'Interrupted system call'
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                log.warn(LOG_PROXY,
                    "Failed select with r=%s, w=%s, e=%s, timeout=%s",
                    str(r), str(w), str(e), str(timeout))
                raise
        log.debug(LOG_PROXY, "poll result %s", (r, w, e))
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        for x in e:
            log.debug(LOG_PROXY, "poll handle exception %s", x)
            x.handle_expt_event()
            handlerCount += 1
        for x in w:
            log.debug(LOG_PROXY, "poll handle write %s", x)
            # note: do not put the following "if" in a list filter
            if not x.writable():
                log.debug(LOG_PROXY, "not writable %s", x)
                continue
            x.handle_write_event()
            handlerCount += 1
        for x in r:
            log.debug(LOG_PROXY, "poll handle read %s", x)
            # note: do not put the following "if" in a list filter
            if not x.readable():
                log.debug(LOG_PROXY, "not readable %s", x)
                continue
            x.handle_read_event()
            handlerCount += 1
    return handlerCount


def mainloop(handle=None):
    """
    Proxy main loop, handles requests forever.
    """
    host = str(configuration.config['bindaddress'])
    port = configuration.config['port']
    Listener.Listener(host, port, HttpClient.HttpClient)
    if configuration.config['sslgateway'] and HasSsl:
        import SslClient
        import ssl
        port = configuration.config['sslport']
        sslctx = ssl.get_serverctx(configuration.config.configdir)
        Listener.Listener(host, port, SslClient.SslClient, sslctx=sslctx)
    class Abort(StandardError):
        pass
    try:
        if handle is not None:
            import win32event
            def abort_check():
                # win32 handle signaling stop
                rc = win32event.WaitForSingleObject(handle, 0)
                if rc == win32event.WAIT_OBJECT_0:
                    raise Abort()
                # regularly check for abort
                timer.make_timer(5, abort_check)
            abort_check()
        while True:
            # Installing a timeout means we're in a handler, and after
            # dealing with handlers, we come to the main loop, so we don't
            # have to worry about being in asyncore.poll when a timer goes
            # off.
            proxy_poll(timeout=timer.run_timers())
    except Abort:
        pass
    log.info(LOG_PROXY, "%s stopped", AppName)
