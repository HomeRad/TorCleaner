from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

class FXAllowRuleFrame(FXRuleFrame):
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

    def __init__(self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_SCHEME,FXAllowRuleFrame.onCmdScheme)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_HOST,FXAllowRuleFrame.onCmdHost)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PORT,FXAllowRuleFrame.onCmdPort)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PATH,FXAllowRuleFrame.onCmdPath)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_PARAMETERS,FXAllowRuleFrame.onCmdParameters)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_QUERY,FXAllowRuleFrame.onCmdQuery)
        FXMAPFUNC(self,SEL_COMMAND,FXAllowRuleFrame.ID_FRAGMENT,FXAllowRuleFrame.onCmdFragment)
        self.matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(self.matrix, _("URL Scheme:\tRegular expression to match the URL scheme"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_SCHEME)
        tf.setText(self.rule.scheme)
        FXLabel(self.matrix, _("URL Host:\tRegular expression to match the host"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_HOST)
        tf.setText(self.rule.host)
        FXLabel(self.matrix, _("URL Port:\tRegular expression to match the port"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PORT)
        tf.setText(self.rule.port)
        FXLabel(self.matrix, _("URL Path:\tRegular expression to match the path"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PATH)
        tf.setText(self.rule.path)
        FXLabel(self.matrix, _("URL Parameters:\tRegular expression to match the parameters"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_PARAMETERS)
        tf.setText(self.rule.parameters)
        FXLabel(self.matrix, _("URL Query:\tRegular expression to match the query"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_QUERY)
        tf.setText(self.rule.query)
        FXLabel(self.matrix, _("URL Fragment:\tRegular expression to match the fragment"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(self.matrix, 25, self, FXAllowRuleFrame.ID_FRAGMENT)
        tf.setText(self.rule.fragment)

    def onCmdScheme(self, sender, sel, ptr):
        self.rule.scheme = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule scheme")
        return 1

    def onCmdHost(self, sender, sel, ptr):
        self.rule.host = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule host")
        return 1

    def onCmdPort(self, sender, sel, ptr):
        self.rule.host = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule port")
        return 1

    def onCmdPath(self, sender, sel, ptr):
        self.rule.path = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule path")
        return 1

    def onCmdParameters(self, sender, sel, ptr):
        self.rule.parameters = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule parameters")
        return 1

    def onCmdQuery(self, sender, sel, ptr):
        self.rule.query = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule query")
        return 1

    def onCmdFragment(self, sender, sel, ptr):
        self.rule.fragment = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule fragment")
        return 1

