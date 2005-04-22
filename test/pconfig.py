#!/usr/bin/python2.4
# -*- coding: iso-8859-1 -*-
"""
Configuration loading profiling.
"""
import wc

def _main ():
    """USAGE: test/run.sh test/pconfig.py"""
    from test import initlog
    initlog("test/logging.conf")
    import hotshot
    profile = hotshot.Profile("config.prof")
    profile.run("config = wc.configuration.init()")
    profile.close()


if __name__=='__main__':
    _main()
