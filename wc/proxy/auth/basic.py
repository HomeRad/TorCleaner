# -*- coding: iso-8859-1 -*-
"""HTTP basic authentication routines"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

__all__ = ["get_basic_challenge", "parse_basic_challenge",
           "get_basic_credentials", "parse_basic_credentials",
           "check_basic_credentials"]
import base64
from wc.log import *
# wc_realm is the default realm
from wc.proxy.auth import wc_realm
from parse import *

def get_basic_challenge ():
    """return initial challenge token for basic authentication"""
    return 'Basic realm="%s"' % wc_realm


def parse_basic_challenge (challenge):
    """parse basic authentication challenge, return dict with
       challenge data"""
    return parse_auth({}, challenge)


def get_basic_credentials (challenge, **attrs):
    """return basic credential string for given challenge"""
    password = base64.decodestring(attrs['password_b64'])
    username = attrs['username']
    auth = base64.encodestring("%s:%s"%(username, password)).strip()
    return "Basic %s"%auth


def parse_basic_credentials (credentials):
    """parse basic authentication credentials, return dict with credentials"""
    auth, credentials = parse_token(credentials, more_chars="=")
    auth = base64.decodestring(auth)
    if ':' not in auth:
        warn(AUTH, "invalid Basic credentials %s", auth)
        _user, _pw = auth, ''
    else:
        _user, _pw = auth.split(':', 1)
    return {'username': _user, 'password': _pw}, credentials.strip()


def check_basic_credentials (cred, **attrs):
    """return True if authentication succeded, else False"""
    password = base64.decodestring(attrs['password_b64'])
    username = attrs['username']
    return cred['username']==username and cred['password']==password

