"""Toolwindow"""
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
from FXPy.fox import *
from wc.gui import loadIcon
from wc import i18n, AppInfo

class ToolWindow (FXMainWindow):
    """common base class for webcleaner tool windows"""
    def __init__ (self, app, name):
	FXMainWindow.__init__(self, app, name)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.about = FXMessageBox(self, i18n._("About WebCleaner"), AppInfo, self.getIcon(),MBOX_OK)

    def create (self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()

