"""support for different HTTP proxy authentication schemes"""
from wc import config
from basic import get_basic_challenge, check_basic_auth

def get_proxy_auth_challenge ():
    """return initial challenge token for WebCleaner proxy authentication
       Note that HTTP/1.1 allows multiple authentication challenges
       separated by commas (",")"""
    # XXX add digest and NTLM
    return "%s" % (get_basic_challenge(),)


def check_proxy_auth (auth):
    if auth.startswith("Basic "):
        return check_basic_auth(auth, config['proxyuser'],
                                config['proxypass'])
    #elif auth.startswith("Digest "):
    #    return check_proxy_auth_digest(auth)
    #elif auth.startswith("NTLM "):
    #    return check_proxy_auth_ntlm(auth)
    else:
        # unsupported proxy authorization scheme
        return get_proxy_auth_challenge()


