from FXPy.fox import *
from wc import _,debug
from wc.gui import loadIcon
from FXRuleFrameFactory import FXRuleFrameFactory
from wc.debug_levels import *


class FXRuleTreeList(FXTreeList):
    def __init__(self, frame, parent, msgid, folders, factory):
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

    def addFolder(self, f, create=0):
        item = self.createRuleItem(f)
        frame = f.fromFactory(self.factory)
        item.setData(frame.rule.index)
        branch = self.addItemLast(self.topmost, item)
        if create:
            frame.create()
            self.folders.append(f)
        for r in f.rules:
            self.addRule(branch, r, create)
        return item

    def addRule(self, branch, rule, create=0):
        item = self.createRuleItem(rule)
        frame = rule.fromFactory(self.factory)
        item.setData(frame.rule.index)
        self.addItemLast(branch, item)
        if create:
            frame.create()
        return item

    def newRule(self, rule):
        item = self.getCurrentItem()
        # we must have selected a rule folder:
        debug(BRING_IT_ON, "item index %d"%item.getData())
        if item.getData()==0:
            item = item.getBelow()
        elif not self.searchFolder(item.getData()):
            item = item.getParent()
        debug(BRING_IT_ON, "item index %d"%item.getData())
        self.expandTree(item)
        folder = self.searchFolder(item.getData())
        rule.parent = folder
        folder.append_rule(rule)
        item = self.addRule(item, rule, 1)
        debug(BRING_IT_ON, "item index %d"%item.getData())

    def searchFolder(self, index):
        for f in self.folders:
            if f.index == index:
                return f

    def searchRule(self, index):
        for f in self.folders:
            if f.index == index:
                return f
            for r in f.rules:
                if r.index == index:
                    return r

    def createRuleItem(self, rule):
        item = FXTreeItem(rule.title)
        self.setItemIcons(item, rule)
        return item

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

