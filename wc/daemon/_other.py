"""generic daemon helper functions"""
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

from wc import i18n

def start (startfunc, pidfile, parent_exit=True):
    """does not return"""
    startfunc()

def stop (pidfile):
    return "", 0

def reload (pidfile):
    return i18n._("reload not supported for this platform"), 1

def startwatch (startfunc, pidfile, watchfile, parent_exit=True, sleepsecs=5):
    return start(startfunc, pidfile)

def stopwatch (pidfile, watchfile):
    return stop(pidfile)
