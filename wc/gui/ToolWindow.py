from FXPy.fox import *
from wc.gui import loadIcon
from wc import i18n

class ToolWindow (FXMainWindow):
    """common base class for webcleaner tool windows"""
    def __init__ (self, app, name):
	FXMainWindow.__init__(self, app, name)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.about = FXMessageBox(self, i18n._("About WebCleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)

    def create (self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()

