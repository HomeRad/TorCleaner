# -*- coding: iso-8859-1 -*-
"""logging and debug functions. Note: we always generate handlers for
logging. Look in logging.conf if you want to customize their behaviour
(eg. setting access loglevel to ERROR to turn off access logging"""
# Copyright (C) 2003-2004  Bastian Kleineidam
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
__all__ = ["FILTER", "PROXY", "GUI", "DNS", "ACCESS", "RATING", "AUTH",
           "CONNECTION", "debug", "info", "warn", "error", "critical",
           "exception", "initlog", "set_format", "usedmemory"]
__author__  = "Bastian Kleineidam <calvin@users.sf.net>"
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import os
import logging
import logging.config
import logging.handlers
import wc


# logger areas
FILTER = "wc.filter"
CONNECTION = "wc.connection"
PROXY = "wc.proxy"
AUTH = "wc.proxy.auth"
DNS = "wc.proxy.dns"
GUI = "wc.gui"
ACCESS = "wc.access"
RATING = "wc.rating"


def initlog (filename):
    """initialize logfiles and configuration"""
    logging.config.fileConfig(filename)
    if os.name=='nt':
        # log to event log
        #from logging.handlers import NTEventLogHandler
        #handler = set_format(NTEventLogHandler(wc.Name))
        # log to file
        logfile = get_log_file("%s.log"%wc.Name)
        handler = get_wc_handler(logfile)
    else:
        # log to file
        logfile = get_log_file("%s.log"%wc.Name)
        handler = get_wc_handler(logfile)
    logging.getLogger("wc").addHandler(handler)
    logging.getLogger("simpleTAL").addHandler(handler)
    logging.getLogger("simpleTALES").addHandler(handler)
    # access log is always a file
    logfile = get_log_file("%s-access.log"%wc.Name)
    handler = get_access_handler(logfile)
    logging.getLogger("wc.access").addHandler(handler)


def get_wc_handler (logfile):
    """return a handler for webcleaner logging"""
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    return set_format(handler)


def get_access_handler (logfile):
    """return a handler for access logging"""
    mode = 'a'
    maxBytes = 1024*1024*2 # 2 MB
    backupCount = 5 # number of files to generate
    handler = logging.handlers.RotatingFileHandler(logfile, mode, maxBytes, backupCount)
    # log only the message
    handler.setFormatter(logging.Formatter("%(message)s"))
    return handler


def get_log_file (fname, trydir=os.getcwd()):
    """get full path name to writeable logfile"""
    if os.name =='nt':
        return _get_log_file_nt(fname, trydir)
    return _get_log_file_posix(fname, trydir)


def _get_log_file_posix (fname, trydir):
    """get full path name to writeable logfile on posix systems"""
    logfile = os.path.join('/', 'var', 'log', 'webcleaner', fname)
    if not wc.iswriteable(logfile):
        logfile = os.path.join(trydir, fname)
    if not wc.iswriteable(logfile):
        logfile = os.path.join('/', 'var', 'tmp', fname)
    if not wc.iswriteable(logfile):
        logfile = os.path.join('/','tmp', fname)
    return logfile


def _get_log_file_nt (fname, trydir):
    """get full path name to writeable logfile on Windows systems"""
    logfile = os.path.join(wc.ConfigDir, fname)
    if not wc.iswriteable(logfile):
        logfile = os.path.join(trydir, fname)
    if not wc.iswriteable(logfile):
        logfile = os.path.join(os.environ.get("TEMP"), fname)
    return logfile


def set_format (handler):
    """set standard format for handler"""
    handler.setFormatter(logging.root.handlers[0].formatter)
    return handler


import gc
gc.enable()
# memory leak debugging
#gc.set_debug(gc.DEBUG_LEAK)
def debug (log, msg, *args):
    """log a debug message"""
    logging.getLogger(log).debug(msg, *args)
    #logging.getLogger(log).info("Mem: %d kB"%usedmemory())


def usedmemory ():
    """return string with used memory"""
    pid = os.getpid()
    fp = file('/proc/%d/status'%pid)
    val = 0
    try:
        for line in fp.readlines():
            if line.startswith('VmRSS:'):
                val = int(line[6:].strip().split()[0])
    finally:
        fp.close()
    return val


def info (log, msg, *args):
    """log in informational message"""
    logging.getLogger(log).info(msg, *args)


def warn (log, msg, *args):
    """log a warning"""
    logging.getLogger(log).warn(msg, *args)


def error (log, msg, *args):
    """log an error"""
    logging.getLogger(log).error(msg, *args)


def critical (log, msg, *args):
    """log a critical error"""
    logging.getLogger(log).critical(msg, *args)


def exception (log, msg, *args):
    """log an exception"""
    logging.getLogger(log).exception(msg, *args)
