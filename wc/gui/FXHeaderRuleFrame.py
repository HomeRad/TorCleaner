from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

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
        FXLabel(matrix, _("Header name:\tRegular expression to match the header name"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXHeaderRuleFrame.ID_NAME)
        tf.setText(self.rule.name)
        FXLabel(matrix, _("Header value:\tHeader value (empty means delete)"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 15, self, FXHeaderRuleFrame.ID_VALUE)
        tf.setText(self.rule.value)

    def onCmdName (self, sender, sel, ptr):
        name = sender.getText().strip()
        if name:
            self.rule.name = name
            self.getApp().dirty = 1
        else:
            sender.setText(self.rule.name)
            self.getApp().error(_("Header rule"), _("Header name must not be empty"))
        debug(BRING_IT_ON, "Changed rule header name")
        return 1

    def onCmdValue (self, sender, sel, ptr):
        self.rule.value = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule header value")
        return 1

