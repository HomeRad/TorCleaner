"""helper functions to start, stop, restart and reload daemons.

Of course this is OS dependent and currently we support only Posix
and Windows systems natively, the other OSes use a generic interface
with no fork().
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os, sys
from wc import i18n, startfunc, Version, iswriteable, AppName

def get_user ():
    """return current logged in user, or an empty string if there is no
    username available"""
    if hasattr(os, "getlogin"):
        try:
            return os.getlogin()
        except OSError, msg:
            print >>sys.stderr, "Error in os.getlogin():", msg
    return ""


# determine pid lockfile name
_fname = "%s-%s.pid" % (AppName, Version)
if os.name=="nt":
    pidfile = os.path.join(os.environ.get("TEMP"), _fname)
else:
    pidfile = os.path.join('/var/run', _fname)
    if not iswriteable(pidfile):
        # an unwriteable /var/run means we are not running as root
        # to enable multiple running webcleaner instances, we use a
        # user-specific lock file name
        _fname = get_user() + _fname
        pidfile = os.path.join('/var/tmp', _fname)
    if not iswriteable(pidfile):
        pidfile = os.path.join('/tmp', _fname)
# last fallback: the current directory
if not iswriteable(pidfile):
    pidfile = _fname
watchfile = pidfile+".watch"


def restart (parent_exit=True):
    msg1, status = stop()
    if status:
        return msg1, status
    # sleep 2 seconds, should be enough to clean up
    import time
    time.sleep(2)
    msg2, status = start(parent_exit=parent_exit)
    return (msg1 or "") + (msg2 or ""), status


def status ():
    if os.path.exists(pidfile):
        pid = open(pidfile).read()
        return i18n._("WebCleaner is running (PID %s)") % pid, 0
    else:
        return i18n._("WebCleaner is not running (no lock file found)"), 3


# import platform specific functions
# POSIX
if os.name=='posix':
    from _posix import *
# Windows
elif os.name=='nt':
    from _nt import *
# other
else:
    from _other import *
