#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter JavaScript.
"""

import sys
import os
import wc.configuration
import wc.js.jslib
import wc.js.JSListener


class JSFilter(wc.js.JSListener.JSListener):
    """defines callback handlers for filtering Javascript code"""

    def __init__(self, script, ver):
        self.js_env = wc.js.jslib.JSEnv()
        self.js_env.listeners.append(self)
        self.js_env.executeScript(script, ver)
        self.js_env.listeners.remove(self)

    def _str__(self):
        return self.__class__.__name__

    def js_process_data(self, data):
        """produced by document.write() JavaScript"""
        print "jsProcessData", repr(data)

    def js_process_popup(self):
        """process javascript popup"""
        print "jsProcessPopup"

    def js_process_error(self, msg):
        """process javascript syntax error"""
        print "jsProcessError", msg


def _main():
    """
    USAGE: scripts/run.sh test/filterjs.py <configdir> <.js file>
    """
    if len(sys.argv) != 3:
        print _main.__doc__.strip()
        sys.exit(1)
    confdir = sys.argv[1]
    fname = sys.argv[2]
    if fname == "-":
        f = sys.stdin
    else:
        f = file(fname)
    try:
        logfile = os.path.join(confdir, "logging.conf")
        wc.initlog(logfile, filelogs=False)
        config = wc.configuration.init(confdir=confdir)
        config.init_filter_modules()
        wc.proxy.dns_lookups.init_resolver()
        script = f.read()
        ver = 1.1
        JSFilter(script, ver)
    finally:
        f.close()


if __name__ == '__main__':
    _main()
