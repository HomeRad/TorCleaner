# -*- coding: iso-8859-1 -*-
"""basic start and init methods"""
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

import os
import time
import socket
import glob
import logging.config
import logging.handlers

import _webcleaner2_configdata as configdata
import wc.log
import wc.i18n

Version = configdata.version
AppName = configdata.appname
Name = configdata.name
Description = configdata.description
App = AppName+" "+Version
UserAgent = AppName+"/"+Version
Author =  configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = "Copyright � 2000-2002 "+Author
HtmlCopyright = "Copyright &copy; 2000-2003 "+HtmlAuthor
AppInfo = App+"              "+Copyright
HtmlAppInfo = App+", "+HtmlCopyright
Url = configdata.url
Email = configdata.author_email
Freeware = """%(appname)s comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions. Look at the file `LICENSE' whithin this
distribution.""" % {'appname': AppName}
ConfigDir = configdata.config_dir
TemplateDir = configdata.template_dir
ConfigCharset = "iso-8859-1"

# logger areas
LOG_FILTER = "wc.filter"
LOG_JS = "wc.filter.js"
LOG_NET = "wc.net"
LOG_PROXY = "wc.proxy"
LOG_AUTH = "wc.proxy.auth"
LOG_DNS = "wc.proxy.dns"
LOG_GUI = "wc.gui"
LOG_ACCESS = "wc.access"
LOG_RATING = "wc.rating"
LOG_TAL = "TAL"
LOG_TALES = "TALES"


def init_i18n ():
    """Deploy i18n gettext method into the default namespace.
       The LOCPATH environment variable is supported.
    """
    wc.i18n.init(configdata.name, get_locdir())

def get_locdir ():
    """return locale directory"""
    locdir = os.environ.get('LOCPATH')
    if locdir is None:
        locdir = os.path.join(configdata.install_data, 'share', 'locale')
    return locdir


def get_translator (lang, translatorklass=None):
    """return TAL translator class"""
    return wc.i18n.get_translator(configdata.name, get_locdir(), lang,
         translatorklass=translatorklass)


def initlog (filename, appname, filelogs=True):
    """initialize logfiles and configuration"""
    logging.config.fileConfig(filename)
    if filelogs:
        trydirs = []
        if os.name == "nt":
            trydirs.append(ConfigDir)
        logname = "%s.log" % appname
        logfile = wc.log.get_log_file(appname, logname, trydirs=trydirs)
        handler = get_wc_handler(logfile)
        logging.getLogger("wc").addHandler(handler)
        logging.getLogger("TAL").addHandler(handler)
        logging.getLogger("TALES").addHandler(handler)
        # access log is always a file
        logname = "%s-access.log" % appname
        logfile = wc.log.get_log_file(appname, logname, trydirs=trydirs)
        handler = get_access_handler(logfile)
        logging.getLogger("wc.access").addHandler(handler)


def get_wc_handler (logfile):
    """return a handler for webcleaner logging"""
    mode = 'a'
    max_bytes = 1024*1024*2 # 2 MB
    backup_count = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(
                                     logfile, mode, max_bytes, backup_count)
    return wc.log.set_format(handler)


def get_access_handler (logfile):
    """return a handler for access logging"""
    mode = 'a'
    max_bytes = 1024*1024*2 # 2 MB
    backup_count = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(
                                     logfile, mode, max_bytes, backup_count)
    # log only the message
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def sort_seq (seq):
    """return sorted list of given sequence"""
    l = list(seq)
    l.sort()
    return l

