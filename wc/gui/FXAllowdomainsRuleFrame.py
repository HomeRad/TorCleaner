from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

class FXAllowdomainsRuleFrame (FXRuleFrame):
    """Allowed domains"""

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Domainfile\tExternal file with domains; one per line"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        tf = FXTextField(matrix, 25, self, self.ID_NOTHING)
        tf.setText(self.rule.file)
        tf.setEditable(0)

