"""FXPython gui classes"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

import sys, os, time, wc
from FXPy.fox import *


def get_time (secs):
    """return formatted timestamp"""
    t = time.localtime(secs)
    return time.strftime("%Y-%m-d %H:%M:%S", t)

# names of the filter types
Filternames = ['block', 'rewrite', 'allow', 'header', 'image', 'nocomments']

config = wc.Configuration()

def error (msg):
    sys.stderr.write("error: "+msg+"\n")

def loadIcon (app, filename):
    """load PNG icons"""
    themedir = os.path.join(wc.TemplateDir, config['gui_theme'])
    filename = os.path.join(themedir, filename)
    if filename[-4:].lower()=='.png':
        return FXPNGIcon(app, open(filename, 'rb').read())
    raise Exception("only PNG graphics supported")

