from FXPy.fox import *
import wc
from wc.gui import loadIcon
from wc import _

class ToolWindow(FXMainWindow):
    """common base class for webcleaner tools"""
    def __init__ (self, app, name):
	FXMainWindow.__init__(self, app, name)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.eventMap()
        self.about = FXMessageBox(self, _("About webcleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)

    def error (self, title, msg):
        """display a message box with the error message"""
        dialog = FXMessageBox(self, title, msg, None, MBOX_OK)
        self.doShow(dialog)

    def create (self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()

    def doShow (self, win):
        return win.execute(PLACEMENT_OWNER)

    def eventMap (self):
        raise Exception, "subclass responsibility"
