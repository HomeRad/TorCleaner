import wc,os
from FXRuleTreeList import FXRuleTreeList
from FXRuleFrameFactory import FXRuleFrameFactory
from FXFolderRuleFrame import FXFolderRuleFrame
from wc import debug,_
from wc.gui import HelpText
from FXPy.fox import *
from types import IntType
from wc.filter.Rules import FolderRule
from wc.filter import GetRuleFromName
from wc.debug_levels import *
from ToolWindow import ToolWindow

UpdateHelp = \
_("Updating procedure:\n\n"
"We download the new configuration files from\n"
"'%s'.\n"
"Changed config files are renamed to .old files, new\n"
"files are copied into the config directory.\n"
"\n"
"If something has changed, we restart the proxy.")


RemoveText = \
_("You cannot remove folders. If you really want to get rid\n"
"of this folder, delete the appropriate configuration file.\n"
"It is always safer to disable a folder or filter instead of\n"
"deleting it!")


import tempfile
# set the directory for new files
tempfile.tempdir = wc.ConfigDir


class ConfWindow(ToolWindow):
    """The main window holds all data and windows to display"""
    (ID_PORT,
     ID_PROXYUSER,
     ID_PROXYPASS,
     ID_DEBUGLEVEL,
     ID_FILTERMODULE,
     ID_PARENTPROXY,
     ID_PARENTPROXYUSER,
     ID_PARENTPROXYPASS,
     ID_PARENTPROXYPORT,
     ID_ACCEPT,
     ID_CANCEL,
     ID_APPLY,
     ID_TIMEOUT,
     ID_OBFUSCATEIP,
     ID_SHOWERRORS,
     ID_LOGFILE,
     ID_ABOUT,
     ID_HELP,
     ID_TITLE,
     ID_FILTER,
     ID_NEWFOLDER,
     ID_NEWRULE,
     ID_REMOVE,
     ID_CONFUPDATE,
     ID_PROXYSTART,
     ID_PROXYSTOP,
     ID_PROXYRESTART,
     ID_PROXYRELOAD,
     ID_PROXYSTATUS,
     ID_DISABLERULE,
     ID_NOPROXYFOR_ADD,
     ID_NOPROXYFOR_EDIT,
     ID_NOPROXYFOR_REMOVE,
     ID_UP,
     ID_DOWN,
     ) = range(ToolWindow.ID_LAST, ToolWindow.ID_LAST+35)


    def __init__(self, app):
	ToolWindow.__init__(self, app, "webcleanerconf")
        self.readconfig()
        self.eventMap()
        FXTooltip(app, TOOLTIP_VARIABLE, 0, 0)
        FXStatusbar(self, LAYOUT_SIDE_BOTTOM|LAYOUT_FILL_X|STATUSBAR_WITH_DRAGCORNER)
        self.help = FXDialogBox(self, _("webcleanerconf Help"))
        w = FXVerticalFrame(self.help)
        t = FXText(w, opts=TEXT_READONLY|TEXT_WORDWRAP)
        t.setVisCols(60)
        t.setVisRows(40)
        t.setText(HelpText)
        FXButton(w, _(" &Ok "), None, self.help, FXDialogBox.ID_ACCEPT)

        self.removeDialog = FXMessageBox(self, _("Remove Folder"), RemoveText, None, MBOX_OK)
        # main frame
        mainframe = FXVerticalFrame(self, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        tabbook = FXTabBook(mainframe, None, 0, LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.proxySettings(tabbook)
        self.filterSettings(tabbook)
        # Buttons
        frame = FXHorizontalFrame(mainframe, LAYOUT_FILL_X)
        FXButton(frame, _(" &Ok "), None, self, self.ID_ACCEPT)
        FXButton(frame, _("&Cancel"), None, self, self.ID_CANCEL)
        FXButton(frame, _("A&pply"), None, self, self.ID_APPLY)
        FXButton(frame, _("A&bout"), None, self, self.ID_ABOUT, opts=FRAME_RAISED|FRAME_THICK|LAYOUT_RIGHT)
        FXButton(frame, _("&Help"), None, self, self.ID_HELP, opts=FRAME_RAISED|FRAME_THICK|LAYOUT_RIGHT)
        daemonmenu = FXMenuPane(self)
        FXMenuCommand(daemonmenu, "Start", None, self, self.ID_PROXYSTART)
        FXMenuCommand(daemonmenu, "Stop", None, self, self.ID_PROXYSTOP)
        FXMenuCommand(daemonmenu, "Restart", None, self, self.ID_PROXYRESTART)
        FXMenuCommand(daemonmenu, "Reload", None, self, self.ID_PROXYRELOAD)
        FXMenuCommand(daemonmenu, "Status", None, self, self.ID_PROXYSTATUS)
        FXMenuButton(frame, "Proxy", None, daemonmenu, MENUBUTTON_ATTACH_BOTH|MENUBUTTON_DOWN|JUSTIFY_HZ_APART|LAYOUT_TOP|FRAME_RAISED|FRAME_THICK|ICON_AFTER_TEXT)
        FXButton(frame, "Update...", None, self, self.ID_CONFUPDATE)


    def eventMap(self):
        """attach all events to (member) functions"""
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_ACCEPT,ConfWindow.onCmdAccept)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_CANCEL,ConfWindow.onCmdCancel)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_APPLY,ConfWindow.onCmdApply)
        FXMAPFUNC(self,SEL_UPDATE,ConfWindow.ID_APPLY,ConfWindow.onUpdApply)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_ABOUT,ConfWindow.onCmdAbout)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_TIMEOUT,ConfWindow.onCmdTimeout)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_OBFUSCATEIP,ConfWindow.onCmdObfuscateIp)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_SHOWERRORS,ConfWindow.onCmdShowErrors)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PORT,ConfWindow.onCmdPort)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_DEBUGLEVEL,ConfWindow.onCmdDebuglevel)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PARENTPROXY,ConfWindow.onCmdParentProxy)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PARENTPROXYPORT,ConfWindow.onCmdParentProxyPort)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_LOGFILE,ConfWindow.onCmdLogfile)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_FILTERMODULE,ConfWindow.onCmdFilterModule)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_FILTER,ConfWindow.onCmdFilter)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_HELP,ConfWindow.onCmdHelp)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_NEWFOLDER,ConfWindow.onCmdNewFolder)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_NEWRULE,ConfWindow.onCmdNewRule)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_REMOVE,ConfWindow.onCmdRemove)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_TITLE,ConfWindow.onCmdTitle)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PROXYSTART,ConfWindow.onCmdProxyStart)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PROXYSTOP,ConfWindow.onCmdProxyStop)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PROXYRESTART,ConfWindow.onCmdProxyRestart)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PROXYRELOAD,ConfWindow.onCmdProxyReload)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_PROXYSTATUS,ConfWindow.onCmdProxyStatus)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_CONFUPDATE,ConfWindow.onCmdConfUpdate)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_DISABLERULE,ConfWindow.onCmdDisableRule)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_NOPROXYFOR_ADD,ConfWindow.onCmdNoProxyForAdd)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_NOPROXYFOR_EDIT,ConfWindow.onCmdNoProxyForEdit)
        FXMAPFUNC(self,SEL_UPDATE, ConfWindow.ID_NOPROXYFOR_EDIT,ConfWindow.onUpdNoProxy)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_NOPROXYFOR_REMOVE,ConfWindow.onCmdNoProxyForRemove)
        FXMAPFUNC(self,SEL_UPDATE, ConfWindow.ID_NOPROXYFOR_REMOVE,ConfWindow.onUpdNoProxy)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_UP,ConfWindow.onCmdUp)
        FXMAPFUNC(self,SEL_COMMAND,ConfWindow.ID_DOWN,ConfWindow.onCmdDown)
        FXMAPFUNC(self,SEL_UPDATE,ConfWindow.ID_UP,ConfWindow.onCmdUpUpdate)
        FXMAPFUNC(self,SEL_UPDATE,ConfWindow.ID_DOWN,ConfWindow.onCmdDownUpdate)


    def proxySettings(self, tabbook):
        """generate the proxy setting tab"""
        FXTabItem(tabbook, _("P&roxy Settings"), None)
        proxy = FXVerticalFrame(tabbook, FRAME_THICK|FRAME_RAISED)
        proxy_top = FXHorizontalFrame(proxy, LAYOUT_FILL_X|LAYOUT_FILL_Y|LAYOUT_SIDE_TOP)

	basics = FXGroupBox(proxy_top, _("Basic Values"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        matrix = FXMatrix(basics, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Version"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXLabel(matrix, wc.Version, opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        FXLabel(matrix, _("User"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXTextField(matrix, 10, self, self.ID_PROXYUSER).setText(self.proxyuser)
        FXLabel(matrix, _("Password"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXTextField(matrix, 10, self, self.ID_PROXYPASS, opts=TEXTFIELD_PASSWD|TEXTFIELD_NORMAL).setText(self.proxypass)
        FXLabel(matrix, _("Port"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        widget = FXSpinner(matrix, 4, self, self.ID_PORT, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        widget.setRange(0,65535)
        widget.setValue(self.port)
        FXLabel(matrix, _("Logfile"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXTextField(matrix, 10, self, self.ID_LOGFILE).setText(self.logfile)
        FXLabel(matrix, _("Log HTML errors"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXCheckButton(matrix, None, self, self.ID_SHOWERRORS, opts=ICON_BEFORE_TEXT|LAYOUT_SIDE_TOP).setCheck(self.showerrors)
        FXLabel(matrix, _("Timeout (sec.)"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        widget = FXSpinner(matrix, 3, self, self.ID_TIMEOUT, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        widget.setRange(1,600)
        widget.setValue(self.timeout)
        FXLabel(matrix, _("Obfuscate IP"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        FXCheckButton(matrix, None, self, self.ID_OBFUSCATEIP, opts=ICON_BEFORE_TEXT|LAYOUT_SIDE_TOP).setCheck(self.obfuscateip)
        FXLabel(matrix, _("Debug level"), opts=LAYOUT_CENTER_Y|LAYOUT_RIGHT)
        cols=0
        d = FXComboBox(matrix,0,4,self, self.ID_DEBUGLEVEL,opts=COMBOBOX_INSERT_LAST|FRAME_SUNKEN|FRAME_THICK|LAYOUT_SIDE_TOP)
        levels = [
            _("No debugging"),
            _("Bring it on"),
            _("Hurt me plenty"),
            _("Nightmare"),
        ]
        for text in levels:
            cols = max(len(text), cols)
            d.appendItem(text)
        d.setEditable(0)
        d.setNumColumns(cols)
        d.setCurrentItem(self.debuglevel)

        f = FXGroupBox(proxy_top, _("No proxy for"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        f = FXVerticalFrame(f, LAYOUT_SIDE_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.noproxylist = FXList(f, 4, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y|LIST_SINGLESELECT)
        for host in self.noproxyfor.keys():
            self.noproxylist.appendItem(host)
        f = FXHorizontalFrame(f, LAYOUT_SIDE_TOP)
        FXButton(f, _("Add"), None, self, ConfWindow.ID_NOPROXYFOR_ADD)
        FXButton(f, _("Edit"), None, self, ConfWindow.ID_NOPROXYFOR_EDIT)
        FXButton(f, _("Remove"), None, self, ConfWindow.ID_NOPROXYFOR_REMOVE)

        frame = FXHorizontalFrame(proxy, LAYOUT_FILL_X|LAYOUT_FILL_Y|LAYOUT_SIDE_TOP)
        filters = FXGroupBox(frame, _("Filter Modules"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        hframe = FXVerticalFrame(filters, LAYOUT_SIDE_TOP)
        for m in self.modules.keys():
            cb = FXCheckButton(hframe, m, self, self.ID_FILTERMODULE,opts=ICON_BEFORE_TEXT|LAYOUT_SIDE_TOP)
            if self.modules[m]:
	        cb.setCheck()
        groupbox = FXGroupBox(frame, _("Parent Proxy"), FRAME_RIDGE|LAYOUT_LEFT|LAYOUT_TOP|LAYOUT_FILL_X|LAYOUT_FILL_Y,0,0,0,0,5,5,5,5)
        matrix = FXMatrix(groupbox, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Host"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        parentproxy = FXTextField(matrix, 16, self, self.ID_PARENTPROXY)
        parentproxy.setText(self.parentproxy)
        FXLabel(matrix, _("Port"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        parentport = FXSpinner(matrix, 4, self, self.ID_PARENTPROXYPORT, SPIN_NORMAL|FRAME_SUNKEN|FRAME_THICK)
        parentport.setRange(0,65535)
        parentport.setValue(self.parentproxyport)
        # proxySettings


    def filterSettings(self, tabbook):
        FXTabItem(tabbook, _("&Filter Settings"), None)
        frame = FXHorizontalFrame(tabbook, FRAME_THICK|FRAME_RAISED|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        splitter = FXSplitter(frame, FRAME_THICK|FRAME_RAISED|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        treeframe = FXVerticalFrame(splitter, FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X|LAYOUT_FILL_Y, 0,0,250,0, 0,0,0,0, 0,0)
        self.filterswitcher = FXSwitcher(splitter, FRAME_SUNKEN|FRAME_THICK|LAYOUT_FILL_X|LAYOUT_FILL_Y)
        f = FXHorizontalFrame(self.filterswitcher)
        FXLabel(f, _("All filters"))
        self.tree = FXRuleTreeList(treeframe, self, self.ID_FILTER, self.folders, FXRuleFrameFactory(self.filterswitcher))
        f = FXHorizontalFrame(treeframe, LAYOUT_FILL_X)
        addmenu = FXMenuPane(self)
        FXMenuCommand(addmenu, _("New Folder"), None, self, self.ID_NEWFOLDER)
        # Make new filter popup menu
        filtermenu = FXMenuPane(self)
        FXMenuCommand(filtermenu, "Allow", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Block", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Header", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Image", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Nocomments", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Rewrite", None, self, self.ID_NEWRULE)
        FXMenuCommand(filtermenu, "Replacer", None, self, self.ID_NEWRULE)
        FXMenuCascade(addmenu, _("Filter"), None, filtermenu)
        FXMenuButton(f, _("Add"), None, addmenu, MENUBUTTON_ATTACH_BOTH|MENUBUTTON_DOWN|JUSTIFY_HZ_APART|LAYOUT_TOP|FRAME_RAISED|FRAME_THICK|ICON_AFTER_TEXT)
        FXButton(f, _("Remove"), None, self, self.ID_REMOVE)
        FXButton(f, _("Up"), None, self, self.ID_UP)
        FXButton(f, _("Dwn"), None, self, self.ID_DOWN)


    def onUpdNoProxy (self, sender, sel, ptr):
        i = self.noproxylist.getCurrentItem()
        if i<0:
            sender.disable()
        elif self.noproxylist.isItemSelected(i):
            sender.enable()
        else:
            sender.disable()
        return 1


    def onCmdNewFolder(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "new folder")
        f = FolderRule("No title","",0,0,tempfile.mktemp()+".zap")
        self.tree.addFolder(f, create=1)
        self.sort_rules()
        self.getApp().dirty = 1
        return 1


    def onCmdNewRule(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "new filter rule")
        self.tree.newRule(GetRuleFromName(sender.getText()))
        self.getApp().dirty = 1
        return 1


    def onCmdTitle(self, sender, sel, ptr):
        item = self.tree.getCurrentItem()
        if item.isSelected():
            self.tree.setItemText(item, sender.getText())
            #debug(BRING_IT_ON, "updated tree item")
        return 1


    def onCmdDisableRule(self, sender, sel, ptr):
        item = self.tree.getCurrentItem()
        #debug(BRING_IT_ON, "%d" % item.getData())
        if item.isSelected():
            rule = self.tree.searchRule(item.getData())
            self.tree.setItemIcons(item, rule)


    def onCmdRemove(self, sender, sel, ptr):
        item = self.tree.getCurrentItem()
        if item.isSelected():
            if self.removeRule(item.getData()):
                self.tree.removeItem(item)
                self.filterswitcher.setCurrent(0)
                self.getApp().dirty = 1
                #debug(BRING_IT_ON, "removed filter")
            else:
                self.removeDialog.execute()
        else:
            self.error(_("filter selection"), _("no filter item selected"))
        return 1


    def onCmdAccept(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "Accept")
        if self.getApp().dirty:
            self.writeconfig()
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1


    def onCmdCancel(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "Cancel")
        self.getApp().handle(self, MKUINT(FXApp.ID_QUIT,SEL_COMMAND), ptr)
        return 1


    def onUpdApply(self, sender, sel, ptr):
        if self.getApp().dirty:
            sender.enable()
        else:
            sender.disable()
        return 1


    def onCmdApply(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "Apply")
        self.writeconfig()
        return 1


    def onCmdAbout(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "About")
        self.doShow(self.about)
        return 1


    def onCmdHelp(self, sender, sel, ptr):
        #debug(BRING_IT_ON, "Help")
        self.doShow(self.help)
        return 1


    def onCmdPort(self, sender, sel, ptr):
        self.port = sender.getValue()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Port=%d"%self.port)
        return 1


    def onCmdDebuglevel(self, sender, sel, ptr):
        if self.debuglevel != sender.getCurrentItem():
            self.debuglevel = sender.getCurrentItem()
            self.getApp().dirty = 1
            #debug(BRING_IT_ON, "Debuglevel=%d"%self.debuglevel)
        return 1


    def onCmdTimeout(self, sender, sel, ptr):
        if self.timeout != sender.getValue():
            self.timeout = sender.getValue()
            self.getApp().dirty = 1
            #debug(BRING_IT_ON, "Timeout=%d" % self.timeout)
        return 1


    def onCmdObfuscateIp(self, sender, sel, ptr):
        self.obfuscateip = sender.getCheck()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Obfuscateip=%d" % self.obfuscateip)
        return 1


    def onCmdShowErrors(self, sender, sel, ptr):
        self.showerrors = sender.getCheck()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Showerrors=%d" % self.showerrors)
        return 1


    def onCmdParentProxy(self, sender, sel, ptr):
        self.parentproxy = sender.getText()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Parentproxy=%s"%self.parentproxy)
        return 1


    def onCmdParentProxyPort(self, sender, sel, ptr):
        self.parentproxyport = sender.getValue()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Parentproxyport=%d"%self.parentproxyport)
        return 1


    def onCmdLogfile(self, sender, sel, ptr):
        self.logfile = sender.getText()
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Logfile=%s"%self.logfile)
        return 1


    def onCmdFilterModule(self, sender, sel, ptr):
        state = sender.getCheck()
        module = sender.getText()
        self.modules[module] = state
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Filtermodule %s = %d" % (module, state))
        return 1


    def onCmdFilter(self, sender, sel, ptr):
        if hasattr(ptr, "isSelected"):
            if not ptr.isSelected(): return 1
        index = ptr.getData()
        #debug(BRING_IT_ON, "tree item index %d" % index)
        if type(index) is IntType:
            self.filterswitcher.setCurrent(index)
        return 1


    def onCmdNoProxyForAdd(self, sender, sel, ptr):
        dialog = FXDialogBox(self,_("Add Hostname"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Hostname:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        host = FXTextField(matrix, 20)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            host = host.getText().strip().lower()
            if not host:
                self.error(_("Add proxy"), _("Empty hostname"))
	        return 1
            if self.noproxyfor.has_key(host):
                self.error(_("Add proxy"), _("Duplicate hostname"))
	        return 1
            self.noproxyfor[host] = 1
            self.noproxylist.appendItem(host)
            self.getApp().dirty = 1
            #debug(BRING_IT_ON, "Added no-proxy host")
        return 1


    def onCmdNoProxyForEdit(self, sender, sel, ptr):
        index = self.noproxylist.getCurrentItem()
        item = self.noproxylist.retrieveItem(index)
        host = item.getText()
        dialog = FXDialogBox(self, _("Edit Hostname"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("New hostname:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        nametf.setText(host)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            newhost = nametf.getText().strip().lower()
            del self.noproxyfor[host]
            self.noproxyfor[newhost] = 1
            self.noproxylist.replaceItem(index, newhost)
            self.getApp().dirty = 1
            #debug(BRING_IT_ON, "Changed no-proxy host")
        return 1


    def onCmdNoProxyForRemove(self, sender, sel, ptr):
        index = self.noproxylist.getCurrentItem()
        item = self.noproxylist.retrieveItem(index)
        host = item.getText()
        del self.noproxyfor[host]
        self.noproxylist.removeItem(index)
        self.getApp().dirty = 1
        #debug(BRING_IT_ON, "Removed no-proxy host")
        return 1


    def onCmdProxyStart(self, sender, sel, ptr):
        from wc import daemon
        daemon.start(parent_exit=0)
        #debug(BRING_IT_ON, "webcleaner start")
        return 1


    def onCmdProxyStop(self, sender, sel, ptr):
        from wc import daemon
        daemon.stop()
        #debug(BRING_IT_ON, "webcleaner stop")
        return 1


    def onCmdProxyRestart(self, sender, sel, ptr):
        from wc import daemon
        daemon.restart(parent_exit=0)
        #debug(BRING_IT_ON, "webcleaner restart")
        return 1


    def onCmdProxyReload(self, sender, sel, ptr):
        from wc import daemon
        daemon.reload()
        #debug(BRING_IT_ON, "webcleaner reload")
        return 1


    def onCmdProxyStatus(self, sender, sel, ptr):
        from wc import daemon
        dialog = FXMessageBox(self,_("Proxy Status"),daemon.status(),None,MBOX_OK)
        self.doShow(dialog)
        #debug(BRING_IT_ON, "webcleaner status")
        return 1


    def onCmdUp (self, sender, sel, ptr):
        # XXX todo
        return 1


    def onCmdDown (self, sender, sel, ptr):
        # XXX todo
        return 1


    def onCmdUpUpdate (self, sender, sel, ptr):
        # XXX todo
        sender.disable()
        return 1


    def onCmdDownUpdate (self, sender, sel, ptr):
        # XXX todo
        sender.disable()
        return 1


    def onCmdConfUpdate(self, sender, sel, ptr):
        """download files from http://webcleaner.sourceforge.net/zapper/
           and copy them over the existing config"""
        # base url for all files
        url = "http://webcleaner.sourceforge.net/zapper/"
        dialog = FXMessageBox(self,_("Update Help"),UpdateHelp % url,None,MBOX_OK_CANCEL)
        if self.doShow(dialog) != MBOX_CLICKED_OK:
            return 1
        try:
            doreload = 0
            import urllib,md5
            lines = urllib.urlopen(url+"md5sums").readlines()
            from glob import glob
            filemap = {}
            for file in glob(wc.ConfigDir+"/*.zap"):
                filemap[os.path.basename(file)] = file
            for line in lines:
                if "<" in line:
                    raise IOError, "could not fetch "+url+"md5sums"
                if not line: continue
                md5sum,filename = line.split()
                # compare checksums
                if filemap.has_key(filename):
                    file = filemap[filename]
                    data = open(file).read()
                    digest = list(md5.new(data).digest())
                    digest = map(lambda c: "%0.2x" % ord(c), digest)
                    digest = "".join(digest)
                    if digest==md5sum:
                        #debug(BRING_IT_ON, "%s is uptodate" % filename)
		        continue
                    # move away old file
                    os.rename(file, file+".old")
                    # copy new file
                    f = open(file, 'w')
                    f.write(urllib.urlopen(url+filename).read())
                    f.close()
                    doreload = 1
                else: # new file, just download it
                    f = open(file, 'w')
                    f.write(urllib.urlopen(url+filename).read())
                    f.close()
                    doreload = 1
        except IOError, msg:
            self.error(_("Update Error"), "%s: %s" % (_("Update Error"), msg))
        else:
            if doreload:
                self.handle(self, MKUINT(ConfWindow.ID_PROXYRESTART,SEL_COMMAND), None)
        return 1


    def removeRule(self, index):
        for f in self.folders:
            for i in range(len(f.rules)):
                if f.rules[i].index == index:
                    f.delete_rule(i)
                    return 1
        return 0


    def readconfig(self):
        """read the configuration from disc"""
        #debug(BRING_IT_ON, "reading config")
        self.config = wc.Configuration()
        for key in ('version','port','parentproxy','parentproxyport',
         'timeout','obfuscateip','debuglevel','logfile',
	 'configfile', 'noproxyfor', 'showerrors', 'proxyuser', 'proxypass'):
            setattr(self, key, self.config[key])
        self.modules = {
	    "Header":0,
	    "Blocker":0,
	    "GifImage":0,
	    "BinaryCharFilter":0,
	    "Rewriter":0,
            "Replacer":0,
	    "Compress":0,
	}
        for f in self.config['filters']:
            self.modules[f] = 1
        # sort the filter list by title
        self.folders = self.config['rules']


    def writeconfig(self):
        """write the current configuration to disc"""
        self.getApp().beginWaitCursor()
        dirty = 0
        errors = []
        try:
            file = open(self.configfile, 'w')
            file.write(self.toxml())
            file.close()
        except IOError:
            errors.append(_("cannot write to file %s") % self.configfile)
            dirty = 1
        for f in self.folders:
            try:
                file = open(f.filename, 'w')
                file.write(f.toxml())
                file.close()
            except IOError:
                dirty = 1
                errors.append(_("cannot write to file %s") % f.filename)
        self.getApp().dirty = dirty
        self.getApp().endWaitCursor()
        if errors:
            self.error(_("Write config"), "\n".join(errors))


    def toxml(self):
        s = """<?xml version="1.0"?>
<!DOCTYPE webcleaner SYSTEM "webcleaner.dtd">
<webcleaner
"""
        s += ' version="%s"\n' % self.version +\
             ' port="%d"\n' % self.port +\
             ' proxyuser="%s"\n' % self.proxyuser +\
             ' proxypass="%s"\n' % self.proxypass
        if self.parentproxy:
            s += ' parentproxy="%s"\n' % self.parentproxy
        s += ' parentproxyuser="%s"\n' % self.parentproxyuser
        s += ' parentproxypass="%s"\n' % self.parentproxypass
        s += ' parentproxyport="%d"\n' % self.parentproxyport +\
             ' timeout="%d"\n' % self.timeout +\
             ' obfuscateip="%d"\n' % self.obfuscateip +\
             ' debuglevel="%d"\n' % self.debuglevel +\
             ' showerrors="%d"\n' % self.showerrors
        if self.logfile:
            s += ' logfile="%s"\n' % self.logfile
        if self.noproxyfor:
            s += ' noproxyfor="%s"\n' % ",".join(self.noproxyfor.keys())
        s += '>\n'
        for key,val in self.modules.items():
            if val:
                s += '<filter name="%s"/>\n' % key
        return s + '</webcleaner>\n'
