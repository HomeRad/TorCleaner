"""Windows specific daemon helper functions.
   Needs Active Python (with win32api module) installed.
"""
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

# try this sometimes:
#win32process.SetThreadPriority(win32api.GetCurrentThread(),
#                               win32process.THREAD_PRIORITY_BELOW_NORMAL)

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys
from wc.debug import *
from wc import i18n, configdata

def start (startfunc, pidfile, parent_exit=True):
    # already running?
    if os.path.exists(pidfile):
        return i18n._("""WebCleaner already started (lock file found).
Do 'webcleaner stop' first."""), 0
    script = os.path.join(configdata.install_scripts, 'webcleaner')
    command = (sys.executable, script, 'start_nt')
    from wc.proxy import winreg
    mode = os.P_DETACH
    try:
        # under Windows NT/2000 we can use NOWAIT
        key = winreg.key_handle(winreg.HKEY_LOCAL_MACHINE,
                 r"Software\Microsoft\Windows NT\CurrentVersion")
        val = key["CurrentVersion"]
        # XXX
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
              i18n._("command '%s' failed: %s") % (command, exc[-1])
    if ret < 0:
        # and this reflects the command running but failing
        raise Exception, \
              i18n._("command '%s' killed by signal %d") % (command, -ret)
    return "", 0


def start_nt (startfunc, pidfile, parent_exit=True):
    # no need to spawn in this thing
    # write pid in pidfile
    f = file(pidfile, 'w')
    f.write("%d" % os.getpid())
    f.close()
    # starting
    startfunc()


def stop (pidfile):
    if not os.path.exists(pidfile):
        return i18n._("WebCleaner was not running (no lock file found)"), 0
    pid = int(file(pidfile).read())
    msg = None
    import win32api
    try:
        handle = win32api.OpenProcess(1, 0, pid)
        rc = win32api.TerminateProcess(handle, 0)
    except win32api.error:
        msg = i18n._("warning: could not terminate process PID %d")%pid
    os.remove(pidfile)
    return msg, 0


def startwatch (startfunc, pidfile, parent_exit=True, sleepsecs=5):
    return start(startfunc, pidfile)


def stopwatch (pidfile, watchfile):
    return stop(pidfile)


def reload ():
    return i18n._("reload not supported for this platform"), 1
