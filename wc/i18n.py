"""internationalization support"""
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

# i18n suppport
import os, locale, gettext
from wc import LocaleDir, Name

_gettext = None
supported_languages = []
default_language = None

def init_gettext ():
    global _gettext
    try:
        _gettext = gettext.translation(Name, LocaleDir).gettext
    except IOError, msg:
        # default gettext function
        _gettext = lambda s: s
    # get supported languages
    for d in os.listdir(LocaleDir):
        path = os.path.join(LocaleDir, d)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, 'LC_MESSAGES', '%s.mo'%Name)):
            supported_languages.append(d)


def _ (msg, lang=None):
    if lang is not None:
        return gettext.translation(Name, LocaleDir, lang).gettext(msg)
    return _gettext(msg)


def get_lang (lang):
    if lang in supported_languages:
        return lang
    return default_language


def get_headers_lang (headers):
    if not headers.has_key('Accept-Language'):
        return default_language
    languages = headers['Accept-Language'].split(",")
    # XXX sort with quality values
    languages = [ lang.split(";")[0].strip() for lang in languages ]
    for lang in languages:
        if lang in supported_languages:
            return lang
    return default_language


def get_locale ():
    loc = locale.getdefaultlocale()[0]
    loc = locale.normalize(loc)
    # split up the locale into its base components
    pos = loc.find('@')
    if pos >= 0:
        loc = loc[:pos]
    pos = loc.find('.')
    if pos >= 0:
        loc = loc[:pos]
    pos = loc.find('_')
    if pos >= 0:
        loc = loc[:pos]
    return loc


init_gettext()
