"""POSIX specific daemon helper functions"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2001-2003  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys
from wc import i18n
from wc.daemon import pidfile, watchfile, startfunc

def start (parent_exit=True):
    """start a daemon using the appropriate pidfile"""
    # already running?
    if os.path.exists(pidfile):
        return i18n._("""WebCleaner already started (lock file found).
Do 'webcleaner stop' first."""), 1
    # forking (only under POSIX systems)
    
    # the parent exits
    if os.fork()!=0:
        if parent_exit:
            os._exit(0)
        else:
            return None
    # create new session and fork once more
    os.setsid()
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    # set umask
    os.umask(0177)
    # we are logging into files, so close these files:
    os.close(sys.__stdin__.fileno())
    os.close(sys.__stdout__.fileno())
    os.close(sys.__stderr__.fileno())
    # write pid in pidfile
    f = file(pidfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    # start function
    startfunc()
    return None


def stop ():
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner was not running (no lock file found)"), 0
    return _stop(pidfile)


def _stop (_pidfile):
    pid = int(file(_pidfile).read())
    import signal
    msg = None
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        msg = i18n._("warning: could not terminate process PID %d")%pid
    os.remove(_pidfile)
    return msg, 0


def startwatch (parent_exit=True, sleepsecs=5):
    """start a monitoring daemon for webcleaner"""
    import time
    if os.path.exists(watchfile):
        return i18n._("""Watch program already started (lock file found)."""), 1
    pid = os.fork()
    if pid!=0:
        if parent_exit:
            raise SystemExit
        else:
            return
    f = file(watchfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    while 1:
        if os.path.exists(pidfile):
            pid = int(file(pidfile).read())
            # linux
            if not os.path.isdir("/proc/%d"%pid):
                start(parent_exit=0)
        else:
            start(parent_exit=False)
        time.sleep(sleepsecs)
    return "", 0


def stopwatch ():
    """stop webcleaner and the monitor"""
    msg, status = stop() or ""
    if not os.path.exists(watchfile):
        if msg: msg += "\n"
        return msg+i18n._("Watcher was not running (no lock file found)"), 1
    return _stop(watchfile)


def reload ():
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner is not running. Do 'webcleaner start' first."), 1
    pid = int(file(pidfile).read())
    import signal
    os.kill(pid, signal.SIGHUP)
    return "", 0
