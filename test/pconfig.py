#!/usr/bin/python2.3
# -*- coding: iso-8859-1 -*-
"""configuration loading profiling
"""
import wc

def _main ():
    """USAGE: test/run.sh test/pconfig.py"""
    from test import initlog
    initlog("test/logging.conf")
    import hotshot
    profile = hotshot.Profile("config.prof")
    profile.run("config = wc.Configuration()")
    profile.close()


if __name__=='__main__':
    _main()
