"""AllowRule frame widget"""
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

from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.log import *

class FXAllowRuleFrame (FXRuleFrame):
    """display all variables found in an AllowRule"""
    (ID_URL,
     ID_LAST,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+2)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_URL,FXAllowRuleFrame.onCmdUrl)
        self.matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(self.matrix, i18n._("URL:\tRegular expression to match the URL"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_URL)
        tf.setText(self.rule.url)

    def onCmdUrl (self, sender, sel, ptr):
        self.rule.url = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule url")
        return 1
