# -*- coding: iso-8859-1 -*-
"""configuration classes for all available filter modules."""
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

from sets import Set

_rules_without_sid = []
_sids = Set()
_sidcounter = 0

def register_rule (rule):
    if rule.sid is None:
        _rules_without_sid.append(rule)
    else:
        register_sid(rule.sid)


def register_sid (sid):
    assert sid not in _sids, "%s is not a unique id"%sid
    _sids.add(sid)
    return sid


def delete_registered_sids ():
    _sids.clear()


def has_sid (sid):
    return sid in _sids


def generate_sids (prefix):
    for rule in _rules_without_sid:
        rule.sid = generate_unique_sid(prefix)
    del _rules_without_sid[:]


def generate_unique_sid (prefix):
    sid = generate_sid(prefix)
    while has_sid(sid):
        sid = generate_sid(prefix)
    return register_sid(sid)


def generate_sid (prefix):
    global _sidcounter
    _sidcounter += 1
    return "%s.%d" % (prefix, _sidcounter)


from AllowRule import *
from AllowdomainsRule import *
from AllowurlsRule import *
from BlockRule import *
from BlockdomainsRule import *
from BlockurlsRule import *
from ExternfileRule import *
from FolderRule import *
from HeaderRule import *
from ImageRule import *
from JavascriptRule import *
from NocommentsRule import *
from RatingRule import *
from ReplaceRule import *
from RewriteRule import *
from UrlRule import *
