# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2009 Bastian Kleineidam
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

import os.path

import PageTemplates.PageTemplate
import PageTemplates.Expressions
import TAL.TALInterpreter
import ZTUtils


class WebCleanerTemplate (PageTemplates.PageTemplate.PageTemplate):
    """A page template class."""

    def __init__ (self, path, mtime):
        """
        Store modification time and compile template from given path.
        """
        super(WebCleanerTemplate, self).__init__()
        self.mtime = mtime
        self.pt_edit(open(path), 'text/html')
        if self._v_errors:
            msg = ", ".join(self._v_errors)
            name = os.path.basename(path)
            raise PageTemplates.PageTemplate.PTRuntimeError(
                                         'Template /%s:\n%s' % (name, msg))

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
        out = ZTUtils.FasterStringIO()
        __traceback_supplement__ = \
          (PageTemplates.PageTemplate.PageTemplateTracebackSupplement, self)
        engine = PageTemplates.Expressions.getEngine()
        TAL.TALInterpreter.TALInterpreter(
            self._v_program, self.macros,
            engine.getContext(context), out, tal=1, strictinsert=0)()
        return out.getvalue().encode("iso8859-1")
