"""POSIX specific daemon helper functions"""
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
import os
from wc import i18n
from wc.daemon import pidfile, watchfile, startfunc

def start (parent_exit=1):
    """start a daemon using the appropriate pidfile"""
    # already running?
    if os.path.exists(pidfile):
        return i18n._("""WebCleaner already started (lock file found).
Do 'webcleaner stop' first.""")
    # forking (only under POSIX systems)
    
    # the parent exits
    if os.fork()!=0:
        if parent_exit:
            os._exit(0)
        else:
            return
    # create new session and fork once more
    os.setsid()
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    # drop privileges
    os.chdir("/")
    os.umask(0177)
    # XXX close if we have a logfile?
    #os.close(sys.__stdin__.fileno())
    #os.close(sys.__stdout__.fileno())
    #os.close(sys.__stderr__.fileno())
    # write pid in pidfile
    f = open(pidfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    # starting
    startfunc()


def stop ():
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner was not running (no lock file found)"), 0
    return _stop(pidfile)


def _stop (file):
    pid=int(open(file).read())
    import signal
    msg = None
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        msg = i18n._("warning: could not terminate process PID %d")%pid
    os.remove(file)
    return msg, 0


def startwatch (parent_exit=1, sleepsecs=5):
    """start a monitoring daemon for webcleaner"""
    import time
    if os.path.exists(watchfile):
        return i18n._("""Watch program already started (lock file found).""")
    pid = os.fork()
    if pid!=0:
        if parent_exit:
            raise SystemExit
        else:
            return
    f = open(watchfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    while 1:
        if os.path.exists(pidfile):
            pid = int(open(pidfile).read())
            # linux
            if not os.path.isdir("/proc/%d"%pid):
                start(parent_exit=0)
        else:
            start(parent_exit=0)
        time.sleep(sleepsecs)


def stopwatch ():
    """stop webcleaner and the monitor"""
    msg = stop() or ""
    if not os.path.exists(watchfile):
        if msg: msg += "\n"
        return msg+i18n._("Watcher was not running (no lock file found)")
    _stop(watchfile)


def reload ():
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner is not running. Do 'webcleaner start' first.")
    pid = int(open(pidfile).read())
    import signal
    os.kill(pid, signal.SIGHUP)
