import sys
from urllib2 import urlopen, URLError

# disable proxy for urllib
import os
os.environ['http_proxy'] = ""

import wc
from wc import debug,_,error, BaseParser, ConfigDir
from wc.debug_levels import *
from wc.gui import loadIcon
from FXPy.fox import *

SCROLLING_NONE = 0
SCROLLING_AUTO = 1
SCROLLING_ALWAYS = 2

def scrollnum(s):
    if s=='auto':
        return SCROLLING_AUTO
    elif s=='none':
        return SCROLLING_NONE
    elif s=='always':
        return SCROLLING_ALWAYS
    return -1


def parse_headers():
    headers = []
    url = "http://localhost:%(port)d/headers/"%wc.config
    try:
        s = urlopen(url).read()
    except URLError:
        print >> sys.stderr, _("WebCleaner is not running")
        return headers
    if s=="-": return headers
    lines = s.split("\n")
    for l in lines:
        # strip off paranthesis
        l = l[1:-1]
        # split into three parts
        url, io, hlist = l.split(", ", 2)
        # split headers
        hlist = (hlist.strip())[2:-2].split("', '")
        # strip headers
        hlist = map(lambda x: x.replace("\\r", ""), hlist)
        hlist = map(lambda x: x.replace("\\n", ""), hlist)
        hlist = map(lambda x: x.split(":", 1), hlist)
        # append
        headers.append([url[1:-1], int(io), hlist])
    return headers


