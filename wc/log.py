"""logging and debug functions. Note: we always generate handlers for
logging. Look in logging.conf if you want to customize their behaviour
(eg. setting access loglevel to ERROR to turn off access logging"""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003  Bastian Kleineidam
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

# public api
__all__ = ["WC", "FILTER", "PROXY", "PARSER", "GUI", "DNS", "ACCESS", "PICS",
           "debug", "info", "warn", "error", "critical", "exception",
           "initlog", "blocktext"]
__author__  = "Bastian Kleineidam <calvin@users.sf.net>"
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import sys, os, re, logging, logging.config, textwrap
from logging.handlers import RotatingFileHandler
try:
    from wc import ConfigDir, Name, iswriteable
except ImportError:
    sys.path.append(os.getcwd())
    from wc import ConfigDir, Name, iswriteable


def initlog (filename):
    """initialize logfiles and configuration"""
    logging.config.fileConfig(filename)
    logging.getLogger("root").addHandler(get_root_handler())
    wc_handler = get_wc_handler()
    logging.getLogger("wc").addHandler(wc_handler)
    logging.getLogger("simpleTAL").addHandler(wc_handler)
    logging.getLogger("simpleTALES").addHandler(wc_handler)
    logging.getLogger("wc.access").addHandler(get_access_handler())


def get_root_handler ():
    """return a handler for basic logging"""
    if os.name=="nt":
        from logging.handlers import NTEventLogHandler
        return set_format(NTEventLogHandler(Name))
    logfile = get_log_file("%s.err"%Name)
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    return set_format(handler)


def get_wc_handler ():
    """return a handler for webcleaner logging"""
    if os.name=="nt":
        from logging.handlers import NTEventLogHandler
        return set_format(NTEventLogHandler(Name))
    logfile = get_log_file("%s.log"%Name)
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    return set_format(handler)


def get_access_handler ():
    """return a handler for access logging"""
    logfile = get_log_file("%s-access.log"%Name)
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    # log only the message
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def get_log_file (fname):
    """get full path name to writeable logfile"""
    if os.name =='nt':
        return os.path.join(os.environ.get("TEMP"), fname)
    logfile = os.path.join('/var/log', fname)
    if not iswriteable(logfile):
        logfile = os.path.join(os.getcwd(), fname)
    if not iswriteable(logfile):
        logfile = os.path.join('/var/tmp', fname)
    if not iswriteable(logfile):
        logfile = os.path.join('/tmp', fname)
    return logfile


def set_format (handler):
    """set standard format for handler"""
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    return handler


# logger areas
WC = "wc"
FILTER = "wc.filter"
PARSER = "wc.parser"
PROXY = "wc.proxy"
GUI = "wc.gui"
DNS = "wc.dns"
ACCESS = "wc.access"
PICS = "wc.pics"

def debug (log, msg, *args):
    logging.getLogger(log).debug(msg, *args)

def info (log, msg, *args):
    logging.getLogger(log).info(msg, *args)

def warn (log, msg, *args):
    logging.getLogger(log).warn(msg, *args)

def error (log, msg, *args):
    logging.getLogger(log).error(msg, *args)

def critical (log, msg, *args):
    logging.getLogger(log).critical(msg, *args)

def exception (log, msg, *args):
    logging.getLogger(log).exception(msg, *args)


################### text utility functions ###############


def blocktext (s, width):
    return textwrap.fill(s, width)


def blocktext2 (s, width):
    """Adjust lines of s to be not wider than width and fill up
    the lines to maximal length.
    We leave Returns if the previous sentence ended with a punctuation.
    We leave the entire paragraph as is if it begins with "!" (but we
    cut the "!").
    """
    # split into lines
    s = s.split("\n")
    ret = ""
    cache = ""
    verbatim = 0
    for line in s:
        if not line.strip():
            ret += cache+"\n"
            cache = ""
            verbatim = 0
        elif verbatim:
            ret += "\n"+line
        #elif re.compile("^!").match(line) and not verbatim:
        #    ret = ret+cache+"\n"+line[1:]
        #    cache = ""
        #    verbatim = 1
        #elif re.compile(r"^(>|\d\)|o\s+)").match(line):
        #    ret = ret+cache+"\n"+line
        #    cache = ""
        else:
            if cache:
                cache += \
                    ((cache[-1] in ['.','!',',','?']) and "\n" or " ") + \
	            line.strip()
            else:
                cache = "\n"+line
            while len(cache) > width:
                j = get_last_word_boundary(cache, width)
                ret += cache[:j].strip() + "\n"
                cache = cache[j:].strip()
    return ret+cache


def get_last_word_boundary (s, width):
    """Get maximal index i of a whitespace char in s with 0 < i < width.
    Note: if s contains no whitespace this returns width-1"""
    match = re.compile(".*\s").match(s[0:width])
    if match:
        return match.end()
    return width-1


if __name__=='__main__':
    _test()
