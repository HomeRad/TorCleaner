# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
"""
TAL template class for WebCleaner.
"""

import wc.webgui.PageTemplates.PageTemplate
import wc.webgui.PageTemplates.Expressions
import wc.webgui.TAL.TALInterpreter
import wc.webgui.ZTUtils


class WebCleanerTemplate (wc.webgui.PageTemplates.PageTemplate.PageTemplate):
    """A page template class."""

    def __init__ (self, path, mtime):
        """
        Store modification time and compile template from given path.
        """
        super(WebCleanerTemplate, self).__init__()
        self.mtime = mtime
        self.pt_edit(open(path), 'text/html')
        if self._v_errors:
            raise wc.webgui.PageTemplates.PageTemplate.PTRuntimeError, \
                                    'Page Template %s has errors.' % self.id

    def html (self):
        """
        Only HTML is supported at the moment.

        @return: True
        """
        return True

    def render (self, context):
        """
        Render this Page Template.
        """
        out = wc.webgui.ZTUtils.FasterStringIO()
        __traceback_supplement__ = \
  (wc.webgui.PageTemplates.PageTemplate.PageTemplateTracebackSupplement, self)
        engine = wc.webgui.PageTemplates.Expressions.getEngine()
        wc.webgui.TAL.TALInterpreter.TALInterpreter(
            self._v_program, self.macros,
            engine.getContext(context), out, tal=1, strictinsert=0)()
        return out.getvalue().encode("iso8859-1")
