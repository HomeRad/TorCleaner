"""POSIX specific daemon helper functions"""
# Copyright (C) 2001  Bastian Kleineidam
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
from wc.daemon import pidfile,startfunc

def start(parent_exit=1):
    """start a daemon using the appropriate pidfile"""
    # already running?
    if os.path.exists(pidfile):
        return """webcleaner already started (lock file found).
Do 'webcleaner stop' first."""
    # forking (only under POSIX systems)
    pid = os.fork()
    # the parent exits
    if pid!=0:
        if parent_exit:
            raise SystemExit
        else:
            return
    # write pid in pidfile
    f = open(pidfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    # starting
    try:
        startfunc()
    except:
        if os.path.exists(pidfile):
	    os.remove(pidfile)
        raise


def stop():
    if not os.path.exists(pidfile):
        return "webcleaner was not running (no lock file found)"
    import signal
    msg = None
    pid = int(open(pidfile).read())
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        msg = "warning: could not terminate process PID %d"%pid
    os.remove(pidfile)
    return msg



def reload():
    if not os.path.exists(pidfile):
        return "webcleaner is not running. Do 'webcleaner start' first."
    pid = int(open(pidfile).read())
    import signal
    os.kill(int(open(pidfile).read()), signal.SIGHUP)

