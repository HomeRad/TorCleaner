"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

# XXX investigate using TCP_NODELAY (disable Nagle)

import sys, re, os, urlparse, time, select, asyncore
from wc import debug,_,config
from wc.debug_levels import *
from urllib import splittype, splithost, splitport

TIMERS = [] # list of (time, function)

def log(msg):
    """If _LOGFILE is defined write the msg into it. The message msg
       must be in common log file format."""
    if config['logfile']:
        config['logfile'].write(msg)


# XXX better name/implementation for this function
def stripsite(url):
    import urlparse
    url = urlparse.urlparse(url)
    return url[1], urlparse.urlunparse( (0,0,url[2],url[3],url[4],url[5]) )

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


def status_info():
    s = """
WebCleaner Proxy Status Info
----------------------------

Uptime: %s

Valid Requests:   %d
Invalid Requests: %d
Failed Requests:  %d

Active connections: [""" % \
    (format_seconds(time.time() - config['starttime']),
     config['requests']['valid'],
     config['requests']['invalid'],
     config['requests']['failed'])
    first = 1
    for conn in asyncore.socket_map.values():
        if first:
            s += str(conn)
            first = 0
        else:
            s += '\n              %s\n' % conn
    s += ']\n\ndnscache: %s' % dns_lookups.dnscache
    return s


def format_seconds(seconds):
    minutes = 0
    hours = 0
    days = 0
    if seconds > 60:
        minutes = seconds / 60
        seconds = seconds % 60
        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60
            if hours > 24:
                days = hours / 24
                hours = hours % 24
    return _("%d days, %02d:%02d:%02d") % (days, hours, minutes, seconds)


def periodic_print_status():
    print status_info()
    make_timer(60, periodic_print_status)


def proxy_poll(timeout=0.0):
    smap = asyncore.socket_map
    if smap:
        r = filter(lambda x: x.readable(), smap.values())
        w = filter(lambda x: x.writable(), smap.values())
        e = smap.values()
        try:
	    (r,w,e) = select.select(r,w,e, timeout)
        except select.error, why:
            debug(BRING_IT_ON, why)
            if why.args == (4, 'Interrupted system call'):
                # this occurs on UNIX systems with a sighup signal
                return
            else:
                raise

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

    #_OBFUSCATE_IP = config['obfuscateip']


def match_host(request):
    if not request:
        return 0
    try:
        foo, url, bar = request.split()
    except Exception, why:
        debug(ALWAYS, "bad request?", why)
        return 0
    scheme, netloc = splittype(url)
    netloc, document = splithost(netloc)
    hostname, port = splitport(netloc)
    hostname = hostname.lower()
    if not hostname:
        return 0
    for domain in config['noproxyfor'].keys():
        if hostname.find(domain) != -1:
            return 1
    return 0


def mainloop():
    import HttpClient,Interpreter
    from Listener import Listener
    # I wrap these in a lambda/apply so that if the module is
    # reloaded, I can use the NEW classes
    Listener(config['port'], lambda *args: apply(HttpClient.HttpClient, args))
    #Listener(8081, lambda *args: apply(Interpreter.Interpreter, args))
    # make_timer(5, transport.http_server.speedcheck_print_status)
    #make_timer(60, periodic_print_socketlist)
    while 1:
        # Installing a timeout means we're in a handler, and after
        # dealing with handlers, we come to the main loop, so we don't
        # have to worry about being in asyncore.poll when a timer goes
        # off.
        handlerCount = proxy_poll(timeout=max(0, run_timers()))

if __name__=='__main__':
    mainloop()