def parse_connections():
    connections = {
        'valid': 0,
        'error': 0,
        'blocked': 0,
    }
    url = "http://localhost:%d/connections/"%wc.config['port']
    try:
        s = urlopen(url).read()
    except URLError:
        print >> sys.stderr, _("WebCleaner is not running")
        return headers
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
     ID_SETREFRESH,
     ID_SETONLYFIRST,
     ID_SETSCROLLING,
     ID_STATUS,
     ID_SETSAVEDHEADERS,
     ID_SAVEOPTIONS,
     ID_ADDHEADER,
     ID_EDITHEADER,
     ID_REMOVEHEADER,
     ) = range(FXMainWindow.ID_LAST, FXMainWindow.ID_LAST+13)


    def __init__(self, app):
	FXMainWindow.__init__(self, app, "wcheaders", w=640, h=500)
        self.setIcon(loadIcon(app, 'iconbig.png'))
        self.eventMap()
        self.getApp().dirty = 0
        self.timer = None
        self.status = "Ready."
        self.read_config()
        FXTooltip(app, TOOLTIP_VARIABLE, 0, 0)
        self.statusbar = FXStatusbar(self, LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|STATUSBAR_WITH_DRAGCORNER)
        # dialogs
        self.about = FXMessageBox(self, _("About webcleaner"),wc.AppInfo, self.getIcon(),MBOX_OK)
        self.options = OptionsWindow(self)
        # main frames
        frame = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.headerFrame(frame)
        self.connectionFrame(frame)
        # Buttons
        frame = FXHorizontalFrame(frame, LAYOUT_FILL_X)
        FXButton(frame, _(" &Quit "), None, self, self.ID_QUIT)
        FXButton(frame, _(" &Refresh "), None, self, self.ID_REFRESH)
        FXButton(frame, _(" &Options "), None, self, self.ID_OPTIONS)
        FXButton(frame, _("A&bout"), None, self, self.ID_ABOUT, opts=FRAME_RAISED|FRAME_THICK|LAYOUT_RIGHT)

        self.statusbar.getStatusline().setTarget(self)
        self.statusbar.getStatusline().setSelector(self.ID_STATUS)
        # start refresh timer
        if self.config['refresh']:
            self.timer = app.addTimeout(self.config['refresh']*1000, self, HeaderWindow.ID_REFRESH)


    def connectionFrame(self, frame):
	basics = FXGroupBox(frame, _("Connections"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)


    def headerFrame(self, frame):
        headers = FXGroupBox(frame, _("Headers"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        self.headers = FXIconList(headers, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y|ICONLIST_SINGLESELECT|ICONLIST_AUTOSIZE)
        self.headers.appendHeader(_("URL"),NULL,150)
        self.headers.appendHeader(_("Name"),NULL,100)
        self.headers.appendHeader(_("Value"),NULL,200)


    def create(self):
        """create the main window and show myself on the screen"""
	FXMainWindow.create(self)
	self.show()


    def eventMap(self):
        """attach all events to (member) functions"""
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_ABOUT, HeaderWindow.onCmdAbout)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_QUIT, HeaderWindow.onCmdQuit)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_REFRESH, HeaderWindow.onCmdRefresh)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_OPTIONS, HeaderWindow.onCmdOptions)
        FXMAPFUNC(self, SEL_TIMEOUT, HeaderWindow.ID_REFRESH, HeaderWindow.onTimerRefresh)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_SETREFRESH, HeaderWindow.onSetRefresh)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_SETONLYFIRST, HeaderWindow.onSetOnlyfirst)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_SETSCROLLING, HeaderWindow.onSetScrolling)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_SETSAVEDHEADERS, HeaderWindow.onSetSavedHeaders)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_SAVEOPTIONS, HeaderWindow.onCmdSaveOptions)
        FXMAPFUNC(self, SEL_UPDATE, HeaderWindow.ID_SAVEOPTIONS, HeaderWindow.onUpdSaveOptions)
        FXMAPFUNC(self, SEL_UPDATE, HeaderWindow.ID_STATUS, HeaderWindow.onUpdStatus)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_ADDHEADER, HeaderWindow.onCmdAddHeader)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_REMOVEHEADER, HeaderWindow.onCmdRemoveHeader)
        FXMAPFUNC(self, SEL_COMMAND, HeaderWindow.ID_EDITHEADER, HeaderWindow.onCmdEditHeader)
        FXMAPFUNC(self, SEL_UPDATE, HeaderWindow.ID_EDITHEADER, HeaderWindow.onUpdHeader)
        FXMAPFUNC(self, SEL_UPDATE, HeaderWindow.ID_REMOVEHEADER, HeaderWindow.onUpdHeader)


    def onCmdAbout(self, sender, sel, ptr):
        debug(BRING_IT_ON, "About")
        self.doShow(self.about)
        return 1


    def onCmdOptions(self, sender, sel, ptr):
        debug(BRING_IT_ON, "About")
        self.doShow(self.options)
        return 1

    def onCmdAddHeader(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Add header")
        dialog = FXDialogBox(self,_("Add Header"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Header:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        header = FXTextField(matrix, 20)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            header = header.getText().strip().lower()
            if not header:
                error(_("Empty header"))
	        return 1
            if header in self.config['nodisplay']:
                error(_("Duplicate header"))
	        return 1
            self.config['nodisplay'].append(header)
            self.options.headers.appendItem(header)
            self.getApp().dirty = 1
            debug(BRING_IT_ON, "Added nodisplay header")
        return 1

    def onCmdRemoveHeader(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Remove header")
        headers = self.options.headers
        index = headers.getCurrentItem()
        item = headers.retrieveItem(index)
        header = item.getText()
        self.config['nodisplay'].remove(header)
        headers.removeItem(index)
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Removed nodisplay header")
        return 1

    def onCmdEditHeader(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Edit header")
        headers = self.options.headers
        index = headers.getCurrentItem()
        item = headers.retrieveItem(index)
        header = item.getText()
        dialog = FXDialogBox(self, _("Edit Header"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("New header:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        nametf.setText(header)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            newheader = nametf.getText().strip().lower()
            self.config['nodisplay'].remove(header)
            self.config['nodisplay'].append(item)
            headers.replaceItem(index, newheader)
            self.getApp().dirty = 1
            debug(BRING_IT_ON, "Changed nodisplay header")
        return 1

    def onUpdHeader(self, sender, sel, ptr):
        i = self.options.headers.getCurrentItem()
        if self.options.headers.isItemSelected(i):
            sender.enable()
        else:
            sender.disable()
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
            'scrolling': SCROLLING_AUTO,
            'nodisplay': [],
            'headersave': 100,
        }
        p = WHeadersParser()
        p.parse(os.path.join(ConfigDir, "wcheaders.conf"), self.config)
        debug(BRING_IT_ON, "config", self.config)


    def onCmdSaveOptions(self, sender, sel, ptr):
        self.getApp().beginWaitCursor()
        file = self.config['configfile']
        try:
            file = open(file, 'w')
            file.write(self.toxml())
            file.close()
            self.getApp().dirty = 0
        except IOError:
            error(_("cannot write to file %s") % file)
        self.getApp().endWaitCursor()


    def onUpdSaveOptions(self, sender, sel, ptr):
        if self.getApp().dirty:
            sender.enable()
        else:
            sender.disable()
        return 1


    def toxml(self):
        s = """<?xml version="1.0"?>
<!DOCTYPE wcheaders SYSTEM "wcheaders.dtd">
<wcheaders
"""
        s += ' version="%s"\n' % self.config['version'] +\
             ' refresh="%d"\n' % self.config['refresh'] +\
             ' headersave="%d"\n' % self.config['headersave']
        s += '>\n'
        for header in self.config['nodisplay']:
            s += '<nodisplay>%s</nodisplay>\n' % header
        return s + '</wcheaders>\n'


    def onCmdRefresh(self, sender, sel, ptr):
        debug(BRING_IT_ON, "Refresh")
        if self.timer:
            self.getApp().removeTimeout(self.timer)
        return self.refresh()


    def onSetRefresh(self, sender, sel, ptr):
        debug(BRING_IT_ON, "SetRefresh", sender.getValue())
        self.config['refresh'] = sender.getValue()
        self.getApp().dirty = 1
        return 1


    def onSetOnlyfirst(self, sender, sel, ptr):
        debug(BRING_IT_ON, "SetOnlyFirst", sender.getCheck())
        self.config['onlyfirst'] = sender.getCheck()
        self.getApp().dirty = 1
        return 1


    def onSetScrolling(self, sender, sel, ptr):
        debug(BRING_IT_ON, "SetScrolling", sender.getCurrentItem())
        self.config['scrolling'] = sender.getCurrentItem()
        self.getApp().dirty = 1
        return 1


    def onSetSavedHeaders(self, sender, sel, ptr):
        debug(BRING_IT_ON, "SetSavedHeaders", sender.getValue())
        self.config['headersave'] = sender.getValue()
        self.getApp().dirty = 1
        return 1


    def onUpdStatus(self, sender, sel, ptr):
        sender.setText(self.status)


    def onTimerRefresh(self, sender, sel, ptr):
        debug(BRING_IT_ON, "TimerRefresh")
        return self.refresh()


    def refresh(self):
        self.getApp().beginWaitCursor()
        try:
            self.status = "Getting headers..."
            oldhost = None
            oldio = None
            for header in parse_headers():
                url = header[0][7:]
                host = url.split("/", 1)[0]
                io = header[1]
                if host==oldhost and io==oldio and self.config['onlyfirst']:
                    continue
                oldhost = host
                oldio = io
                if io:
                    url = "<- "+url
                else:
                    url = "-> "+url
                for name, value in header[2]:
                    if name.lower() in self.config['nodisplay']:
                        continue
                    if self.headers.getNumItems() >= self.config['headersave']:
                        self.headers.removeItem(0)
                    self.headers.appendItem("%s\t%s\t%s"%(url, name, value))
                    if url:
                        url = ""
            last = self.headers.getNumItems()-1
            if last > 0 and (self.config['scrolling']==SCROLLING_ALWAYS or \
               (self.config['scrolling']==SCROLLING_AUTO and \
                self.headers.isItemVisible(last))):
                self.headers.makeItemVisible(last)
            self.status = "Getting connections..."
            connections = parse_connections()
            self.status = "Ready."
            # XXX
        except Exception, msg:
            self.status = "Error %s"%msg
            raise
        if self.config['refresh']:
            self.getApp().addTimeout(self.config['refresh']*1000, self, HeaderWindow.ID_REFRESH)
        self.getApp().endWaitCursor()
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
            for key in ('onlyfirst', 'refresh', 'headersave'):
                self.config[key] = int(self.config[key])
            for key in ('version',):
                if self.config[key] is not None:
                    self.config[key] = str(self.config[key])
            if type(self.config['scrolling']) != type(0):
                self.config['scrolling'] = scrollnum(self.config['scrolling'])


    def end_element(self, name):
        self.cmode = None


    def character_data(self, data):
        if self.cmode=='nodisplay':
            self.config['nodisplay'].append(data.lower())



class OptionsWindow(FXDialogBox):

    def __init__(self, owner):
        FXDialogBox.__init__(self, owner, "Options",DECOR_TITLE|DECOR_BORDER|DECOR_RESIZE,0,0,0,0, 4,4,4,4, 4,4)
        frame = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        # options
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        # refresh
        FXLabel(matrix, _("Refresh"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        w = FXSpinner(matrix, 4, owner, HeaderWindow.ID_SETREFRESH, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_COLUMN)
        w.setRange(0,65535)
        w.setValue(owner.config['refresh'])
        # only first
        FXLabel(matrix, _("Only first\tDisplay only the first hit in a series of headers for the same host"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        w = FXCheckButton(matrix, None, owner, HeaderWindow.ID_SETONLYFIRST, opts=ICON_BEFORE_TEXT|LAYOUT_SIDE_TOP|LAYOUT_FILL_COLUMN)
        w.setCheck(owner.config['onlyfirst'])
        # scrolling
        FXLabel(matrix, _("Scrolling"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        cols=0
        w = FXComboBox(matrix,0,3,owner, HeaderWindow.ID_SETSCROLLING,opts=COMBOBOX_INSERT_LAST|FRAME_SUNKEN|FRAME_THICK|LAYOUT_SIDE_TOP|LAYOUT_FILL_COLUMN)
        levels = [
            _("none"),
            _("auto"),
            _("always"),
        ]
        for text in levels:
            cols = max(len(text), cols)
            w.appendItem(text)
        w.setEditable(0)
        w.setNumColumns(cols)
        w.setCurrentItem(owner.config['scrolling'])
        # number of cached headers
        FXLabel(matrix, _("No. of saved Headers"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        w = FXSpinner(matrix, 4, owner, HeaderWindow.ID_SETSAVEDHEADERS, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_COLUMN)
        w.setRange(1, 65535)
        w.setValue(owner.config['headersave'])
        # display headers
        FXLabel(matrix, _("Suppress headers"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        self.headers = FXList(matrix, 4, None, 0, opts=LIST_SINGLESELECT|LAYOUT_FILL_COLUMN|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.update_headers(owner)
        # header buttons
        w = FXHorizontalFrame(frame, LAYOUT_FILL_X|PACK_UNIFORM_WIDTH)
        FXButton(w, "&Add",None,owner,HeaderWindow.ID_ADDHEADER,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK)
        FXButton(w, "&Edit",None,owner,HeaderWindow.ID_EDITHEADER,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK)
        FXButton(w, "&Remove",None,owner,HeaderWindow.ID_REMOVEHEADER,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK)

        # close button
        w = FXHorizontalFrame(frame,LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|PACK_UNIFORM_WIDTH)
        FXButton(w,"&Save",None,owner,HeaderWindow.ID_SAVEOPTIONS,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK,0,0,0,0, 20,20,5,5)
        FXButton(w,"&Close",None,self,FXDialogBox.ID_CANCEL,LAYOUT_RIGHT|FRAME_RAISED|FRAME_THICK,0,0,0,0, 20,20,5,5)

    def update_headers(self, owner):
        self.headers.clearItems()
        for h in owner.config['nodisplay']:
            self.headers.appendItem(str(h))


if __name__=='__main__':
    parse_headers()
