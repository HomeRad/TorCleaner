# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Hold a list of urls to allow in external file, like those
found in SquidGuard.
"""

from . import ExternfileRule


class AllowurlsRule(ExternfileRule.ExternfileRule):
    """
    Specifies a list of url paths to allow, even if they would be blocked
    otherwise.
    See also the Blocker filter module.
    """
    pass
