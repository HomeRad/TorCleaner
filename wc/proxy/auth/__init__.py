"""support for different HTTP proxy authentication schemes"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc import config
from wc.log import *
from basic import *

def get_proxy_auth_challenge ():
    """return initial challenge token for WebCleaner proxy authentication
       Note that HTTP/1.1 allows multiple authentication challenges
       separated by commas (",")"""
    # XXX add digest and NTLM
    return "%s" % (get_basic_challenge(),)


def get_proxy_auth (_user, _password):
    return get_basic_proxy_auth(_user, _password)


def check_proxy_auth (auth):
    if auth.startswith("Basic "):
        return check_basic_proxy_auth(auth, config['proxyuser'],
                                      config['proxypass'])
    #elif auth.startswith("Digest "):
    #    return check_proxy_auth_digest(auth)
    #elif auth.startswith("NTLM "):
    #    return check_proxy_auth_ntlm(auth)
    else:
        # unsupported proxy authorization scheme
        warn(PROXY, "Unsupported proxy authorization %s", `auth`)
        return get_proxy_auth_challenge()


