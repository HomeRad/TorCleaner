# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
HTTP digest authentication routines.
"""

__all__ = ["get_digest_challenge", "parse_digest_challenge",
           "get_digest_credentials", "parse_digest_credentials",
           "check_digest_credentials"]

import md5
import sha
import random
import base64
import time

from parse import parse_auth

import wc
import wc.log
# the default realm
from wc.proxy.auth import wc_realm


random.seed()
# the default opaque value
wc_opaque = base64.b64encode("unknown")
# XXX regularly delete all old nonces
nonces = {} # nonce to timestamp
max_noncesecs = 2*60*60 # max. lifetime of a nonce is 2 hours (and 5 minutes)


def check_nonces ():
    """
    Deprecate old digest nonces.
    """
    todelete = []
    for nonce, value in nonces.items():
        noncetime = time.time() - value
        if noncetime > max_noncesecs:
            todelete.append(nonce)
    for nonce in todelete:
        del nonces[nonce]
    make_timer(300, check_nonces)


def get_digest_challenge (stale="false"):
    """
    Return initial challenge token for digest authentication.
    """
    realm = wc_realm
    nonce = encode_digest("%f:%f" % (time.time(), random.random()))
    assert nonce not in nonces
    nonces[nonce] = time.time()
    opaque = wc_opaque
    auth = 'realm="%s", nonce="%s", opaque="%s", stale=%s' % \
           (realm, nonce, opaque, stale)
    return "Digest %s" % auth


def parse_digest_challenge (challenge):
    """
    Parse a digest challenge into a dictionary.
    """
    return parse_auth({}, challenge)


def parse_digest_credentials (credentials):
    """
    Parse digest credentials into a dictionary.
    """
    return parse_auth({}, credentials)


def check_digest_credentials (credentials, **attrs):
    """
    Check digest credentials.
    """
    if not check_digest_values(credentials):
        wc.log.warn(wc.LOG_AUTH, "digest wrong values")
        return False
    # note: opaque value _should_ be there, but is not in apache mod_digest
    opaque = credentials.get("opaque")
    if opaque != wc_opaque:
        wc.log.warn(wc.LOG_AUTH, "digest wrong opaque %s!=%s",
                    opaque, wc_opaque)
        return False
    realm = credentials["realm"]
    if realm != wc_realm:
        wc.log.warn(wc.LOG_AUTH, "digest wrong realm %s!=%s", realm, wc_realm)
        return False
    nonce = credentials["nonce"]
    if nonce not in nonces:
        wc.log.warn(wc.LOG_AUTH, "digest wrong nonce %s", nonce)
        return False
    uri = credentials['uri']
    if uri != attrs['uri']:
        wc.log.warn(wc.LOG_AUTH, "digest wrong uri %s!=%s", uri, attrs['uri'])
        return False
    # compare responses
    response = credentials.get('response')
    our_response = get_response_digest(credentials, **attrs)[2]
    if response != our_response:
        assert wc.log.debug(wc.LOG_AUTH, "digest wrong response %s!=%s",
                     response, our_response)
        return False
    return True


def check_digest_values (auth):
    """
    Check basic digest values on vadility; auth can be a parsed
    challenge or credential.
    """
    # check data
    if auth.get('algorithm') not in ("MD5", "MD5-sess", "SHA", None):
        wc.log.error(wc.LOG_AUTH, "unsupported digest algorithm value %r",
                     auth['algorithm'])
        return False
    if auth.get('qop') not in ("auth", "auth-int", None):
        wc.log.error(wc.LOG_AUTH, "unsupported digest qop value %r",
                     auth['qop'])
        return False
    for key in ('realm', 'nonce'):
        if key not in auth:
            wc.log.error(wc.LOG_AUTH, "missing digest challenge value for %r",
                         key)
            return False
    return True


def get_digest_credentials (challenge, **attrs):
    """
    Return digest credentials for given challenge.
    """
    if not check_digest_values(challenge):
        return None
    # calculate response digest
    try:
        password = base64.b64decode(attrs['password_b64'])
    except TypeError:
        wc.log.warn(wc.LOG_AUTH, "bad encoded password at %r", attrs['uri'])
        password = ""
    nc, cnonce, response_digest = get_response_digest(challenge, **attrs)
    # construct credentials
    base = 'username="%s", realm="%s", nonce="%s", uri="%s"' % \
             (attrs['username'], challenge['realm'], challenge['nonce'],
              attrs['uri'])
    base += ', algorithm="%s"' % challenge.get('algorithm', 'MD5')
    base += ', response="%s"' % response_digest
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
    """
    Calculate the response digest.
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
    elif algorithm == 'SHA':
        H = lambda x: sha.new(x).digest()
    data = attrs.get('data')
    if data:
        # XXX POST data digest not implemented yet
        entdig = get_entity_digest(data, challenge)
        assert attrs['method'] == "POST"
    else:
        entdig = None
    # calculate H(A1)
    username = attrs['username']
    try:
        password = base64.b64decode(attrs['password_b64'])
    except TypeError:
        wc.log.warn(wc.LOG_AUTH, "bad encoded password at %r", attrs['uri'])
        password = ""
    A1 = "%s:%s:%s" % (username, challenge['realm'], password)
    HA1 = encode_digest(H(A1))
    if algorithm == 'MD5-sess':
        cnonce = get_cnonce()
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
    """
    Return 16 random hex characters.
    """
    return "".join([ _hexchars[random.randint(0, 15)] for _ in range(16) ])


_nonce_count = 0
def get_nonce_count ():
    """
    Increment nonce count and return it as formatted string.
    """
    global _nonce_count
    _nonce_count += 1
    return "%08d" % _nonce_count


def get_entity_digest (data, chal):
    """
    XXX not implemented yet, returns None.
    """
    return None


def encode_digest (digest):
    """
    Encode given digest in hexadecimal representation and return it.
    """
    hexrep = []
    for c in digest:
        n = (ord(c) >> 4) & 0xf
        hexrep.append(hex(n)[-1])
        n = ord(c) & 0xf
        hexrep.append(hex(n)[-1])
    return ''.join(hexrep)


from wc.proxy import make_timer
def init ():
    """
    Check for timed out nonces every 5 minutes.
    """
    make_timer(300, check_nonces)
