from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.debug import *
from wc.filter.PICS import services

class FXPicsRuleFrame (FXRuleFrame):
    """display all variables found in a PicsRule"""
    (ID_SERVICE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+1)

    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        #FXMAPFUNC(self,SEL_COMMAND,FXHeaderRuleFrame.ID_VALUE,FXHeaderRuleFrame.onCmdValue)
	g = FXGroupBox(self, i18n._("PICS services"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        fv = FXVerticalFrame(g, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
        for service, sdata in services.items():
            FXCheckButton(fv, i18n._("%s\tDisable this rating service.")%sdata['name'], self, FXRuleFrame.ID_DISABLE_RULE,ICON_AFTER_TEXT|LAYOUT_RIGHT|LAYOUT_CENTER_Y|LAYOUT_FILL_X).setCheck(self.rule.ratings.has_key(service))

