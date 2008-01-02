# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2008 Bastian Kleineidam
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
HTML configuration interface functions.
"""

import os
import re
import urllib
import urlparse

import wc.configuration
import wc.i18n
import wc.log


def norm (path):
    """
    Normalize a path name.
    """
    return os.path.realpath(os.path.normpath(os.path.normcase(path)))


safe_path = re.compile(r"[-a-zA-Z0-9_.]+").match
def is_safe_path (path):
    """
    Return True iff path is safe for opening.
    """
    return safe_path(path) and ".." not in path


def get_relative_path (path):
    """
    Return splitted and security filtered path.
    """
    # get non-empty url path components, remove path fragments
    dirs = [ urlparse.urldefrag(d)[0] for d in path.split("/") if d ]
    # remove ".." and other invalid paths (security!)
    return [ d for d in dirs if is_safe_path(d) ]


def get_template_url (url, lang):
    """
    Return tuple (path, dirs, lang).
    """
    parts = urlparse.urlsplit(url)
    return get_template_path(urllib.unquote(parts[2]), lang)


def get_safe_template_path (path):
    """
    Return tuple (path, dirs).
    """
    base = os.path.join(wc.TemplateDir, wc.configuration.config['gui_theme'])
    base = norm(base)
    dirs = get_relative_path(path)
    if not dirs:
        # default template
        dirs = ['index.html']
    path = os.path.splitdrive(os.path.join(*tuple(dirs)))[1]
    path = norm(os.path.join(base, path))
    if not os.path.isabs(path):
        raise IOError("Relative path %r" % path)
    if not path.startswith(base):
        raise IOError("Invalid path %r" % path)
    return path, dirs


def get_template_path (path, defaultlang):
    """
    Return tuple (path, dirs, lang).
    """
    path, dirs = get_safe_template_path(path)
    lang = defaultlang
    for la in wc.i18n.supported_languages:
        assert len(la) == 2
        if path.endswith(".html.%s" % la):
            path = path[:-3]
            dirs[-1] = dirs[-1][:-3]
            lang = la
            break
    if not os.path.isfile(path):
        raise IOError("Non-file path %r" % path)
    return path, dirs, lang
