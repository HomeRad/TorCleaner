from FXPy.fox import *
import sys

class ToolApp (FXApp):
    """common base class for webcleaner tool applications"""
    def __init__ (self, name):
        FXApp.__init__(self, name, "TheDude")
        # set default color scheme
        self.reg().writeColorEntry("SETTINGS","basecolor",FXRGB(141,157,170))
        self.reg().writeColorEntry("SETTINGS","backcolor",FXRGB(211,223,232))
        self.reg().writeColorEntry("SETTINGS","hilitecolor",FXRGB(226,225,220))
        self.reg().writeColorEntry("SETTINGS","shadowcolor",FXRGB(158,165,191))
        self.reg().writeColorEntry("SETTINGS","bordercolor",FXRGB(86,90,104))
        self.reg().writeColorEntry("SETTINGS","selbackcolor",FXRGB(20,58,84))
        self.init(sys.argv)
        # dirty flag for the apply button
        self.dirty = 0

    def error (self, title, msg):
        """display a message box with the error message"""
        dialog = FXMessageBox(self.getRoot(), title, msg, None, MBOX_OK)
        return self.doShow(dialog)

    def doShow (self, win):
        """show a modal dialog"""
        return win.execute(PLACEMENT_OWNER)
