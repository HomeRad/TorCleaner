"""AllowRule frame widget"""
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
    (ID_SCHEME,
     ID_HOST,
     ID_PORT,
     ID_PATH,
     ID_PARAMETERS,
     ID_QUERY,
     ID_FRAGMENT,
     ID_LAST,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+8)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_SCHEME,FXAllowRuleFrame.onCmdScheme)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_HOST,FXAllowRuleFrame.onCmdHost)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PORT,FXAllowRuleFrame.onCmdPort)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PATH,FXAllowRuleFrame.onCmdPath)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PARAMETERS,FXAllowRuleFrame.onCmdParameters)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_QUERY,FXAllowRuleFrame.onCmdQuery)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_FRAGMENT,FXAllowRuleFrame.onCmdFragment)
        self.matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(self.matrix, i18n._("URL Scheme:\tRegular expression to match the URL scheme"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_SCHEME)
        tf.setText(self.rule.scheme)
        FXLabel(self.matrix, i18n._("URL Host:\tRegular expression to match the host"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_HOST)
        tf.setText(self.rule.host)
        FXLabel(self.matrix, i18n._("URL Port:\tRegular expression to match the port"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PORT)
        tf.setText(self.rule.port)
        FXLabel(self.matrix, i18n._("URL Path:\tRegular expression to match the path"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PATH)
        tf.setText(self.rule.path)
        FXLabel(self.matrix, i18n._("URL Parameters:\tRegular expression to match the parameters"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PARAMETERS)
        tf.setText(self.rule.parameters)
        FXLabel(self.matrix, i18n._("URL Query:\tRegular expression to match the query"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_QUERY)
        tf.setText(self.rule.query)
        FXLabel(self.matrix, i18n._("URL Fragment:\tRegular expression to match the fragment"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_FRAGMENT)
        tf.setText(self.rule.fragment)

    def onCmdScheme (self, sender, sel, ptr):
        self.rule.scheme = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule scheme")
        return 1

    def onCmdHost (self, sender, sel, ptr):
        self.rule.host = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule host")
        return 1

    def onCmdPort (self, sender, sel, ptr):
        self.rule.host = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule port")
        return 1

    def onCmdPath (self, sender, sel, ptr):
        self.rule.path = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule path")
        return 1

    def onCmdParameters (self, sender, sel, ptr):
        self.rule.parameters = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule parameters")
        return 1

    def onCmdQuery (self, sender, sel, ptr):
        self.rule.query = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule query")
        return 1

    def onCmdFragment (self, sender, sel, ptr):
        self.rule.fragment = sender.getText().strip()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule fragment")
        return 1

