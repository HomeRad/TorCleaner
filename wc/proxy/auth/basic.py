"""support for Basic HTTP proxy authentication"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import base64
from wc.log import *

def get_basic_challenge ():
    """return initial challenge token for basic authentication"""
    return 'Basic realm="unknown"'


def get_basic_proxy_auth (proxyuser, proxypass_b64):
    proxypass = base64.decodestring(proxypass_b64)
    auth = base64.encodestring("%s:%s"%(proxyuser, proxypass)).strip()
    return "Basic %s"%auth


def check_basic_proxy_auth (auth, proxyuser, proxypass_b64):
    """check a base64-encoded auth token against the given user and
       pass. The pass is also base64-encoded.
       returns None if authentication succeded, a new challenge if not
    """
    proxypass = base64.decodestring(proxypass_b64)
    auth = base64.decodestring(auth[6:])
    if ':' not in auth:
        warn(PROXY, "invalid proxy authorization")
        return get_basic_challenge()
    _user, _pass = auth.split(":", 1)
    if _user!=proxyuser:
        warn(PROXY, "failed proxy authorization")
        return get_basic_challenge()
    if _pass!=proxypass:
        warn(PROXY, "failed proxy authorization")
        return get_basic_challenge()
    return None

