from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug
from wc.debug_levels import *

def _lang_num (lang):
    """a little helper function for an FXComboBox"""
    if lang=="Perl": return 1
    if lang=="Python": return 2
    return 0

def _num_lang (num):
    """another little helper function for an FXComboBox"""
    if num==1: return "Perl"
    if num==2: return "Python"
    return None


class FXFolderRuleFrame (FXRuleFrame):
    """display all variables found in a FolderRule"""
    (ID_LANG,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+1)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXFolderRuleFrame.ID_LANG,FXFolderRuleFrame.onCmdLang)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Filename")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 22, self, self.ID_NOTHING)
        t.setText(self.rule.filename)
        t.setEditable(0)
        FXLabel(matrix, _("Language")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXComboBox(matrix,5,3,self, self.ID_LANG,opts=COMBOBOX_INSERT_LAST|FRAME_SUNKEN|FRAME_THICK|LAYOUT_SIDE_TOP)
        t.appendItem("All")
        t.appendItem("Perl")
        t.appendItem("Python")
        t.setEditable(0)
        t.setCurrentItem(_lang_num(self.rule.lang))

    def onCmdLang (self, sender, sel, ptr):
        self.rule.lang = _num_lang(sender.getCurrentItem())
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Changed rule language")
        return 1

