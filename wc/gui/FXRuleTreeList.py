from FXPy.fox import *
from wc import i18n
from wc.gui import loadIcon
from FXRuleFrameFactory import FXRuleFrameFactory
from wc.debug import *


class FXRuleTreeList (FXTreeList):
    def __init__ (self, frame, parent, msgid, folders, factory):
        FXTreeList.__init__(self, frame, 0, parent, msgid, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y)
        self.setListStyle(TREELIST_SHOWS_LINES|TREELIST_SHOWS_BOXES|TREELIST_SINGLESELECT)
        self.icon_open = loadIcon(self.getApp(), 'minifolderopen.png')
        self.icon_closed = loadIcon(self.getApp(), 'minifolder.png')
        self.icon_disabled = loadIcon(self.getApp(), 'disabledrule.png')
        self.icon_doc = loadIcon(self.getApp(), 'minidoc.png')
        topItem = FXTreeItem('Filter', self.icon_open, self.icon_closed)
        topItem.setData(0)
        self.topmost = self.addItemLast(None, topItem)
        self.expandTree(self.topmost)
        self.factory = factory
        self.folders = folders
        # add initial folders
        for f in self.folders:
            self.addFolder(f)

    def addFolder (self, f, create=0):
        frame = self.createRuleItem(f)
        branch = self.addItemLast(self.topmost, f.item)
        if create:
            frame.create()
            self.folders.append(f)
        for r in f.rules:
            self.addRule(branch, r, create=create)

    def addRule (self, branch, rule, create=0):
        frame = self.createRuleItem(rule)
        self.addItemLast(branch, rule.item)
        if create:
            frame.create()

    def newRule (self, rule):
        item = self.getCurrentItem()
        # we must have selected a rule folder:
        debug(BRING_IT_ON, "item index %d"%item.getData())
        if item.getData()==0:
            item = item.getBelow()
        elif not self.searchIndexFolder(item.getData()):
            item = item.getParent()
        debug(BRING_IT_ON, "item index %d"%item.getData())
        self.expandTree(item)
        folder = self.searchIndexFolder(item.getData())
        rule.parent = folder
        folder.append_rule(rule)
        self.addRule(item, rule, 1)

    def searchIndexFolder (self, index):
        for f in self.folders:
            if f.index == index:
                return f

    def searchIndexRule (self, index):
        for f in self.folders:
            if f.index == index:
                return f
            for r in f.rules:
                if r.index == index:
                    return r

    def searchOidRule (self, item, oid):
        if self.isItemLeaf(item):
            for f in self.folders:
                for r in f.rules:
                    if r.oid == oid:
                        return r
        else:
            for f in self.folders:
                if f.oid == oid:
                    return f

    def createRuleItem (self, rule):
        if rule.get_name()!="folder":
            title = "[%s] %s" % (rule.get_name(), rule.title)
        else:
            title = rule.title
        rule.item = FXTreeItem(title)
        self.setItemIcons(rule.item, rule)
        frame = rule.fromFactory(self.factory)
        rule.item.setData(rule.index)
        return frame

    def onCmdUp (self):
        item = self.getCurrentItem()
        if self.isItemSelected(item):
            index = item.getData()
            debug(BRING_IT_ON, "onCmdUp: tree item index %d" % index)
            rule = self.searchIndexRule(index)
            debug(BRING_IT_ON, "onCmdUp: rule %s" % rule)
            rule_before = self.searchOidRule(item, rule.oid-1)
            rule_before.oid, rule.oid = rule.oid, rule_before.oid
            self.sort()
            self.removeItem(item)
            self.addItemBefore2(rule_before.item, item)

    def onCmdDown (self):
        item = self.getCurrentItem()
        if self.isItemSelected(item):
            index = item.getData()
            debug(BRING_IT_ON, "onCmdUp: tree item index %d" % index)
            rule = self.searchIndexRule(index)
            rule_after = self.searchOidRule(item, rule.oid+1)
            rule_after.oid, rule.oid = rule.oid, rule_after.oid
            self.sort()
            self.removeItem(item)
            self.addItemAfter2(rule_after.item, item)

    def sort (self):
        for f in self.folders: f.sort()
        self.folders.sort()

    def setItemIcons(self, item, rule):
        if rule.disable:
            # disabled
            self.setItemOpenIcon(item, self.icon_disabled)
	    self.setItemClosedIcon(item, self.icon_disabled)
        elif rule.get_name()=='folder':
            # folder rule
            self.setItemOpenIcon(item, self.icon_open)
	    self.setItemClosedIcon(item, self.icon_closed)
        else:
            # normal rule
            self.setItemOpenIcon(item, self.icon_doc)
	    self.setItemClosedIcon(item, self.icon_doc)

