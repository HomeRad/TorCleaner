# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
"""
Proxy start function.
"""

import os
from . import (configuration, log, fileutil, ConfigDir, initlog,
    HasProfile, HasPsyco, LOG_PROXY, clamav)
from .proxy import mainloop, timer, dns_lookups


def wstartfunc(handle=None, confdir=ConfigDir, filelogs=True,
                profiling=False):
    """
    Initalize configuration, start psyco compiling and the proxy loop.
    This function does not return until Ctrl-C is pressed.
    """
    # init logging
    logconf = os.path.join(confdir, "logging.conf")
    def checklog():
        if fileutil.has_changed(logconf):
            initlog(filename=logconf, filelogs=filelogs)
        # check regularly for a changed logging configuration
        timer.make_timer(60, checklog)
    checklog()
    # read configuration
    config = configuration.init(confdir)
    clamav.init_clamav_conf(config['clamavconf'])
    config.init_filter_modules()
    dns_lookups.init_resolver()
    if profiling and HasProfile:
        _profile = "webcleaner.prof"
        run = True
        if os.path.exists(_profile):
            question = "Overwrite profiling file %r?\n" \
                      "Press Ctrl-C to cancel, RETURN to continue." % _profile
            try:
                raw_input(question)
            except KeyboardInterrupt:
                import sys
                print >> sys.stderr
                print >> sys.stderr, "Canceled."
                run = False
        if run:
            import profile
            prof = profile.Profile()
            try:
                prof.runcall(mainloop.mainloop, handle=handle)
            except KeyboardInterrupt:
                pass
            prof.dump_stats(_profile)
            return
    load_psyco()
    # start the proxy
    mainloop.mainloop(handle=handle)


def load_psyco():
    """
    Load psyco library for speedup.
    """
    if HasPsyco:
        import psyco
        # psyco >= 1.4.0 final is needed
        if psyco.__version__ >= 0x10400f0:
            #psyco.log(logfile="psyco.log")
            psyco.profile(memory=10000, memorymax=100000)
        else:
            # warn about old psyco version
            log.warn(LOG_PROXY,
         _("Psyco is installed but not used since the version is too old.\n"
           "Psyco >= 1.4 is needed."))


def restart():
    """
    Restart the runit service. Assumes a standard installation, ie.
    it will not work if installed in custom directory.
    """
    service = "/var/service/webcleaner"
    stop_cmd = "svwaitdown -k -t 5 %s" % service
    start_cmd = "runsvctrl up %s" % service
    status = os.system(stop_cmd)
    if status != 0:
        log.error(LOG_PROXY,
                     "Stop command %r failed: %s", stop_cmd, str(status))
    status = os.system(start_cmd)
    if status != 0:
        log.error(LOG_PROXY,
                     "Start command %r failed: %s", start_cmd, str(status))
