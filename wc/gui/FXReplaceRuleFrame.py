"""ReplaceRule frame widget"""
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

class FXReplaceRuleFrame (FXRuleFrame):
    """display all variables found in a ReplaceRule"""
    (ID_SEARCH,
     ID_REPLACE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+2)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self, SEL_COMMAND, FXReplaceRuleFrame.ID_SEARCH, FXReplaceRuleFrame.onCmdSearch)
        FXMAPFUNC(self, SEL_COMMAND, FXReplaceRuleFrame.ID_REPLACE, FXReplaceRuleFrame.onCmdReplace)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Replace regex:\tRegular expression to match the data stream"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXReplaceRuleFrame.ID_SEARCH)
        tf.setText(self.rule.search)
        FXLabel(matrix, i18n._("Replacement:\tReplacement value (empty means delete)"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXReplaceRuleFrame.ID_REPLACE)
        tf.setText(self.rule.replace)

    def onCmdSearch (self, sender, sel, ptr):
        self.rule.search = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed replace rule search value")
        return 1

    def onCmdReplace (self, sender, sel, ptr):
        self.rule.replace = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed replace rule replace value")
        return 1

