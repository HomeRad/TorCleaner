"""ImageRule frame widget"""
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

class FXImageRuleFrame (FXRuleFrame):
    """display all variables found in a ImageRule"""
    (ID_WIDTH,
     ID_HEIGHT,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+2)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXImageRuleFrame.ID_WIDTH,FXImageRuleFrame.onCmdWidth)
        FXMAPFUNC(self,SEL_COMMAND,FXImageRuleFrame.ID_HEIGHT,FXImageRuleFrame.onCmdHeight)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Image width:\tThe width of the image to be blocked."), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXSpinner(matrix, 4, self, FXImageRuleFrame.ID_WIDTH, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        t.setRange(0,65535)
        t.setValue(self.rule.width)
        FXLabel(matrix, i18n._("Image height:\tThe height of the image to be blocked."), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXSpinner(matrix, 4, self, FXImageRuleFrame.ID_HEIGHT, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        t.setRange(0,65535)
        t.setValue(self.rule.height)

    def onCmdWidth (self, sender, sel, ptr):
        self.rule.width = sender.getValue()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule image width")
        return 1

    def onCmdHeight (self, sender, sel, ptr):
        self.rule.height = sender.getValue()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule image height")
        return 1

