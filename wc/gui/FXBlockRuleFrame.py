"""BlockRule frame widget"""
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
from FXAllowRuleFrame import FXAllowRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.log import *

class FXBlockRuleFrame (FXAllowRuleFrame):
    """display all variables found in a BlockRule"""
    ID_URL = FXAllowRuleFrame.ID_LAST

    def __init__ (self, parent, rule, index):
        FXAllowRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXBlockRuleFrame.ID_URL,FXBlockRuleFrame.onCmdUrl)
        FXLabel(self.matrix, i18n._("Blocked URL\tThe URL we want to show instead"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXBlockRuleFrame.ID_URL)
        tf.setText(self.rule.fragment)

    def onCmdUrl (self, sender, sel, ptr):
        self.rule.url = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule blocked url")
        return 1

