"""fourth incarnation of Amit's web proxy

used by Bastian Kleineidam for WebCleaner
"""

# XXX investigate using TCP_NODELAY (disable Nagle)

import sys, time, select, asyncore
# fix the ****ing asyncore getattr, as this is swallowing AttributeErrors
del asyncore.dispatcher.__getattr__
def fileno(self):
    return self.socket.fileno()
asyncore.dispatcher.fileno = fileno
from wc import debug,_,config
from wc.debug_levels import *
from urllib import splittype, splithost, splitport
from LimitQueue import LimitQueue

TIMERS = [] # list of (time, function)

# list of gathered headers
# entries have the form
# (url, 0(incoming)/1(outgoing), headers)
HEADERS = LimitQueue(config['headersave'])

HTML_TEMPLATE = """<html><head>
<title>%(title)s</title>
</head>
<body bgcolor="#fff7e5">
<center><h3>%(header)s</h3></center>
%(content)s
</body></html>"""

STATUS_TEMPLATE = """
WebCleaner Proxy Status Info
============================

Uptime: %(uptime)s

Requests:
  Valid:   %(valid)d
  Error:   %(error)d
  Blocked: %(blocked)d

Active connections:
["""


def log(msg):
    """If the logfile is defined write the msg into it. The message msg
       should be in common log file format."""
    debug(HURT_ME_PLENTY, "logging", `msg`)
    if config['logfile']:
        config['logfile'].write(msg)
        config['logfile'].flush()


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


def text_status():
    data = {
    'uptime': format_seconds(time.time() - config['starttime']),
    'valid':  config['requests']['valid'],
    'error': config['requests']['error'],
    'blocked': config['requests']['blocked'],
    }
    s = STATUS_TEMPLATE % data
    first = 1
    for conn in asyncore.socket_map.values():
        if first:
            s += str(conn)
            first = 0
        else:
            s += '\n              %s\n' % conn
    s += ']\n\ndnscache: %s'%dns_lookups.dnscache
    return s


def html_portal():
    data = {
    'title': 'WebCleaner Proxy',
    'header': 'WebCleaner Proxy',
    'content': "<pre>"+text_config()+"\n"+text_status()+"</pre>",
    }
    return HTML_TEMPLATE % data


def new_headers(i):
    return "\n".join(HEADERS.getall()) or "-"


def access_denied(addr):
    data = {
      'title': "WebCleaner Proxy",
      'header': "WebCleaner Proxy",
      'content': "access denied for %s"%str(addr),
    }
    return HTML_TEMPLATE % data


def text_config():
    return str(config)


def format_seconds(seconds):
    minutes = 0
    hours = 0
    days = 0
    if seconds > 60:
        minutes, seconds = divmod(seconds, 60)
        if minutes > 60:
            hours, minutes = divmod(minutes, 60)
            minutes = minutes % 60
            if hours > 24:
                days, hours = divmod(hours, 24)
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
        debug(NIGHTMARE, "write poll")
        for x in w:
            try:
                t = time.time()
                if x not in e:
                    x.handle_write_event()
                    handlerCount += 1
                    if time.time() - t > 0.1:
                        debug(BRING_IT_ON, 'wslow', '%4.1f'%(time.time()-t), 's', x)
            except:
                x.handle_error("poll error", sys.exc_type, sys.exc_value, tb=sys.exc_traceback)
        debug(NIGHTMARE, "read poll")
        for x in r:
            try:
                t = time.time()
                if x not in e and x not in w:
                    x.handle_read_event()
                    handlerCount += 1
                    if time.time() - t > 0.1:
                        debug(BRING_IT_ON, 'rslow', '%4.1f'%(time.time()-t), 's', x)
            except:
                x.handle_error("poll error", sys.exc_type, sys.exc_value, tb=sys.exc_traceback)
        return handlerCount

    #_OBFUSCATE_IP = config['obfuscateip']


def match_host(request):
    if not request:
        return 0
    try:
        foo, url, bar = request.split()
    except Exception, why:
        print >> sys.stderr, "bad request", why
        return 0
    hostname = spliturl(url)[1]
    if not hostname:
        return 0
    hostname = hostname.lower()
    for domain in config['noproxyfor'].keys():
        if hostname.find(domain) != -1:
            return 1
    return 0


def spliturl (url):
    scheme, netloc = splittype(url)
    host, document = splithost(netloc)
    if not host:
        hostname = "localhost"
        port = config['port']
    else:
        hostname, port = splitport(host)
        if port is None:
            port = 80
        else:
            port = int(port)
    return scheme, hostname, port, document


def mainloop():
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


if __name__=='__main__':
    mainloop()
