"""logging and debug functions"""
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
__all__ = ["WC", "FILTER", "PROXY", "PARSER", "GUI", "DNS", "ACCESS",
           "debug", "info", "warn", "error", "critical", "exception"]

from wc import ConfigDir
import os, logging, logging.config
logging.config.fileConfig(os.path.join(ConfigDir, "logging.conf"))

# logger areas
WC = "wc"
FILTER = "wc.filter"
PARSER = "wc.parser"
PROXY = "wc.proxy"
GUI = "wc.gui"
DNS = "wc.dns"
ACCESS = "wc.access"

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

