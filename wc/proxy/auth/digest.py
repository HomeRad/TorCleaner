# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import md5, sha, random, base64, time
from parse import *
random.seed()
# the default realm
from wc.proxy.auth import wc_realm
# the default opaque value
wc_opaque = base64.encodestring("unknown").strip()
# nonce dictionary
# XXX regularly delete nonces
nonces = {}


def get_digest_challenge (stale=False):
    """return initial challenge token for digest authentication"""
    realm = wc_realm
    nonce = encode_digest("%f:%f" % (time.time(), random.random()))
    assert nonce not in nonces
    nonces[nonce] = None
    opaque = wc_opaque
    auth = 'realm="%(realm)s", nonce="%(nonce)s", opaque="%(opaque)s"' % \
           locals()
    if stale:
        auth += ', stale=true'
    return "Digest %s"%auth


def parse_digest_challenge (challenge):
    return parse_auth({'stale': False, 'algorithm': 'MD5'}, challenge)


def parse_digest_credentials (credentials):
    return parse_auth({'algorithm': 'MD5'}, credentials)


def check_digest_credentials (credentials, **attrs):
    # XXX not working???
    opaque = credentials.get("opaque", "")
    if opaque!=wc_opaque:
        return False
    realm = credentials.get("realm", "")
    if realm!=wc_realm:
        return False
    nonce = credentials.get("nonce", "")
    if nonce not in nonces:
        return False
    nonces.clear()
    username = attrs['username']
    password = base64.decodestring(attrs['password_b64'])
    uri = attrs['uri']
    method = attrs['method']
    data = attrs.get('data')
    response = credentials.get('response', '')
    algorithm = credentials.get('algorithm', 'MD5')
    H, KD = get_algorithm_impls(algorithm)
    if H is None:
        return False
    # XXX MD5-sess
    A1 = "%s:%s:%s" % (username, realm, password)
    A2 = "%s:%s" % (method, uri)
    respdig = KD(H(A1), "%s:%s" % (nonce, H(A2)))
    return response==respdig


def get_digest_credentials (challenge, **attrs):
    """return digest credentials for given challenge"""
    username = attrs['username']
    password = base64.decodestring(attrs['password_b64'])
    uri = attrs['uri']
    method = attrs['method']
    data = attrs.get('data')
    try:
        realm = challenge['realm']
        nonce = challenge['nonce']
        algorithm = challenge.get('algorithm', 'MD5')
        # mod_digest doesn't send an opaque, even though it isn't
        # supposed to be optional
        opaque = challenge.get('opaque', None)
    except KeyError:
        return None

    H, KD = get_algorithm_impls(algorithm)
    if H is None:
        return None

    # XXX not implemented yet
    if data:
        entdig = get_entity_digest(data, challenge)
    else:
        entdig = None

    # XXX MD5-sess
    A1 = "%s:%s:%s" % (username, realm, password)
    A2 = "%s:%s" % (method, uri)
    respdig = KD(H(A1), "%s:%s" % (nonce, H(A2)))
    # XXX should the partial digests be encoded too?

    base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
           'response="%s"' % (username, realm, nonce, uri, respdig)
    if opaque:
        base += ', opaque="%s"' % opaque
    if entdig:
        base += ', digest="%s"' % entdig
    if algorithm != 'MD5':
        base += ', algorithm="%s"' % algorithm
    return "Digest %s" % base


def get_algorithm_impls (algorithm):
    # lambdas assume digest modules are imported at the top level
    if algorithm in ('MD5', 'MD5-sess'):
        H = lambda x, e=encode_digest:e(md5.new(x).digest())
    elif algorithm == 'SHA':
        H = lambda x, e=encode_digest:e(sha.new(x).digest())
    KD = lambda s, d, H=H: H("%s:%s" % (s, d))
    return H, KD


def get_entity_digest(data, chal):
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

