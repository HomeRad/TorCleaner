"""support for Basic HTTP proxy authentication"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import base64

def get_basic_challenge ():
    """return initial challenge token for basic authentication"""
    return 'Basic realm="unknown"'


def check_basic_auth (auth, proxyuser, proxypass_b64):
    """check a base64-encoded auth token against the given user and
       pass. The pass is also base64-encoded.
       returns None if authentication succeded, a new challenge if not
    """
    auth = base64.decodestring(auth[6:])
    if ':' not in auth:
        warn(PROXY, "invalid proxy authorization")
        return get_basic_challenge()
    _user, _pass = auth.split(":", 1)
    if _user!=proxyuser:
        warn(PROXY, "failed proxy authorization")
        return get_basic_challenge()
    if _pass!=base64.decodestring(proxypass_b64):
        warn(PROXY, "failed proxy authorization")
        return get_basic_challenge()
    return None

