if __name__=='__main__':
    import sys
    sys.path.insert(0, ".")

import wc,os
from wc import debug,_,error
from wc.debug_levels import *
from wc.gui import loadIcon
from FXPy.fox import *
os.environ['http_proxy'] = ""

def parse_headers():
    url = "http://localhost:%d/headers/"%wc.config['port']
    from urllib2 import urlopen
    s = urlopen(url).read()
    headers = []
    if s=="-": return headers
    strheaders = s.split("\n")
    for h in strheaders:
        # strip off paranthesis
        h = h[1:-1]
        # split into three parts
        url, io, hlist = h.split(",", 2)
        # split headers
        hlist = hlist.strip()[1:-1].split("', '")
        # strip headers
        hlist = map(lambda x: x.replace("\\r", ""), hlist)
        hlist = map(lambda x: x.replace("\\n", ""), hlist)
        # append
        headers.append((url[1:-1], int(io), hlist))
    return headers


class HeaderWindow(FXMainWindow):
    """The main window holds all data and windows to display"""
    (ID_ABOUT,
     ID_QUIT,
     ID_REFRESH,
     ) = range(FXMainWindow.ID_LAST, FXMainWindow.ID_LAST+3)


    def __init__(self, app):
	FXMainWindow.__init__(self, app, "wcheaders", w=640, h=500)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.eventMap()
        FXTooltip(app, TOOLTIP_VARIABLE, 0, 0)
        FXStatusbar(self, LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|STATUSBAR_WITH_DRAGCORNER)
        # dialogs
        self.about = FXMessageBox(self, _("About webcleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)
        # main frames
        frame = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.connectionFrame(frame)
        self.headerFrame(frame)
        # Buttons
        frame = FXHorizontalFrame(frame, LAYOUT_FILL_X)
        FXButton(frame, _(" &Quit "), None, self, self.ID_QUIT)
        FXButton(frame, _(" &Refresh "), None, self, self.ID_REFRESH)
        FXButton(frame, _("A&bout"), None, self, self.ID_ABOUT, opts=FRAME_RAISED|FRAME_THICK|LAYOUT_RIGHT)


    def connectionFrame(self, frame):
	basics = FXGroupBox(frame, _("Connections"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)


    def headerFrame(self, frame):
        headers = FXGroupBox(frame, _("Headers"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)


    def create(self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()


    def eventMap(self):
        """attach all events to (member) functions"""
        FXMAPFUNC(self,SEL_COMMAND,HeaderWindow.ID_ABOUT,HeaderWindow.onCmdAbout)
        FXMAPFUNC(self,SEL_COMMAND,HeaderWindow.ID_QUIT,HeaderWindow.onCmdQuit)
        FXMAPFUNC(self,SEL_COMMAND,HeaderWindow.ID_REFRESH,HeaderWindow.onCmdRefresh)


    def onCmdAbout(self, sender, sel, ptr):
        debug(BRING_IT_ON, "About")
        self.doShow(self.about)
        return 1


    def onCmdQuit(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Accept")
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1


    def onCmdRefresh(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Refresh")
        headers = parse_headers()
        return 1


    def doShow(self, win):
        return win.execute(PLACEMENT_OWNER)

if __name__=='__main__':
    for h in parse_headers():
        print h
