from FXPy.fox import *
import wc
from wc.gui import loadIcon
from wc import _

class ToolWindow (FXMainWindow):
    """common base class for webcleaner tool windows"""
    def __init__ (self, app, name):
	FXMainWindow.__init__(self, app, name)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.about = FXMessageBox(self, _("About webcleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)

    def create (self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()

