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

def start (startfunc, pidfile, parent_exit=True, do_profile=False):
    """start a daemon using the appropriate pidfile"""
    # already running?
    if os.path.exists(pidfile):
        return i18n._("""WebCleaner already started (lock file found).
Do 'webcleaner stop' first."""), 1
    # forking (only under POSIX systems)

    # the parent exits
    if os.fork() != 0:
        if parent_exit:
            os._exit(0)
        else:
            return "", 0
    # create new session and fork once more
    os.setsid()
    if os.fork() != 0:
        os._exit(0)
    # set umask
    os.umask(0177)
    # we are logging into files, so close unused handles (except stderr
    # used by the logging module)
    os.close(sys.__stdin__.fileno())
    os.close(sys.__stdout__.fileno())
    # write pid in pidfile
    f = file(pidfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    # start function
    if do_profile:
        import profile
        profile.run("startfunc", "webcleaner.prof")
    else:
        startfunc()
    return "", 0


def stop (pidfile):
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner was not running (no lock file found)"), 0
    return _stop(pidfile)


def _stop (pidfile):
    pid = int(file(pidfile).read())
    import signal
    msg = None
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        msg = i18n._("warning: could not terminate process PID %d")%pid
    os.remove(pidfile)
    return msg, 0


def startwatch (startfunc, pidfile, watchfile, parent_exit=True, sleepsecs=5):
    """start a monitoring daemon for webcleaner"""
    import time
    if os.path.exists(watchfile):
        return i18n._("""Watch program already started (lock file found)."""), 1
    if os.fork() != 0:
        if parent_exit:
            raise SystemExit
        else:
            return "", 0
    f = file(watchfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    while 1:
        if os.path.exists(pidfile):
            pid = int(file(pidfile).read())
            # linux specific?
            if not os.path.isdir("/proc/%d"%pid):
                # XXX detect zombie state?
                msg, status = start(startfunc, pidfile, parent_exit=False)
        else:
            msg, status = start(startfunc, pidfile, parent_exit=False)
        # XXX check status here?
        time.sleep(sleepsecs)
    return "", 0


def stopwatch (pidfile, watchfile):
    """stop webcleaner and the monitor"""
    if not os.path.exists(watchfile):
        return i18n._("Watcher was not running (no lock file found)"), 1
    msg1, status1 = _stop(watchfile)
    msg2, status2 = stop(pidfile)
    if msg1:
        if msg2:
            msg = "%s\n%s"%(msg1,msg2)
        else:
            msg = msg1
    else:
        msg = msg2
    if status1:
        status = status1
    else:
        status = status2
    return msg, status


def reload (pidfile):
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner is not running. Do 'webcleaner start' first."), 1
    pid = int(file(pidfile).read())
    import signal
    os.kill(pid, signal.SIGHUP)
    return "", 0
