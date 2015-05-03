# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Hold a list of urls to block in external file, like those
found in SquidGuard.
"""
from . import ExternfileRule


class BlockurlsRule(ExternfileRule.ExternfileRule):
    """
    Specifies a list of url paths to block, displaying the standard
    block message page.
    See also the Blocker filter module.
    """
    pass
