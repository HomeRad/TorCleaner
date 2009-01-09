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
A template cache.
"""

import os
import stat
import errno

import template


class TemplateCache (dict):
    """
    Handle requests for templates. Compiled templates are cached for
    performance reasons and only reloaded if the template file changes.
    """

    def __getitem__ (self, key):
        """
        The key must be a path suitable for an open() and os.stat()
        call, except when the path is already cached and the file
        has been deleted. In this case, the already cached template
        is returned, ignoring the file deletion.

        @return: compiled TAL template from given path
        """
        if key in self:
            _template = super(TemplateCache, self).__getitem__(key)
            try:
                mtime = os.stat(key)[stat.ST_MTIME]
                if mtime > _template.mtime:
                    # refresh entry
                    _template = template.WebCleanerTemplate(key, mtime)
                    self[key] = _template
            except os.error, msg:
                # ignore missing files if already cached
                if msg.errno != errno.ENOENT:
                    raise
        else:
            # new entry
            mtime = os.stat(key)[stat.ST_MTIME]
            _template = template.WebCleanerTemplate(key, mtime)
            self[key] = _template
        return _template


templates = TemplateCache()
