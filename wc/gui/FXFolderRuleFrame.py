from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.debug import *

class FXFolderRuleFrame (FXRuleFrame):
    """display all variables found in a FolderRule"""
    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Filename:\tThe name of the configuration file where these filters are stored (cannot be changed)."), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 30, self, self.ID_NOTHING)
        t.setText(self.rule.filename)
        t.setEditable(0)
