"""BlockRule frame widget"""
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

from FXAllowRuleFrame import FXAllowRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.log import *

class FXBlockRuleFrame (FXAllowRuleFrame):
    """display all variables found in a BlockRule"""
    ID_REPLACEMENT = FXAllowRuleFrame.ID_LAST

    def __init__ (self, parent, rule, index):
        FXAllowRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXBlockRuleFrame.ID_REPLACEMENT,FXBlockRuleFrame.onCmdReplacement)
        FXLabel(self.matrix, i18n._("URL replacement\tThe URL we want to show instead"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXBlockRuleFrame.ID_REPLACEMENT)
        tf.setText(self.rule.replacement)

    def onCmdUrl (self, sender, sel, ptr):
        self.rule.replacement = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule blocked url replacement")
        return 1

