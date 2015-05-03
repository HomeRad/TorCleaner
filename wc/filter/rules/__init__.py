# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Rule objects representing configured filter rules.
"""

_rules_without_sid = []
_sids = set()
_sidcounter = 0

def register_rule(rule):
    """
    Register given rule to internal rule id list.
    """
    if rule.sid is None:
        _rules_without_sid.append(rule)
    else:
        register_sid(rule.sid)


def register_sid(sid):
    """
    Register given sequential id in id list.
    """
    assert sid not in _sids, "%s is not a unique id" % sid
    _sids.add(sid)
    return sid


def delete_registered_sids():
    """
    Clear registered id list.
    """
    _sids.clear()


def has_sid(sid):
    """
    Return True if given id is registered.
    """
    return sid in _sids


def generate_sids(prefix):
    """
    Add missing ids with given prefix to rules.
    """
    for rule in _rules_without_sid:
        rule.sid = generate_unique_sid(prefix)
    del _rules_without_sid[:]


def generate_unique_sid(prefix):
    """
    Generate a unique id with given prefix.
    """
    sid = generate_sid(prefix)
    while has_sid(sid):
        sid = generate_sid(prefix)
    return register_sid(sid)


def generate_sid(prefix):
    """
    Generate an id with given prefix.
    """
    global _sidcounter
    _sidcounter += 1
    return "%s.%d" % (prefix, _sidcounter)
