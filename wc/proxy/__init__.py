#!/usr/bin/env python
"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

# XXX investigate using TCP_NODELAY (disable Nagle)

import sys, os, urlparse, time, select, asyncore, wc
from wc import debug
from wc.debug_levels import *

TIMERS = [] # list of (time, function)

def log(msg):
    """If _LOGFILE is defined write the msg into it. The message msg
       must be in common log file format."""
    if _LOGFILE:
        _LOGFILE.write(msg)


# XXX better name/implementation for this function
def stripsite(url):
    import urlparse
    url = urlparse.urlparse(url)
    return url[1], urlparse.urlunparse( (0,0,url[2],url[3],url[4],url[5]) )

class ProxyConfig:
    local_sockets_only = 0
    
def make_timer(delay, callback):
    "After DELAY seconds, run the CALLBACK function"
    TIMERS.append( (time.time() + delay, callback) )
    TIMERS.sort()

def run_timers():
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
    

            

def periodic_print_socketlist():
    print 'connections: [',
    first = 1
    for conn in asyncore.socket_map.values():
        if first:
            print conn,
            first = 0
        else:
            print '\n              %s' % conn
    print ']'
    #print 'dnscache:', proxy4_dns.DnsCache
    make_timer(60, periodic_print_socketlist)

def proxy_poll(timeout=0.0):
    smap = asyncore.socket_map
    if smap:
        r = filter(lambda x: x.readable(), smap.values())
        w = filter(lambda x: x.writable(), smap.values())
        e = smap.values()
        (r,w,e) = select.select(r,w,e, timeout)
        
        # Make sure we only process one type of event at a time,
        # because if something needs to close the connection we
        # don't want to call another handle_* on it
        handlerCount = 0
        for x in e:
            try:
                x.handle_expt_event()
                handlerCount = handlerCount + 1
            except:
                x.handle_error(sys.exc_type, sys.exc_value, sys.exc_traceback)
        for x in w:
            try:
                t = time.time()
                if x not in e:
                    x.handle_write_event()
                    handlerCount = handlerCount + 1
                    if time.time() - t > 0.1:
                        debug(BRING_IT_ON, 'wslow', '%4.1f'%(time.time()-t), 's', x)
            except:
                x.handle_error(sys.exc_type, sys.exc_value, sys.exc_traceback)
        for x in r:
            try:
                t = time.time()
                if x not in e and x not in w:
                    x.handle_read_event()
                    handlerCount = handlerCount + 1
                    if time.time() - t > 0.1:
                        debug(BRING_IT_ON, 'rslow', '%4.1f'%(time.time()-t), 's', x)
            except:
                x.handle_error(sys.exc_type, sys.exc_value, sys.exc_traceback)
        return handlerCount


def configure(config):
    global _PORT,_LOGFILE
    _PORT = config['port']
    _PARENT_PROXY_PORT = config['parentproxyport']
    _PARENT_PROXY = config['parentproxy']
    _LOGFILE = config['logfile']
    _TIMEOUT = config['timeout']
    _OBFUSCATE_IP = config['obfuscateip']
    wc.filter._FILTER_LIST = config['filterlist']
    _ERROR_LEN = config["errorlen"]
    _ERROR_TEXT = config["errortext"]
    if _LOGFILE == 'stdout':
        _LOGFILE = sys.stdout
    elif _LOGFILE:
        _LOGFILE = open(_LOGFILE, 'a')
    config.init_filtermodules()


def mainloop():
    import HttpClient,Interpreter
    from Listener import Listener
    # I wrap these in a lambda/apply so that if the module is
    # reloaded, I can use the NEW classes
    Listener(_PORT, lambda *args: apply(HttpClient.HttpClient, args))
    #Listener(8081, lambda *args: apply(Interpreter.Interpreter, args))
    # make_timer(5, transport.http_server.speedcheck_print_status)
    make_timer(60, periodic_print_socketlist)
    while 1:
        # Installing a timeout means we're in a handler, and after
        # dealing with handlers, we come to the main loop, so we don't
        # have to worry about being in asyncore.poll when a timer goes
        # off.
        handlerCount = proxy_poll(timeout=max(0, run_timers()))

if __name__=='__main__':
    mainloop()
