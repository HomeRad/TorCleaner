import string
from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

class FXReplaceRuleFrame(FXRuleFrame):
    """display all variables found in a ReplaceRule"""
    (ID_SEARCH,
     ID_REPLACE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+2)

    def __init__(self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXReplaceRuleFrame.ID_SEARCH,FXReplaceRuleFrame.onCmdSearch)
        FXMAPFUNC(self,SEL_COMMAND,FXReplaceRuleFrame.ID_REPLACE,FXReplaceRuleFrame.onCmdReplace)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Replace regex:\tRegular expression to match the data stream"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXReplaceRuleFrame.ID_SEARCH)
        tf.setText(self.rule.search)
        FXLabel(matrix, _("Replacement:\tReplacement value (empty means delete)"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXReplaceRuleFrame.ID_REPLACE)
        tf.setText(self.rule.replace)

    def onCmdSearch(self, sender, sel, ptr):
        self.rule.search = string.strip(sender.getText())
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed replace rule search value")
        return 1

    def onCmdReplace(self, sender, sel, ptr):
        self.rule.replace = string.strip(sender.getText())
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed replace rule replace value")
        return 1



