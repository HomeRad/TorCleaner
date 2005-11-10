# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
Basic start and init methods.
"""

import sys
if not hasattr(sys, "version_info"):
    raise SystemExit, "This program requires Python 2.4 or later."
if sys.version_info < (2, 4, 0, 'final', 0):
    raise SystemExit, "This program requires Python 2.4 or later."
import os
import logging.config

import _webcleaner2_configdata as configdata
import wc.log
import wc.i18n
import wc.fileutil

def abspath (path):
    """
    If path is not absolute, make it absolute with sys.prefix.
    """
    if not os.path.isabs(path):
        path = os.path.join(sys.prefix, path)
    return path

# config data
Version = configdata.version
AppName = configdata.appname
Name = configdata.name
Description = configdata.description
App = AppName+u" "+Version
UserAgent = AppName+u"/"+Version
Author =  configdata.author
HtmlAuthor = Author.replace(' ', '&nbsp;')
Copyright = u"Copyright (C) 2000-2005 "+Author
HtmlCopyright = u"Copyright &copy; 2000-2005 "+HtmlAuthor
AppInfo = App+u"              "+Copyright
HtmlAppInfo = App+u", "+HtmlCopyright
Url = configdata.url
Email = configdata.author_email
Freeware = u"""%(appname)s comes with ABSOLUTELY NO WARRANTY!
This is free software, and you are welcome to redistribute it
under certain conditions. Look at the file `LICENSE' whithin this
distribution.""" % {'appname': AppName}
ConfigDir = abspath(configdata.config_dir)
TemplateDir = abspath(configdata.template_dir)
InstallData = abspath(configdata.install_data)
ScriptDir = abspath(configdata.install_scripts)

# optional features
HasSsl = wc.fileutil.has_module("OpenSSL")
HasCrypto = wc.fileutil.has_module("Crypto")
HasPil = wc.fileutil.has_module("PIL")
HasPsyco = wc.fileutil.has_module("psyco")

# logger areas
LOG_FILTER = "wc.filter"
LOG_JS = "wc.filter.js"
LOG_RATING = "wc.filter.rating"
LOG_HTML = "wc.filter.html"
LOG_NET = "wc.net"
LOG_PROXY = "wc.proxy"
LOG_AUTH = "wc.proxy.auth"
LOG_DNS = "wc.proxy.dns"
LOG_GUI = "wc.gui"
LOG_ACCESS = "wc.access"
LOG_TAL = "TAL"
LOG_TALES = "TALES"


def get_locdir ():
    """
    Return locale directory.
    """
    locdir = os.environ.get('LOCPATH')
    if locdir is None:
        locdir = os.path.join(InstallData, 'share', 'locale')
    return locdir


def init_i18n ():
    """
    Deploy i18n gettext method into the default namespace.
    The LOCPATH environment variable is supported.
    """
    wc.i18n.init(configdata.name, get_locdir())

# init i18n on import
wc.init_i18n()

def get_translator (lang, translatorklass=None, fallbackklass=None):
    """
    Return translator class.
    """
    return wc.i18n.get_translator(configdata.name, get_locdir(), [lang],
         translatorklass=translatorklass,
         fallback=True, fallbackklass=fallbackklass)


def iswritable (fname):
    """
    Return True if given file is writable.
    """
    if os.path.isdir(fname) or os.path.islink(fname):
        return False
    try:
        if os.path.exists(fname):
            open(fname, 'a').close()
            return True
        else:
            open(fname, 'w').close()
            os.remove(fname)
            return True
    except IOError:
        pass
    return False


def get_log_file (name, logname, trydirs=None):
    """
    Get full path name to writeable logfile.
    """
    dirs = []
    if os.name == "nt":
        dirs.append(os.environ.get("TEMP"))
    else:
        dirs.append(os.path.join('/', 'var', 'log', name))
        dirs.append(os.path.join('/', 'var', 'tmp', name))
        dirs.append(os.path.join('/', 'tmp', name))
    dirs.append(os.getcwd())
    if trydirs is None:
        trydirs = dirs
    else:
        trydirs.extend(dirs)
    for d in trydirs:
        fullname = os.path.join(d, logname)
        if iswritable(fullname):
            return fullname
    raise IOError, "Could not find writable directory for %s in %s" % \
                   (logname, str(trydirs))


def initlog (filename, appname, filelogs=True):
    """
    Initialize logfiles and configuration.
    """
    logging.config.fileConfig(filename)
    if filelogs:
        trydirs = []
        if os.name == "nt":
            trydirs.append(ConfigDir)
        logname = "%s.log" % appname
        logfile = get_log_file(appname, logname, trydirs=trydirs)
        handler = get_wc_handler(logfile)
        logging.getLogger("wc").addHandler(handler)
        logging.getLogger("TAL").addHandler(handler)
        logging.getLogger("TALES").addHandler(handler)
        # access log is always a file
        logname = "%s-access.log" % appname
        logfile = get_log_file(appname, logname, trydirs=trydirs)
        handler = get_access_handler(logfile)
        logging.getLogger("wc.access").addHandler(handler)


def set_format (handler):
    """
    Set standard format for handler.
    """
    handler.setFormatter(logging.root.handlers[0].formatter)
    return handler


def get_wc_handler (logfile):
    """
    Return a handler for webcleaner logging.
    """
    mode = 'a'
    max_bytes = 1024*1024*2 # 2 MB
    backup_count = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(
                                     logfile, mode, max_bytes, backup_count)
    return set_format(handler)


def get_access_handler (logfile):
    """
    Return a handler for access logging.
    """
    mode = 'a'
    max_bytes = 1024*1024*2 # 2 MB
    backup_count = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(
                                     logfile, mode, max_bytes, backup_count)
    # log only the message
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def sort_seq (seq):
    """
    Return sorted list of given sequence.
    """
    l = list(seq)
    l.sort()
    return l


def restart ():
    """
    Restart the webcleaner proxy.
    """
    if os.name == 'nt':
        py_exe = os.path.join(sys.prefix, "pythonw.exe")
    else:
        py_exe = sys.executable
    script = os.path.join(wc.ScriptDir, "webcleaner")
    wc.log.info(LOG_PROXY, "Restarting with: %s %s restart", py_exe, script)
    os.spawnl(os.P_NOWAIT, py_exe, py_exe, script, "restart")
