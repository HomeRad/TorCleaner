#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""configuration loading profiling
"""
import wc

def _main ():
    """USAGE: test/run.sh test/pconfig.py"""
    from test import initlog
    initlog("test/logging.conf")
    import profile
    profile.run("config = wc.Configuration()", "filter.prof")


if __name__=='__main__':
    _main()
