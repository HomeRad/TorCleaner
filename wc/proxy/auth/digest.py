__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

def get_digest_challenge ():
    """return initial challenge token for digest authentication"""
    #'Digest realm="unknown" qop="%s" nonce="%s" opque="%s"'
    pass # XXX


def check_proxy_auth_digest (self, auth):
    # XXX
    return 'Digest realm="unknown"'


