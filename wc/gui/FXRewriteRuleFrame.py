import sys
from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import _,debug,error
from wc.debug_levels import *

class FXRewriteRuleFrame(FXRuleFrame):
    """display all variables found in a RewriteRule"""
    (ID_TAG,
     ID_ENCLOSED_BLOCK,
     ID_REPLACE_PART,
     ID_ATTRIBUTE_ADD,
     ID_ATTRIBUTE_EDIT,
     ID_ATTRIBUTE_REMOVE,
     ID_REPLACE_VALUE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+7)

    def __init__(self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_TAG,FXRewriteRuleFrame.onCmdTag)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ENCLOSED_BLOCK,FXRewriteRuleFrame.onCmdEnclosed)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_REPLACE_PART,FXRewriteRuleFrame.onCmdReplacePart)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_REPLACE_VALUE,FXRewriteRuleFrame.onCmdReplaceValue)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_ADD,FXRewriteRuleFrame.onCmdAttributeAdd)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_EDIT,FXRewriteRuleFrame.onCmdAttributeEdit)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_REMOVE,FXRewriteRuleFrame.onCmdAttributeRemove)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Tag name:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 10, self, FXRewriteRuleFrame.ID_TAG)
        t.setText(self.rule.tag)
        FXLabel(matrix, _("Attributes:"))
        f = FXHorizontalFrame(matrix, LAYOUT_FILL_X|LAYOUT_FIX_HEIGHT|FRAME_SUNKEN|FRAME_THICK, 0,0,0,60, 0,0,0,0, 0,0)
        self.iconlist = FXIconList(f, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y|ICONLIST_SINGLESELECT|ICONLIST_AUTOSIZE)
        self.iconlist.appendHeader(_("Name"),NULL,50)
        self.iconlist.appendHeader(_("Value"),NULL,175)
        for name,value in self.rule.attrs.items():
            self.iconlist.appendItem(name+"\t"+value)
        FXLabel(matrix, "")
        f = FXHorizontalFrame(matrix)
        FXButton(f, _("Add"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_ADD)
        FXButton(f, _("Edit"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_EDIT)
        FXButton(f, _("Remove"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_REMOVE)
        FXLabel(matrix, _("Enclosed block:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 20, self, FXRewriteRuleFrame.ID_ENCLOSED_BLOCK)
        if self.rule.enclosed:
            t.setText(self.rule.enclosed)
        FXLabel(matrix, _("Replace part:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXComboBox(matrix,9,6,self, self.ID_REPLACE_PART,opts=COMBOBOX_INSERT_LAST|FRAME_SUNKEN|FRAME_THICK|LAYOUT_SIDE_TOP)
        t.appendItem(_("Tag"))
        t.appendItem(_("Tag name"))
        t.appendItem(_("Attribute"))
        t.appendItem(_("Attribute value"))
        t.appendItem(_("Complete tag"))
        t.appendItem(_("Enclosed block"))
        t.setEditable(0)
        t.setCurrentItem(self.rule.replace[0])
        FXLabel(matrix, _("Replace value:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 20, self, FXRewriteRuleFrame.ID_REPLACE_VALUE)
        t.setText(self.rule.replace[1])


    def onCmdTag(self, sender, sel, ptr):
        tag = sender.getText().strip()
        if not tag:
            error("empty tag name")
            sender.setText(self.rule.tag)
            return 1
        self.rule.tag = tag
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule tag name")
        return 1


    def onCmdEnclosed(self, sender, sel, ptr):
        enclosed = sender.getText().strip()
        if enclosed:
            self.rule.enclosed = enclosed
        else:
            self.rule.enclosed = None
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule enclosed block")
        return 1


    def onCmdReplacePart(self, sender, sel, ptr):
        self.rule.replace[0] = sender.getCurrentItem()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule replace part")
        return 1

    def onCmdAttributeAdd(self, sender, sel, ptr):
        dialog = FXDialogBox(self,_("Add Attribute"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("Name:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        FXLabel(matrix, _("Value:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        valuetf = FXTextField(matrix, 20)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            name = nametf.getText().strip().lower()
            if not name:
                error(_("Empty attribute name"))
	        return 1
            if self.rule.attrs.has_key(name):
                error(_("Duplicate attribute name"))
                return 1
            try:
                value = valuetf.getText().strip()
            except:
                error(_("Invalid regex %s: %s") % (value,sys.exc_info()[1]))
                return 1
            self.rule.attrs[name] = value
            self.getApp().dirty = 1
            self.iconlist.appendItem(name+"\t"+value)
            debug(BRING_IT_ON, "Added rule attribute")
        return 1

    def onCmdAttributeEdit(self, sender, sel, ptr):
        index = self.iconlist.getCurrentItem()
        if index < 0: return 1
        item = self.iconlist.retrieveItem(index)
        if not item.isSelected(): return 1
        name,value = item.getText().split('\t')
        dialog = FXDialogBox(self, _("Edit Attribute"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, _("New name:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        nametf.setText(name)
        FXLabel(matrix, _("New value:"), opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        valuetf = FXTextField(matrix, 20)
        valuetf.setText(value)
        f = FXHorizontalFrame(frame)
        FXButton(f, _("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, _("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            newname = nametf.getText().strip().lower()
            try:
                value = valuetf.getText().strip()
            except:
                error(_("Invalid regex %s: %s")%(value,sys.exc_info()[1]))
                return 1
            del self.rule.attrs[name]
            self.rule.attrs[newname] = value
            self.getApp().dirty = 1
            self.iconlist.replaceItem(index, newname+"\t"+value)
            debug(BRING_IT_ON, "Changed rule attribute")
        return 1

    def onCmdAttributeRemove(self, sender, sel, ptr):
        index = self.iconlist.getCurrentItem()
        if index < 0: return 1
        item = self.iconlist.retrieveItem(index)
        if not item.isSelected(): return 1
        name,value = item.getText().split('\t')
        del self.rule.attrs[name]
        self.getApp().dirty = 1
        self.iconlist.removeItem(index)
        debug(BRING_IT_ON, "Removed rule attribute")
        return 1

    def onCmdReplaceValue(self, sender, sel, ptr):
        self.rule.replace[1] = sender.getText()
        self.getApp().dirty = 1
        debug(BRING_IT_ON, "Changed rule replace value")
        return 1



