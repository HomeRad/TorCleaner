import wc,os
from wc import debug,_,error
from wc.debug_levels import *
from wc.gui import loadIcon
from FXPy.fox import *

class HeaderWindow(FXMainWindow):
    """The main window holds all data and windows to display"""
    (ID_ACCEPT,
     ID_CANCEL,
     ) = range(FXMainWindow.ID_LAST, FXMainWindow.ID_LAST+2)


    def __init__(self, app):
	FXMainWindow.__init__(self, app, "wcheaders", w=640, h=500)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.eventMap()
        FXTooltip(app, TOOLTIP_VARIABLE, 0, 0)
        FXStatusbar(self, LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|STATUSBAR_WITH_DRAGCORNER)


    def create(self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()


    def eventMap(self):
        """attach all events to (member) functions"""
        FXMAPFUNC(self,SEL_COMMAND,HeaderWindow.ID_ACCEPT,HeaderWindow.onCmdAccept)
        FXMAPFUNC(self,SEL_COMMAND,HeaderWindow.ID_CANCEL,HeaderWindow.onCmdCancel)


    def onCmdAccept(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Accept")
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1


    def onCmdCancel(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Cancel")
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1

