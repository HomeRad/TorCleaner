#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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

def _main ():
    """USAGE: test/run.sh test/block.py <url>"""
    import sys
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    url = sys.argv[1]
    data = "GET %s HTTP/1.0" % url
    from test import initlog
    initlog("test/logging.conf")
    import wc
    from wc.proxy.Headers import WcMessage
    wc.config = wc.init()
    wc.config['filters'] = ['Blocker',]
    wc.config.init_filter_modules()
    from wc.filter import applyfilter, get_filterattrs, FILTER_REQUEST
    headers = WcMessage()
    headers['Content-Type'] = "text/html"
    attrs = get_filterattrs(url, [FILTER_REQUEST], headers=headers)
    print applyfilter(FILTER_REQUEST, data, 'finish', attrs)


if __name__=='__main__':
    _main()
