from FXAllowRuleFrame import FXAllowRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

class FXBlockRuleFrame(FXAllowRuleFrame):
    """display all variables found in a BlockRule"""
    ID_URL = FXAllowRuleFrame.ID_LAST

    def __init__(self, parent, rule, index):
        FXAllowRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXBlockRuleFrame.ID_URL,FXBlockRuleFrame.onCmdUrl)
        FXLabel(self.matrix, _("Blocked URL\tThe URL we want to show instead"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 15, self, FXBlockRuleFrame.ID_URL)
        tf.setText(self.rule.fragment)

    def onCmdUrl(self, sender, sel, ptr):
        self.rule.url = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule blocked url")
        return 1



