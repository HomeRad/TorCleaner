"""HeaderRule frame widget"""
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
from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.debug import *

class FXHeaderRuleFrame (FXRuleFrame):
    """display all variables found in a HeaderRule"""
    (ID_NAME,
     ID_VALUE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+2)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXHeaderRuleFrame.ID_NAME,FXHeaderRuleFrame.onCmdName)
        FXMAPFUNC(self,SEL_COMMAND,FXHeaderRuleFrame.ID_VALUE,FXHeaderRuleFrame.onCmdValue)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Header name:\tRegular expression to match the header name"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXHeaderRuleFrame.ID_NAME)
        tf.setText(self.rule.name)
        FXLabel(matrix, i18n._("Header value:\tIf empty, delete the header. Else add or, if already there modify the header."), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXHeaderRuleFrame.ID_VALUE)
        tf.setText(self.rule.value)

    def onCmdName (self, sender, sel, ptr):
        name = sender.getText().strip()
        if name:
            self.rule.name = name
            self.getApp().dirty = 1
        else:
            sender.setText(self.rule.name)
            self.getApp().error(i18n._("Header rule"), i18n._("Header name must not be empty"))
        debug(BRING_IT_ON, "Changed rule header name")
        return 1

    def onCmdValue (self, sender, sel, ptr):
        self.rule.value = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule header value")
        return 1

