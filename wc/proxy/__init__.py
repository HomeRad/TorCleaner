"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

# XXX investigate using TCP_NODELAY (disable Nagle)

import sys, time, select, asyncore, re
# fix the ****ing asyncore getattr, as this is swallowing AttributeErrors
del asyncore.dispatcher.__getattr__
def fileno(self):
    return self.socket.fileno()
asyncore.dispatcher.fileno = fileno
from wc import i18n, config, ip
from wc.XmlUtils import xmlify
from wc.debug import *
from urllib import splittype, splithost, splitnport
from LimitQueue import LimitQueue

TIMERS = [] # list of (time, function)

# list of gathered headers
# entries have the form
# (url, 0(incoming)/1(outgoing), headers)
HEADERS = LimitQueue(config['headersave'])

def log (msg):
    """If logfile is defined write the msg into it. The message msg
       should be in common log file format."""
    debug(HURT_ME_PLENTY, "Proxy: logging", `msg`)
    if config['logfile']:
        config['logfile'].write(msg)
        config['logfile'].flush()


# XXX better name/implementation for this function
def stripsite (url):
    """remove scheme and host from url. return host, newurl"""
    import urlparse
    url = urlparse.urlparse(url)
    return url[1], urlparse.urlunparse( (0,0,url[2],url[3],url[4],url[5]) )


is_http = re.compile(r"^HTTP/(?P<major>\d+)\.(?P<minor>\d+)$").search

def fix_http_version (protocol):
    """sanitize http protocol version string"""
    return "HTTP/%.1f"%get_http_version(protocol)


def get_http_version (protocol):
    """return http version number as a float"""
    mo = is_http(protocol)
    if mo:
        major, minor = int(mo.group("major")), int(mo.group("minor"))
        f = float("%d.%d"%(minor, major))
        if f > 1.1:
            print >>sys.stderr, "Error: invalid HTTP version", f
            f = 1.1
        return f
    print >>sys.stderr, "Error: invalid HTTP version", `protocol`
    return 1.0


def set_via_header (headers):
    """set via header"""
    # XXX does not work with multiple existing via headers
    via = headers.get('Via', "").strip()
    if via: via += ", "
    via += "1.1 unknown\r"
    headers['Via'] = via


def remove_warning_headers (headers):
    # XXX todo
    pass

def make_timer (delay, callback):
    "After DELAY seconds, run the CALLBACK function"
    TIMERS.append( [time.time() + delay, callback] )
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


def proxy_poll (timeout=0.0):
    smap = asyncore.socket_map
    if smap:
        r = filter(lambda x: x.readable(), smap.values())
        w = filter(lambda x: x.writable(), smap.values())
        e = smap.values()
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
        handlerCount = 0
        for x in e:
            try:
                x.handle_expt_event()
                handlerCount += 1
            except:
                x.handle_error("poll error", sys.exc_type, sys.exc_value, tb=sys.exc_traceback)
        for x in w:
            try:
                t = time.time()
                if x not in e:
                    x.handle_write_event()
                    handlerCount += 1
                    #if time.time() - t > 0.1:
                    #    debug(BRING_IT_ON, 'Proxy: wslow', '%4.1f'%(time.time()-t), 's', x)
                    #    pass
            except:
                x.handle_error("poll error", sys.exc_type, sys.exc_value, tb=sys.exc_traceback)
        for x in r:
            try:
                t = time.time()
                if x not in e and x not in w:
                    x.handle_read_event()
                    handlerCount += 1
                    #if time.time() - t > 0.1:
                    #    debug(BRING_IT_ON, 'Proxy: rslow', '%4.1f'%(time.time()-t), 's', x)
                    #    pass
            except:
                x.handle_error("poll error", sys.exc_type, sys.exc_value, tb=sys.exc_traceback)
        return handlerCount


def match_host (request):
    """Decide whether to filter this request or not.
       Return a boolean false value if the request must be filtered,
       a boolean true value if the request must not be filtered.
       The String "noproxy" indicates a turned off filtering by the
       noproxy suffix before the hostname."""
    if not request:
        return None
    try:
        foo, url, bar = request.split()
    except Exception, why:
        print >> sys.stderr, "bad request", why
        return None
    hostname = spliturl(url)[1]
    if not hostname:
        return None
    if hostname.startswith('noproxy.'):
        return "noproxy"
    hosts, nets, foo = config['noproxyfor']
    return ip.host_in_set(hostname, hosts, nets)


def spliturl (url):
    """split url in a tuple (scheme, hostname, port, document) where
    hostname is always lowercased"""
    # XXX this relies on scheme==http!
    scheme, netloc = splittype(url)
    host, document = splithost(netloc)
    port = 80
    if host:
        host = host.lower()
        host, port = splitnport(host, 80)
    return scheme, host, port, document


def mainloop (handle=None):
    from HttpClient import HttpClient
    #from Interpreter import Interpreter
    from Listener import Listener
    Listener(config['port'], HttpClient)
    #Listener(8081, lambda *args: apply(Interpreter.Interpreter, args))
    # make_timer(5, transport.http_server.speedcheck_print_status)
    #make_timer(60, periodic_print_socketlist)
    while 1:
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
