"""Toolapp"""
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

from FXPy.fox import *
import sys

class ToolApp (FXApp):
    """common base class for webcleaner tool applications"""
    def __init__ (self, name):
        FXApp.__init__(self, name, "TheDude")
        # set default color scheme
        self.reg().writeColorEntry("SETTINGS","basecolor",FXRGB(141,157,170))
        self.reg().writeColorEntry("SETTINGS","backcolor",FXRGB(211,223,232))
        self.reg().writeColorEntry("SETTINGS","hilitecolor",FXRGB(226,225,220))
        self.reg().writeColorEntry("SETTINGS","shadowcolor",FXRGB(158,165,191))
        self.reg().writeColorEntry("SETTINGS","bordercolor",FXRGB(86,90,104))
        self.reg().writeColorEntry("SETTINGS","selbackcolor",FXRGB(20,58,84))
        self.init(sys.argv)
        # dirty flag for the apply button
        self.dirty = 0

    def error (self, title, msg):
        """display a message box with the error message"""
        dialog = FXMessageBox(self.getRoot(), title, msg, None, MBOX_OK)
        return self.doShow(dialog)

    def doShow (self, win):
        """show a modal dialog"""
        return win.execute(PLACEMENT_OWNER)
