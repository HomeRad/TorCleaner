"""Win32 specific daemon helper functions"""
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
from wc import startfunc,pidfile

def start():
    # already running?
    if os.path.exists(pidfile):
        raise Exception("webcleaner already started (lock file found). "
	                "Do 'webcleaner stop' first.")
    try:
        ret = os.spawnv(os.P_NOWAIT, os.path.normpath(sys.executable), ('webcleaner', 'start_nt'))
    except OSError, exc:
        # this seems to happen when the command isn't found
        print exc
        raise Exception, \
              "command '%s' failed: %s" % (cmd[0], exc[-1])
    if ret != 0:
        # and this reflects the command running but failing
        raise Exception, \
              "command '%s' failed with exit status %d" % (cmd[0], ret)


def start_nt():
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
        print "webcleaner was not running"
        return
    import win32api
    handle = win32api.OpenProcess(1, 0, int(open(pidfile).read()))
    rc = win32api.TerminateProcess(handle, 0)
    os.remove(pidfile)


def reload():
    raise Exception, "Reload not supported for this platform"
