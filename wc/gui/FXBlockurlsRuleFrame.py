from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.debug import *

class FXBlockurlsRuleFrame (FXRuleFrame):
    """Blocked urls"""

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Urlsfile\tExternal file with urls; one per line"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 25, self, self.ID_NOTHING)
        tf.setText(self.rule.file)
        tf.setEditable(0)

