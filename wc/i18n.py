# -*- coding: iso-8859-1 -*-
"""internationalization support"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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
import os
import locale
import gettext
import wc

# more supported languages are added in init_gettext
supported_languages = ['en']
default_language = None

def init_gettext ():
    """initialize this gettext i18n module"""
    global _, default_language
    try:
        _ = gettext.translation(wc.Name, wc.LocaleDir).gettext
    except IOError:
        # default gettext function
        _ = lambda s: s
    # get supported languages
    for lang in os.listdir(wc.LocaleDir):
        path = os.path.join(wc.LocaleDir, lang)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, 'LC_MESSAGES', '%s.mo'%wc.Name)):
            supported_languages.append(lang)
    loc = get_locale()
    if loc in supported_languages:
        default_language = loc
    else:
        default_language = "en"


def get_lang (lang):
    """return lang if it is supported, or the default language"""
    if lang in supported_languages:
        return lang
    return default_language


def get_headers_lang (headers):
    """return preferred supported language in given HTTP headers"""
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
    """return current configured locale"""
    loc = locale.getdefaultlocale()[0]
    if loc is None:
        loc = 'C'
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


lang_names = {
    'en': u'English',
    'de': u'Deutsch',
}
lang_transis = {
    'de': {'en': u'German'},
    'en': {'de': u'Englisch'},
}

def lang_name (lang):
    """return full name of given language"""
    return lang_names[lang]


def lang_trans (lang, curlang):
    """return translated full name of given language"""
    return lang_transis[lang][curlang]


init_gettext()
