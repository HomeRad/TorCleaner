"""Windows specific daemon helper functions.
   Needs Active Python (with win32api module) installed.
"""
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

import os,sys
from wc.daemon import startfunc,pidfile
from wc.debug_levels import *
from wc import debug

def start():
    # already running?
    if os.path.exists(pidfile):
        return """webcleaner already started (lock file found).
Do 'webcleaner stop' first."""
    command = (sys.executable, 'webcleaner', 'start_nt')
    from wc.proxy import winreg
    mode = os.P_DETACH
    try:
        # under Windows NT/2000 we can use NOWAIT
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
                 r"Software\Microsoft\Windows NT\CurrentVersion")
        val = key["CurrentVersion"]
        mode = os.P_NOWAIT
    except EnvironmentError:
        pass
    except IndexError:
        # key not found
        pass
    try:
        ret = os.spawnv(mode, command[0], command)
    except OSError, exc:
        # this seems to happen when the command isn't found
        raise Exception, \
              "command '%s' failed: %s" % (command, exc[-1])
    if ret < 0:
        # and this reflects the command running but failing
        raise Exception, \
              "command '%s' killed by signal %d" % (command, -ret)


def start_nt(parent_exit=1):
    # no need to spawn in this thing
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
        return "WebCleaner was not running (no lock file found)"
    pid = int(open(pidfile).read())
    msg = None
    import win32api
    try:
        handle = win32api.OpenProcess(1, 0, pid)
        rc = win32api.TerminateProcess(handle, 0)
    except win32api.error:
        msg = "warning: could not terminate process PID %d"%pid
    os.remove(pidfile)
    return msg


def reload():
    return "reload not supported for this platform"
