#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
"""
Filter JavaScript.
"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sys
import wc
import wc.js
import wc.js.jslib
import wc.js.JSListener
import wc.filter.rules.RewriteRule


class JSFilter (wc.js.JSListener.JSListener):
    """defines callback handlers for filtering Javascript code"""

    def __init__ (self, script, ver):
        self.js_env = wc.js.jslib.JSEnv()
        self.js_env.listeners.append(self)
        self.js_env.executeScript(script, ver)
        self.js_env.listeners.remove(self)

    def _str__ (self):
        return self.__class__.__name__

    def jsProcessData (self, data):
        """produced by document.write() JavaScript"""
        print "jsProcessData", repr(data)

    def jsProcessPopup (self):
        """process javascript popup"""
        print "jsProcessPopup"

    def jsProcessError (self, msg):
        """process javascript syntax error"""
        print "jsProcessError", msg


def _main ():
    """USAGE: test/run.sh test/filterjs.py <.js file>"""
    if len(sys.argv)!=2:
        print _main.__doc__
        sys.exit(1)
    fname = sys.argv[1]
    if fname=="-":
        f = sys.stdin
    else:
        f = file(fname)
    from test import initlog, disable_rating_rules
    initlog("test/logging.conf")
    wc.configuration.config = wc.configuration.init()
    disable_rating_rules(wc.config)
    wc.config['filters'] = ['Replacer', 'Rewriter', 'BinaryCharFilter']
    wc.config.init_filter_modules()
    script = f.read()
    ver = 1.1
    JSFilter(script, ver)


if __name__=='__main__':
    _main()
