# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
import wc.proxy.dns_lookups
import wc.filter
import wc.filter.VirusFilter


def wstartfunc (handle=None, abort=None, confdir=wc.ConfigDir, filelogs=True):
    """
    Initalize configuration, start psyco compiling and the proxy loop.
    This function does not return until Ctrl-C is pressed.
    """
    # init logging
    wc.initlog(os.path.join(confdir, "logging.conf"),
               wc.Name, filelogs=filelogs)
    # read configuration
    config = wc.configuration.init(confdir)
    if abort is not None:
        abort(False)
    # support reload on posix systems
    elif os.name == 'posix':
        import signal
        signal.signal(signal.SIGHUP, wc.configuration.sighup_reload_config)
    config.init_filter_modules()
    wc.filter.VirusFilter.init_clamav_conf()
    wc.proxy.dns_lookups.init_resolver()
    # psyco library for speedup
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    # start the proxy
    wc.proxy.mainloop(handle=handle, abort=abort)


def restart ():
    # XXX this does not work on custom installations
    service = "/var/service/webcleaner"
    stop_cmd = "svwaitdown -k -t 5 %s" % service
    start_cmd = "runsvctrl up %s" % service
    status = os.system(stop_cmd)
    if status != 0:
        error["stopfail"] = True
    status = os.system(start_cmd)
    if status != 0:
        error["startfail"] = True
