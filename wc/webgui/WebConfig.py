# Copyright (C) 2002  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import time, asyncore
import wc.proxy
from wc.proxy.ServerHandleDirectly import ServerHandleDirectly
from wc import config, i18n
from wc.XmlUtils import xmlify

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


def html_portal ():
    data = {
    'title': 'WebCleaner Proxy',
    'header': 'WebCleaner Proxy',
    'content': "<pre>%s\n%s</pre>" % (text_config(), text_status()),
    }
    return HTML_TEMPLATE % data


def handle_document (document, client):
    if document=="/":
        ServerHandleDirectly(client,
        'HTTP/1.0 200 OK\r\n',
        'Content-Type: text/html\r\n\r\n',
        html_portal())
    elif document=="/headers/":
        ServerHandleDirectly(client,
        'HTTP/1.0 200 OK\r\n',
        'Content-Type: text/plain\r\n\r\n',
        text_headers())
    elif document=="/connections/":
        ServerHandleDirectly(client,
        'HTTP/1.0 200 OK\r\n',
        'Content-Type: text/plain\r\n\r\n',
        text_connections())
    else:
        return 0
    return "True"


def text_status ():
    data = {
    'uptime': format_seconds(time.time() - config['starttime']),
    'valid':  config['requests']['valid'],
    'error': config['requests']['error'],
    'blocked': config['requests']['blocked'],
    }
    connections = map(str, asyncore.socket_map.values())
    s = STATUS_TEMPLATE % data
    s += xmlify('\n     '.join(connections))
    s += ']\n\ndnscache: %s'%wc.proxy.dns_lookups.dnscache
    return s


def text_headers ():
    return "\n".join(wc.proxy.HEADERS.getall()) or "-"


def text_connections ():
    return "valid:%(valid)d\nerror:%(error)d\nblocked:%(blocked)d"%\
           config['requests']


def access_denied (addr):
    data = {
      'title': "WebCleaner Proxy",
      'header': "WebCleaner Proxy",
      'content': "access denied for %s"%str(addr),
    }
    return HTML_TEMPLATE % data


def text_config ():
    return str(config)


def format_seconds (seconds):
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
    return i18n._("%d days, %02d:%02d:%02d") % (days, hours, minutes, seconds)


