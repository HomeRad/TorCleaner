"""helper functions to start, stop, restart and reload daemons.

Of course this is OS dependent and currently we support only Unix
natively, the other OSes use a generic interface with no fork().
"""
#    Copyright (C) 2001  Bastian Kleineidam
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
import os
from wc import startfunc

def iswriteable(file):
    if os.path.isdir(file) or os.path.islink(file):
        return 0
    try:
        if os.path.exists(file):
            f = open(file, 'a')
            f.close()
            return 1
        else:
            f = open(file, 'w')
            f.close()
            os.remove(file)
            return 1
    except IOError:
        pass
    return 0


pidfile='/var/run/webcleaner.pid'
if not iswriteable(pidfile):
    pidfile = '/var/tmp/webcleaner.pid'
if not iswriteable(pidfile):
    pidfile = '/tmp/webcleaner.pid'
if not iswriteable(pidfile):
    pidfile = 'webcleaner.pid'


def restart():
    stop()
    # sleep 2 seconds, should be enough to clean up
    import time
    time.sleep(2)
    start()


def status():
    if os.path.exists(pidfile):
        pid = open(pidfile).read()
        return "WebCleaner is running (PID %s)" % pid
    else:
        return "WebCleaner is not running"

# import platform specific functions
if os.name=='posix':
    from _posix import *
# process things for Windoze: not yet implemented
#elif os.name=='nt':
#    from _nt import *
else:
    from _other import *

