# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2008 Bastian Kleineidam
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
"""
HTTP basic authentication routines.
"""

__all__ = ["get_basic_challenge", "parse_basic_challenge",
           "get_basic_credentials", "parse_basic_credentials",
           "check_basic_credentials"]
import base64
from ... import log, LOG_AUTH
# wc_realm is the default realm
from . import wc_realm
from .parse import parse_token, parse_auth

def get_basic_challenge ():
    """
    Return initial challenge token for basic authentication.
    """
    return 'Basic realm="%s"' % wc_realm


def parse_basic_challenge (challenge):
    """
    Parse basic authentication challenge, return dict with
    challenge data.
    """
    return parse_auth({}, challenge)


def get_basic_credentials (challenge, **attrs):
    """
    Return basic credential string for given challenge.
    """
    password = base64.decodestring(attrs['password_b64'])
    username = attrs['username']
    auth = base64.encodestring("%s:%s"%(username, password)).strip()
    return "Basic %s" % auth


def parse_basic_credentials (credentials):
    """
    Parse basic authentication credentials, return dict with credentials.
    """
    auth, credentials = parse_token(credentials, more_chars="=")
    auth = base64.decodestring(auth)
    if ':' not in auth:
        log.info(LOG_AUTH, "invalid Basic credentials %s", auth)
        _user, _pw = auth, ''
    else:
        _user, _pw = auth.split(':', 1)
    return {'username': _user, 'password': _pw}, credentials.strip()


def check_basic_credentials (cred, **attrs):
    """
    Return True if authentication succeded, else False.
    """
    password = base64.decodestring(attrs['password_b64'])
    username = attrs['username']
    return cred['username'] == username and cred['password'] == password
