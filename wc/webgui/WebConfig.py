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

from wc.proxy.ServerHandleDirectly import ServerHandleDirectly
from wc import config
import wc.proxy

HTML_TEMPLATE = """<html><head>
<title>%(title)s</title>
</head>
<body bgcolor="#fff7e5">
<center><h3>%(header)s</h3></center>
%(content)s
</body></html>"""


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
    s += ']\n\ndnscache: %s'%dns_lookups.dnscache
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


