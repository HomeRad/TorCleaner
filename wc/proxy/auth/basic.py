"""support for Basic HTTP proxy authentication"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from base64 import decodestring as base64decode

def get_basic_challenge ():
    """return initial challenge token for basic authentication"""
    return 'Basic realm="unknown"'


def check_basic_auth (auth, authuser, authpass_b64):
    """check a base64-encoded auth token against the given user and
       pass. The pass is also base64-encoded.
       returns None if authentication succeded, a new challenge if not
    """
    auth = base64decode(auth[6:])
    if ':' not in auth:
        return get_basic_challenge()
    _user,_pass = auth.split(":", 1)
    if _user!=authuser:
        return get_basic_challenge()
    if authpass and _pass!=base64decode(authpass_b64):
        return get_basic_challenge()
    return None

