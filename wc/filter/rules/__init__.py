# -*- coding: iso-8859-1 -*-
"""Rule objects represent configured filter rules"""
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

import sets

_rules_without_sid = []
_sids = sets.Set()
_sidcounter = 0

def register_rule (rule):
    """register given rule to internal rule id list"""
    if rule.sid is None:
        _rules_without_sid.append(rule)
    else:
        register_sid(rule.sid)


def register_sid (sid):
    """register given sequential id in id list"""
    assert sid not in _sids, "%s is not a unique id"%sid
    _sids.add(sid)
    return sid


def delete_registered_sids ():
    """clear registered id list"""
    _sids.clear()


def has_sid (sid):
    """return True if given id is registered"""
    return sid in _sids


def generate_sids (prefix):
    """add missing ids with given prefix to rules"""
    for rule in _rules_without_sid:
        rule.sid = generate_unique_sid(prefix)
    del _rules_without_sid[:]


def generate_unique_sid (prefix):
    """generate a unique id with given prefix"""
    sid = generate_sid(prefix)
    while has_sid(sid):
        sid = generate_sid(prefix)
    return register_sid(sid)


def generate_sid (prefix):
    """generate an id with given prefix"""
    global _sidcounter
    _sidcounter += 1
    return "%s.%d" % (prefix, _sidcounter)

