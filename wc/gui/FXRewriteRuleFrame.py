"""RewriteRule frame widget"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sys
from FXRuleFrame import FXRuleFrame
from FXPy.fox import *
from wc import i18n
from wc.log import *
from wc.filter.rules.RewriteRule import partvalnames, partnames


class FXRewriteRuleFrame (FXRuleFrame):
    """display all variables found in a RewriteRule"""
    (ID_TAG,
     ID_ENCLOSED_BLOCK,
     ID_REPLACE_PART,
     ID_ATTRIBUTE_ADD,
     ID_ATTRIBUTE_EDIT,
     ID_ATTRIBUTE_REMOVE,
     ID_REPLACE_VALUE,
    ) = range(FXRuleFrame.ID_LAST, FXRuleFrame.ID_LAST+7)


    def __init__ (self, parent, rule, index):
        FXRuleFrame.__init__(self, parent, rule, index)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_TAG,FXRewriteRuleFrame.onCmdTag)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ENCLOSED_BLOCK,FXRewriteRuleFrame.onCmdEnclosed)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_REPLACE_PART,FXRewriteRuleFrame.onCmdReplacePart)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_REPLACE_VALUE,FXRewriteRuleFrame.onCmdReplaceValue)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_ADD,FXRewriteRuleFrame.onCmdAttributeAdd)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_EDIT,FXRewriteRuleFrame.onCmdAttributeEdit)
        FXMAPFUNC(self,SEL_UPDATE,FXRewriteRuleFrame.ID_ATTRIBUTE_EDIT,FXRewriteRuleFrame.onUpdAttributes)
        FXMAPFUNC(self,SEL_COMMAND,FXRewriteRuleFrame.ID_ATTRIBUTE_REMOVE,FXRewriteRuleFrame.onCmdAttributeRemove)
        FXMAPFUNC(self,SEL_UPDATE,FXRewriteRuleFrame.ID_ATTRIBUTE_REMOVE,FXRewriteRuleFrame.onUpdAttributes)
        matrix = FXMatrix(self, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Tag name")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 25, self, FXRewriteRuleFrame.ID_TAG)
        t.setText(self.rule.tag)
        FXLabel(matrix, i18n._("Attributes")+":")
        f = FXHorizontalFrame(matrix, LAYOUT_FILL_X|LAYOUT_FIX_HEIGHT|FRAME_SUNKEN|FRAME_THICK, 0,0,0,60, 0,0,0,0, 0,0)
        self.iconlist = FXIconList(f, opts=LAYOUT_FILL_X|LAYOUT_FILL_Y|ICONLIST_SINGLESELECT|ICONLIST_AUTOSIZE)
        self.iconlist.appendHeader(i18n._("Name"),NULL,50)
        self.iconlist.appendHeader(i18n._("Value"),NULL,175)
        for name,value in self.rule.attrs.items():
            self.iconlist.appendItem(name+"\t"+value)
        FXLabel(matrix, "")
        f = FXHorizontalFrame(matrix)
        FXButton(f, i18n._("Add"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_ADD)
        FXButton(f, i18n._("Edit"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_EDIT)
        FXButton(f, i18n._("Remove"), None, self, FXRewriteRuleFrame.ID_ATTRIBUTE_REMOVE)
        FXLabel(matrix, i18n._("Enclosed block")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 25, self, FXRewriteRuleFrame.ID_ENCLOSED_BLOCK)
        if self.rule.enclosed:
            t.setText(self.rule.enclosed)
        FXLabel(matrix, i18n._("Replace part")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXComboBox(matrix,23,6,self, self.ID_REPLACE_PART,opts=COMBOBOX_INSERT_LAST|FRAME_SUNKEN|FRAME_THICK|LAYOUT_SIDE_TOP)
        for part in partvalnames:
            t.appendItem(partnames[part])
        t.setEditable(0)
        t.setCurrentItem(self.rule.part)
        FXLabel(matrix, i18n._("Replace value")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        t = FXTextField(matrix, 25, self, FXRewriteRuleFrame.ID_REPLACE_VALUE)
        t.setText(self.rule.replacement)


    def onCmdTag (self, sender, sel, ptr):
        tag = sender.getText().strip()
        if not tag:
            self.getApp().error(i18n._("Error"), i18n._("Empty tag name"))
            sender.setText(self.rule.tag)
            return 1
        self.rule.tag = tag
        self.getApp().dirty = 1
        debug(GUI, "Changed rule tag name")
        return 1


    def onCmdEnclosed (self, sender, sel, ptr):
        enclosed = sender.getText().strip()
        if enclosed:
            self.rule.enclosed = enclosed
        else:
            self.rule.enclosed = None
        self.getApp().dirty = 1
        debug(GUI, "Changed rule enclosed block")
        return 1


    def onCmdReplacePart (self, sender, sel, ptr):
        self.rule.part = sender.getCurrentItem()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule replace part")
        return 1


    def onCmdAttributeAdd (self, sender, sel, ptr):
        dialog = FXDialogBox(self,i18n._("Add Attribute"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("Name")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        FXLabel(matrix, i18n._("Value")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        valuetf = FXTextField(matrix, 20)
        f = FXHorizontalFrame(frame)
        FXButton(f, i18n._("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, i18n._("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            name = nametf.getText().strip().lower()
            if not name:
                self.getApp().error(i18n._("Error"),
                         i18n._("Empty attribute name"))
	        return 1
            if self.rule.attrs.has_key(name):
                self.getApp().error(i18n._("Error"),
                         i18n._("Duplicate attribute name"))
                return 1
            value = valuetf.getText().strip()
            self.rule.attrs[name] = value
            self.getApp().dirty = 1
            self.iconlist.appendItem(name+"\t"+value)
            debug(GUI, "Added rule attribute")
        return 1


    def onCmdAttributeEdit (self, sender, sel, ptr):
        index = self.iconlist.getCurrentItem()
        item = self.iconlist.retrieveItem(index)
        name,value = item.getText().split('\t')
        dialog = FXDialogBox(self, i18n._("Edit Attribute"),DECOR_TITLE|DECOR_BORDER)
        frame = FXVerticalFrame(dialog, LAYOUT_SIDE_TOP|FRAME_NONE|LAYOUT_FILL_X|LAYOUT_FILL_Y|PACK_UNIFORM_WIDTH)
        matrix = FXMatrix(frame, 2, MATRIX_BY_COLUMNS)
        FXLabel(matrix, i18n._("New name")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        nametf = FXTextField(matrix, 20)
        nametf.setText(name)
        FXLabel(matrix, i18n._("New value")+":", opts=LAYOUT_CENTER_Y|LAYOUT_LEFT)
        valuetf = FXTextField(matrix, 20)
        valuetf.setText(value)
        f = FXHorizontalFrame(frame)
        FXButton(f, i18n._("&Ok"), None, dialog, FXDialogBox.ID_ACCEPT,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        FXButton(f, i18n._("&Cancel"), None, dialog, FXDialogBox.ID_CANCEL,FRAME_RAISED|FRAME_THICK|LAYOUT_CENTER_X|LAYOUT_CENTER_Y)
        if dialog.execute():
            newname = nametf.getText().strip().lower()
            value = valuetf.getText().strip()
            del self.rule.attrs[name]
            self.rule.attrs[newname] = value
            self.getApp().dirty = 1
            self.iconlist.replaceItem(index, newname+"\t"+value)
            debug(GUI, "Changed rule attribute")
        return 1


    def onCmdAttributeRemove (self, sender, sel, ptr):
        index = self.iconlist.getCurrentItem()
        item = self.iconlist.retrieveItem(index)
        name,value = item.getText().split('\t')
        del self.rule.attrs[name]
        self.getApp().dirty = 1
        self.iconlist.removeItem(index)
        debug(GUI, "Removed rule attribute")
        return 1


    def onUpdAttributes (self, sender, sel, ptr):
        i = self.iconlist.getCurrentItem()
        if i<0:
            sender.disable()
        elif self.iconlist.isItemSelected(i):
            sender.enable()
        else:
            sender.disable()
        return 1


    def onCmdReplaceValue (self, sender, sel, ptr):
        self.rule.replacement = sender.getText()
        self.getApp().dirty = 1
        debug(GUI, "Changed rule replace value")
        return 1

