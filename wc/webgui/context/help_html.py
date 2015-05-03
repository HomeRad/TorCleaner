# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2009 Bastian Kleineidam
"""
Parameters for help.html page.
"""

from wc import AppName, Version
from wc.configuration import config

port = config.get('port', 8080)
