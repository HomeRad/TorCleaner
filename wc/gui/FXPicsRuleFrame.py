from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.debug import *
from wc.filter.PICS import services

class FXPicsRuleFrame (FXRuleFrame):
    """display all variables found in a PicsRule"""
    (ID_URL,
     ID_SERVICE,
     ID_CATEGORY,
     ID_CATEGORY_VALUE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+4)

    def __init__ (self, parent, rule, index):
        """initialize pics rule display frame"""
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXPicsRuleFrame.ID_URL,FXPicsRuleFrame.onCmdUrl)
        FXMAPFUNC(self,SEL_COMMAND,FXPicsRuleFrame.ID_SERVICE,FXPicsRuleFrame.onCmdService)
        FXMAPFUNC(self,SEL_COMMAND,FXPicsRuleFrame.ID_CATEGORY,FXPicsRuleFrame.onCmdCategory)
	g = FXGroupBox(self, i18n._("PICS services"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        fv = FXVerticalFrame(g, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
        fh = FXHorizontalFrame(fv, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
        FXLabel(fh, i18n._("Fallback URL:\tA URL to display if the page is censored\nThe default is to return a 403 Forbidden HTTP error."), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        FXTextField(fh, 25, self, FXPicsRuleFrame.ID_URL).setText(self.rule.url)
        scroll = FXScrollWindow(self, LAYOUT_FILL_X|LAYOUT_FILL_Y|LAYOUT_LEFT|LAYOUT_TOP|SCROLLERS_TRACK, 0,0,0,0)
        fv = FXVerticalFrame(scroll, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
        # store checkbox groups in local config
        self.widgets = {}
        # store rating values in local config
        # draw lots of checkboxes
        for service, sdata in services.items():
            self.widgets[service] = {}
            c = FXCheckButton(fv, i18n._("%s\tEnable/disable this rating service.")%sdata['name'], self, FXPicsRuleFrame.ID_SERVICE,ICON_BEFORE_TEXT|LAYOUT_LEFT|LAYOUT_TOP)
            c.setCheck(self.rule.ratings.has_key(service))
            c.setHelpText(service)
            # categories
            for category in sdata['categories'].keys():
                fh = FXHorizontalFrame(fv, LAYOUT_FILL_X|LAYOUT_LEFT|LAYOUT_TOP, 0,0,0,0, 0,0,0,0, 0,0)
                c = FXCheckButton(fh, i18n._("%s\tEnable/disable this category.")%category, self, FXPicsRuleFrame.ID_CATEGORY,ICON_BEFORE_TEXT|LAYOUT_LEFT|LAYOUT_TOP)
                c.setHelpText("%s %s" % (service, category))
                c.setPadLeft(20)
                #v = FXSpinner(fh, 3, self, FXPicsRuleFrame.ID_CATEGORY_VALUE, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_COLUMN)
                #v.setRange(0,100)
                #v.setValue(0)
                self.widgets[service][category] = c #(c,v)
                if not self.rule.ratings.has_key(service):
                    c.disable()
                elif self.rule.ratings[service].has_key(category):
                    c.setCheck(1)
                    #val =  self.rule.ratings[service][category]
                    #v.setValue(int(val))


    def onCmdUrl (self, sender, sel, ptr):
        """change the url param"""
        # XXX url syntax check ???
        self.rule.url = sender.getText().strip()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule pics url")
        return 1


    def onCmdService (self, sender, sel, ptr):
        """enable/disable a PICS service"""
        service = sender.getHelpText()
        widgets = self.widgets[service].values()
        # enable this service
        if sender.getCheck():
            # rule update
            self.rule.ratings[service] = {}
            for c in widgets:
                # gui update
                c.enable()
        # disable this service
        else:
            # rule update
            del self.rule.ratings[service]
            # gui update
            for c in widgets:
                c.setCheck(0)
                #v.setValue(0)
                c.disable()
                #v.disable()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule pics service data")
        return 1


    def onCmdCategory (self, sender, sel, ptr):
        """enable/disable a PICS service rating"""
        service, cat = sender.getHelpText().split()
        if sender.getCheck():
            self.rule.ratings[service][cat] = 1
        else:
            del self.rule.ratings[service][cat]
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule pics category data")
        return 1

