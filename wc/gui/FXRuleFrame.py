from FXPy.fox import *
from wc import _,debug,error
from wc.debug_levels import *

class FXRuleFrame (FXVerticalFrame):
    """display all variables found in a basic Rule.
    This means basically we have a FOX widget for each variable
    found in the rule (e.g. for rule.title we have an FXTextField).
    """
    (ID_TITLE,
     ID_DESC,
     ID_DISABLE_RULE,
     ID_MATCHURL,
     ID_DONTMATCHURL,
     ID_NOTHING,
     ID_LAST,
    ) = range(FXVerticalFrame.ID_LAST, FXVerticalFrame.ID_LAST+7)

    def __init__ (self, parent, rule, index):
        FXVerticalFrame.__init__(self, parent, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        # event map
        FXMAPFUNC(self,SEL_COMMAND, FXRuleFrame.ID_TITLE, FXRuleFrame.onCmdTitle)
        FXMAPFUNC(self,SEL_CHANGED, FXRuleFrame.ID_DESC, FXRuleFrame.onCmdDesc)
        FXMAPFUNC(self,SEL_COMMAND, FXRuleFrame.ID_DISABLE_RULE, FXRuleFrame.onCmdDisableRule)
        FXMAPFUNC(self,SEL_CHANGED, FXRuleFrame.ID_NOTHING, FXRuleFrame.onCmdNone)
        FXMAPFUNC(self,SEL_COMMAND, FXRuleFrame.ID_NOTHING, FXRuleFrame.onCmdNone)
        self.rule = rule
        # augment the rule information with the (unique) index
        self.rule.index = index
        f = FXHorizontalFrame(self, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
        FXLabel(f, self.get_name(), opts=LAYOUT_CENTER_X|LAYOUT_TOP|LAYOUT_FILL_X)
        FXCheckButton(f, _("disable"), self, FXRuleFrame.ID_DISABLE_RULE,ICON_AFTER_TEXT|LAYOUT_RIGHT|LAYOUT_CENTER_Y|LAYOUT_FILL_X).setCheck(self.rule.disable)
        f = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(f, _("Title")+":", opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXTextField(f, 25, self, FXRuleFrame.ID_TITLE).setText(self.rule.title)
        if hasattr(self.rule, "matchurl"):
            # some rules can have url matchers
            FXLabel(f, _("Match url")+":", opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
            FXTextField(f, 25, self, FXRuleFrame.ID_MATCHURL).setText(self.rule.matchurl)
            FXMAPFUNC(self,SEL_COMMAND, FXRuleFrame.ID_MATCHURL, FXRuleFrame.onCmdMatchUrl)
            FXLabel(f, _("Dont match url")+":", opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
            FXTextField(f, 25, self, FXRuleFrame.ID_DONTMATCHURL).setText(self.rule.dontmatchurl)
            FXMAPFUNC(self,SEL_COMMAND, FXRuleFrame.ID_DONTMATCHURL, FXRuleFrame.onCmdDontMatchUrl)
        FXLabel(self, _("Description")+":")
        f = FXVerticalFrame(self, FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X|LAYOUT_FILL_Y, 0,0,0,0, 0,0,0,0, 0,0)
        t = FXText(f, self, FXRuleFrame.ID_DESC, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y|TEXT_WORDWRAP)
        t.setText(self.rule.desc)
        t.setEditable()

    def get_name (self):
        """display this name at the top of the window"""
        s = self.rule.get_name().capitalize()+_(" rule")
        s += " (ID %d)" % self.rule.oid
        return s

    def onCmdTitle (self, sender, sel, ptr):
        title = sender.getText().strip()
        if not title:
            error(_("empty title"))
            sender.setText(self.rule.title)
            return 1
        sender.setText(title)
        self.rule.title = title
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Rule title changed")
        # send message to main window for treelist updating
        win = self.getApp().getMainWindow()
        win.handle(sender, MKUINT(win.ID_TITLE, SEL_COMMAND), ptr)
        return 1

    def onCmdDesc (self, sender, sel, ptr):
        if self.rule.desc != sender.getText():
            self.rule.desc = sender.getText()
            self.getApp().dirty = 1
            debug(BRING_IT_ON, "Rule description changed")
        return 1

    def onCmdDisableRule (self, sender, sel, ptr):
        debug(BRING_IT_ON, "Rule %d %s"%(self.rule.index, (self.rule.disable and "disabled" or "enabled")))
        self.rule.disable = sender.getCheck()
        self.getApp().dirty = 1
        # send message to main window for icon updating
        win = self.getApp().getMainWindow()
        win.handle(sender, MKUINT(win.ID_DISABLERULE,SEL_COMMAND), ptr)
        return 1

    def onCmdMatchUrl (self, sender, sel, ptr):
        if self.rule.matchurl != sender.getText():
            self.rule.matchurl = sender.getText()
            self.getApp().dirty = 1
            debug(BRING_IT_ON, "Rule matchurl changed")
        return 1

    def onCmdDontMatchUrl (self, sender, sel, ptr):
        if self.rule.dontmatchurl != sender.getText():
            self.rule.dontmatchurl = sender.getText()
            self.getApp().dirty = 1
            debug(BRING_IT_ON, "Rule dontmatchurl changed")
        return 1

    def onCmdNone (self, sender, sel, ptr):
        return 1
