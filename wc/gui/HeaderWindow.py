if __name__=='__main__':
    import sys
    sys.path.insert(0, ".")

import wc,os
from wc import debug,_,error, BaseParser, ConfigDir
from wc.debug_levels import *
from wc.gui import loadIcon
from FXPy.fox import *
os.environ['http_proxy'] = ""
wc.DebugLevel = 1

def parse_headers():
    headers = []
    url = "http://localhost:%d/headers/"%wc.config['port']
    from urllib2 import urlopen
    s = urlopen(url).read()
    if s=="-": return headers
    lines = s.split("\n")
    for l in lines:
        # strip off paranthesis
        l = l[1:-1]
        # split into three parts
        url, io, hlist = l.split(",", 2)
        # split headers
        hlist = hlist.strip()[1:-1].split("', '")
        # strip headers
        hlist = map(lambda x: x.replace("\\r", ""), hlist)
        hlist = map(lambda x: x.replace("\\n", ""), hlist)
        # append
        headers.append((url[1:-1], int(io), hlist))
    return headers


def parse_connections():
    connections = {
        'valid': 0,
        'error': 0,
        'blocked': 0,
    }
    url = "http://localhost:%d/connections/"%wc.config['port']
    from urllib2 import urlopen
    s = urlopen(url).read()
    lines = s.split("\n")
    for l in lines:
        name, num = l.split(":")
        connections[name] = int(num)
    return connections


class HeaderWindow(FXMainWindow):
    """The main window holds all data and windows to display"""
    (ID_ABOUT,
     ID_QUIT,
     ID_REFRESH,
     ID_OPTIONS,
     ) = range(FXMainWindow.ID_LAST, FXMainWindow.ID_LAST+4)


    def __init__(self, app):
	FXMainWindow.__init__(self, app, "wcheaders", w=640, h=500)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.eventMap()
        self.timer = None
        self.read_config()
        FXTooltip(app, TOOLTIP_VARIABLE, 0, 0)
        FXStatusbar(self, LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|STATUSBAR_WITH_DRAGCORNER)
        # dialogs
        self.about = FXMessageBox(self, _("About webcleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)
        self.options = OptionsWindow(self)
        # main frames
        frame = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.connectionFrame(frame)
        self.headerFrame(frame)
        # Buttons
        frame = FXHorizontalFrame(frame, LAYOUT_FILL_X)
        FXButton(frame, _(" &Quit "), None, self, self.ID_QUIT)
        FXButton(frame, _(" &Refresh "), None, self, self.ID_REFRESH)
        FXButton(frame, _(" &Options "), None, self, self.ID_OPTIONS)
        FXButton(frame, _("A&bout"), None, self, self.ID_ABOUT, opts=FRAME_RAISED|FRAME_THICK|LAYOUT_RIGHT)
        # start refresh timer
        self.timer = app.addTimeout(self.config['refresh']*1000, self, HeaderWindow.ID_REFRESH)


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
        FXMAPFUNC(self,SEL_COMMAND, HeaderWindow.ID_ABOUT, HeaderWindow.onCmdAbout)
        FXMAPFUNC(self,SEL_COMMAND, HeaderWindow.ID_QUIT, HeaderWindow.onCmdQuit)
        FXMAPFUNC(self,SEL_COMMAND, HeaderWindow.ID_REFRESH, HeaderWindow.onCmdRefresh)
        FXMAPFUNC(self,SEL_COMMAND, HeaderWindow.ID_OPTIONS, HeaderWindow.onCmdOptions)
        FXMAPFUNC(self,SEL_TIMEOUT, HeaderWindow.ID_REFRESH, HeaderWindow.onTimerRefresh)


    def onCmdAbout(self, sender, sel, ptr):
        debug(BRING_IT_ON, "About")
        self.doShow(self.about)
        return 1


    def onCmdOptions(self, sender, sel, ptr):
        debug(BRING_IT_ON, "About")
        self.doShow(self.options)
        return 1


    def onCmdQuit(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Quit")
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1


    def read_config(self):
        self.config = {
            'version': '0.1',
            'onlyfirst': 1,
            'refresh': 5,
            'scrolling': 'auto',
            'nodisplay': [],
        }
        p = WHeadersParser()
        p.parse(os.path.join(ConfigDir, "wcheaders.conf"), self.config)
        debug(BRING_IT_ON, "config", self.config)


    def onCmdRefresh(self, sender, sel, ptr):
        if self.timer:
            self.getApp().removeTimeout(self.timer)
        self.refresh()
        self.getApp().addTimeout(self.config['refresh']*1000, self, HeaderWindow.ID_REFRESH)


    def onTimerRefresh(self, sender, sel, ptr):
        self.refresh()
        self.timer = self.getApp().addTimeout(self.config['refresh']*1000, self, HeaderWindow.ID_REFRESH)



    def refresh(self):
        debug(BRING_IT_ON, "Refresh")
        headers = parse_headers()
        connections = parse_connections()
        # XXX
        #sender->handle(this,MKUINT(ID_SETSTRINGVALUE,SEL_COMMAND),(void*)&info);
        return 1


    def doShow(self, win):
        return win.execute(PLACEMENT_OWNER)



class WHeadersParser(BaseParser):
    def parse(self, filename, config):
        BaseParser.parse(self, filename, config)
        self.config['configfile'] = filename


    def start_element(self, name, attrs):
        self.cmode = name
        if name=='wcheaders':
            for key,val in attrs.items():
                self.config[str(key)] = val
            for key in ('onlyfirst', 'refresh'):
                self.config[key] = int(self.config[key])
            for key in ('version', 'scrolling'):
                if self.config[key] is not None:
                    self.config[key] = str(self.config[key])


    def end_element(self, name):
        self.cmode = None


    def character_data(self, data):
        if self.cmode:
            self.config['nodisplay'].append(data.lower())



class OptionsWindow(FXDialogBox):

    def __init__(self, owner):
        FXDialogBox.__init__(self, owner, "Options",DECOR_TITLE|DECOR_BORDER|DECOR_RESIZE,0,0,0,0, 4,4,4,4, 4,4)
        close = FXHorizontalFrame(self,LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|PACK_UNIFORM_WIDTH)
        FXButton(close,"&Close",None,self,FXDialogBox.ID_CANCEL,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK,0,0,0,0, 20,20,5,5);


if __name__=='__main__':
    for h in parse_headers():
        print h
