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
        wc.proxy.text_headers())
    elif document=="/connections/":
        ServerHandleDirectly(client,
        'HTTP/1.0 200 OK\r\n',
        'Content-Type: text/plain\r\n\r\n',
        wc.proxy.text_connections())
    else:
        return 0
