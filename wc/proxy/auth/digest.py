# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

__all__ = ["get_digest_challenge", "parse_digest_challenge",
           "get_digest_credentials", "parse_digest_credentials",
           "check_digest_credentials"]

import md5, sha, random, base64, time
from parse import *
random.seed()
# the default realm
from wc.proxy.auth import wc_realm
# the default opaque value
wc_opaque = base64.encodestring("unknown").strip()
# nonce dictionary
# XXX regularly delete all old nonces
nonces = {}


def get_digest_challenge (stale="false"):
    """return initial challenge token for digest authentication"""
    realm = wc_realm
    nonce = encode_digest("%f:%f" % (time.time(), random.random()))
    assert nonce not in nonces
    nonces[nonce] = None
    opaque = wc_opaque
    auth = 'realm="%(realm)s", nonce="%(nonce)s", opaque="%(opaque)s", stale=%(stale)s' % \
           locals()
    return "Digest %s"%auth


def parse_digest_challenge (challenge):
    """parse a digest challenge into a dictionary"""
    return parse_auth({}, challenge)


def parse_digest_credentials (credentials):
    """parse digest credentials into a dictionary"""
    return parse_auth({}, credentials)


def check_digest_credentials (credentials, **attrs):
    """check digest credentials"""
    if not check_digest_values(credentials):
        return False
    # note: opaque value _should_ be there, but is not in apache mod_digest
    if credentials.get("opaque") != wc_opaque:
        return False
    if credentials["realm"] != wc_realm:
        return False
    if credentials["nonce"] not in nonces:
        return False
    # deprecate old nonce
    del nonces[credentials["nonce"]]
    # compare responses
    response = credentials.get('response')
    return response == get_response_digest(credentials, **attrs)


def check_digest_values (auth):
    """check basic digest values on vadility; auth can be a parsed
       challenge or credential"""
    # check data
    if auth.get('algorithm') not in ("MD5", "MD5-sess", "SHA", None):
        error(AUTH, "unsupported digest algorithm value %s", `auth['algorithm']`)
        return False
    if auth.get('qop') not in ("auth", "auth-int", None):
        error(AUTH, "unsupported digest qop value %s", `auth['qop']`)
        return False
    for key in ('realm', 'nonce'):
        if key not in auth:
            error(AUTH, "missing digest challenge value for %s", `key`)
            return False
    return True


def get_digest_credentials (challenge, **attrs):
    """return digest credentials for given challenge"""
    if not check_digest_values(challenge):
        return None
    # calculate reponse digest
    password = base64.decodestring(attrs['password_b64'])
    nc, cnonce, response_digest = get_response_digest(challenge, **attrs)
    # construct credentials
    base = 'username="%s", realm="%s", nonce="%s", uri="%s"' % \
             (attrs['username'], challenge['realm'], challenge['nonce'],
              attrs['uri'])
    if challenge.has_key('algorithm'):
        base += ', algorithm="%s"' % challenge['algorithm']
    base += ", response=\"%s\"" % response_digest
    # note: opaque value _should_ be there, but is not in apache mod_digest
    if challenge.has_key('opaque'):
        base += ', opaque="%s"' % challenge['opaque']
    if challenge.has_key('qop'):
        # Microsoft-IIS implementation requires extra quotes
        if attrs['requireExtraQuotes']:
            base += ", qop=\"%s\"" % challenge['qop']
        else:
            base += ", qop=%s" % challenge['qop']
        base += ", nc=%s" % nc
        base += ", cnonce=\"%s\"" % cnonce
    #if entdig is not None:
    #    base += ', digest="%s"' % entdig
    return "Digest %s" % base


def get_response_digest (challenge, **attrs):
    """Calculate the response digest.
       The get_response_digest function is taken from the following sources
       and falls under their respective licenses:
       - Mozilla browser 1.4, netwerk/protocol/http/src/nsHttpDigestAuth.cpp
       - Python 2.3, urllib2.py
       You'll find both copyrights in the file debian/copyright that
       comes with the WebCleaner source distribution.
    """
    # lambdas assume digest modules are imported at the top level
    algorithm = challenge.get('algorithm', 'MD5')
    if algorithm.startswith('MD5'):
        H = lambda x: md5.new(x).digest()
    elif algorithm=='SHA':
        H = lambda x: sha.new(x).digest()
    # XXX POST data digest not implemented yet
    if attrs.has_key('data'):
        entdig = get_entity_digest(attrs['data'], challenge)
        assert attrs['method'] == "POST"
    else:
        entdig = None
    # calculate H(A1)
    username = attrs['username']
    password = base64.decodestring(attrs['password_b64'])
    A1 = "%s:%s:%s" % (username, challenge['realm'], password)
    HA1 = encode_digest(H(A1))
    if algorithm=='MD5-sess':
        A1 = "%s:%s:%s" % (HA1, challenge['nonce'], cnonce)
        HA1 = encode_digest(H(A1))
    # calculate H(A2)
    A2 = "%s:%s" % (attrs['method'], attrs['uri'])
    qop = challenge.get('qop')
    if qop == "auth-int":
        A2 += ":%s" % entdig
    HA2 = encode_digest(H(A2))
    response_digest = "%s:%s:" % (HA1, challenge['nonce'])
    if qop in ("auth", "auth-int"):
        nc = get_nonce_count()
        cnonce = get_cnonce()
        response_digest += "%s:%s:%s:" % (nc, cnonce, qop)
    else:
        nc = cnonce = None
    response_digest += HA2
    response_digest = encode_digest(H(response_digest))
    return nc, cnonce, response_digest


_hexchars = "0123456789abcdef"
def get_cnonce ():
    """return 16 random hex characters"""
    return "".join([ _hexchars[random.randint(0, 15)] for i in range(16) ])


_nonce_count = 0
def get_nonce_count ():
    global _nonce_count
    _nonce_count += 1
    return "%08d" % _nonce_count


def get_entity_digest (data, chal):
    # XXX not implemented yet
    return None


def encode_digest (digest):
    hexrep = []
    for c in digest:
        n = (ord(c) >> 4) & 0xf
        hexrep.append(hex(n)[-1])
        n = ord(c) & 0xf
        hexrep.append(hex(n)[-1])
    return ''.join(hexrep)

