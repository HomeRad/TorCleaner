from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

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
        FXLabel(matrix, _("Image width:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXSpinner(matrix, 4, self, FXImageRuleFrame.ID_WIDTH, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        t.setRange(0,65535)
        t.setValue(self.rule.width)
        FXLabel(matrix, _("Image height:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXSpinner(matrix, 4, self, FXImageRuleFrame.ID_HEIGHT, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        t.setRange(0,65535)
        t.setValue(self.rule.height)

    def onCmdWidth (self, sender, sel, ptr):
        self.rule.width = sender.getValue()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule image width")
        return 1

    def onCmdHeight (self, sender, sel, ptr):
        self.rule.height = sender.getValue()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule image height")
        return 1

