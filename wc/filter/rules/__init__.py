"""configuration classes for all available filter modules."""
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2003  Bastian Kleineidam
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

# global counter in case the .zap rules dont yet have the oid entry
oidcounter = 1

_rules_without_sid = []
_sids = Set()
_sidcounter = 0

def register_rule (rule):
    _rules_without_sid.append(rule)


def register_sid (sid):
    _sids.add(sid)


def has_sid (sid):
    return sid in _sids


def generate_sids (prefix="wc"):
    for rule in _rules_without_sid:
        rule.sid = generate_unique_sid(prefix)
    del _rules_without_sid[:]


def generate_unique_sid (prefix):
    sid = generate_sid(prefix)
    while has_sid(sid):
        sid = generate_sid(prefix)
    register_sid(sid)
    return sid


def generate_sid (prefix):
    global _sidcounter
    _sidcounter += 1
    return "%s.%d" % (prefix, _sidcounter)
