# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
Proxy start function.
"""

import os
import wc
import wc.configuration
import wc.url
import wc.log
import wc.proxy
import wc.proxy.mainloop
import wc.proxy.timer
import wc.proxy.dns_lookups
import wc.filter
import wc.filter.VirusFilter


def wstartfunc (handle=None, confdir=wc.ConfigDir, filelogs=True,
                profiling=False):
    """
    Initalize configuration, start psyco compiling and the proxy loop.
    This function does not return until Ctrl-C is pressed.
    """
    # init logging
    logconf = os.path.join(confdir, "logging.conf")
    def checklog ():
        if wc.fileutil.has_changed(logconf):
            wc.initlog(filename=logconf, filelogs=filelogs)
        # check regularly for a changed logging configuration
        wc.proxy.timer.make_timer(60, checklog)
    checklog()
    # read configuration
    config = wc.configuration.init(confdir)
    wc.filter.VirusFilter.init_clamav_conf(config['clamavconf'])
    config.init_filter_modules()
    wc.proxy.dns_lookups.init_resolver()
    if profiling and wc.HasProfile:
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
                prof.runcall(wc.proxy.mainloop.mainloop, handle=handle)
            except KeyboardInterrupt:
                pass
            prof.dump_stats(_profile)
            return
    load_psyco()
    # start the proxy
    wc.proxy.mainloop.mainloop(handle=handle)


def load_psyco ():
    """
    Load psyco library for speedup.
    """
    if wc.HasPsyco:
        import psyco
        # psyco >= 1.4.0 final is needed
        if psyco.__version__ >= 0x10400f0:
            #psyco.log(logfile="psyco.log")
            psyco.profile(memory=10000, memorymax=100000)
        else:
            # warn about old psyco version
            wc.log.warn(wc.LOG_PROXY,
         _("Psyco is installed but not used since the version is too old.\n"
           "Psyco >= 1.4 is needed."))


def restart ():
    """
    Restart the runit service. Assumes a standard installation, ie.
    it will not work if installed in custom directory.
    """
    service = "/var/service/webcleaner"
    stop_cmd = "svwaitdown -k -t 5 %s" % service
    start_cmd = "runsvctrl up %s" % service
    status = os.system(stop_cmd)
    if status != 0:
        wc.log.error(wc.LOG_PROXY,
                     "Stop command %r failed: %s", stop_cmd, str(status))
    status = os.system(start_cmd)
    if status != 0:
        wc.log.error(wc.LOG_PROXY,
                     "Start command %r failed: %s", start_cmd, str(status))
