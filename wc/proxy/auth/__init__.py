# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
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
Support for different HTTP proxy authentication schemes.
"""

# default realm for authentication
wc_realm = "unknown"

from ... import log, LOG_AUTH, configuration, url as urlutil, HasCrypto

from basic import parse_basic_challenge, get_basic_challenge
from basic import parse_basic_credentials, get_basic_credentials
from basic import check_basic_credentials
from digest import parse_digest_challenge, get_digest_challenge
from digest import parse_digest_credentials, get_digest_credentials
from digest import check_digest_credentials
if HasCrypto:
    from ntlm import parse_ntlm_challenge, get_ntlm_challenge
    from ntlm import parse_ntlm_credentials, get_ntlm_credentials
    from ntlm import check_ntlm_credentials


def get_auth_uri (url):
    """
    Return uri ready for authentication purposes.
    """
    return urlutil.stripsite(url)[1]


def get_header_challenges (headers, key):
    """
    Get parsed challenge(s) out of headers[key].
    """
    auths = {}
    for auth in headers.getheaders(key):
        log.debug(LOG_AUTH, "%s header challenge: %s", key, auth)
        for key, data in parse_challenges(auth).iteritems():
            auths.setdefault(key, []).extend(data)
    log.debug(LOG_AUTH, "parsed challenges: %s", auths)
    return auths


def parse_challenges (challenge):
    """
    Return a parsed challenge dict.
    """
    auths = {}
    while challenge:
        if challenge.startswith('Basic'):
            auth, challenge = parse_basic_challenge(challenge[5:].strip())
            auths.setdefault('Basic', []).append(auth)
        elif challenge.startswith('Digest'):
            auth, challenge = parse_digest_challenge(challenge[6:].strip())
            auths.setdefault('Digest', []).append(auth)
        elif challenge.startswith('NTLM') and HasCrypto:
            auth, challenge = parse_ntlm_challenge(challenge[4:].strip())
            auths.setdefault('NTLM', []).append(auth)
        else:
            auth, challenge = challenge, None
            auths.setdefault('unknown', []).append(auth)
    return auths


def get_challenges (**args):
    """
    Return list of challenges for WebCleaner proxy authentication
    Note that HTTP/1.1 allows multiple authentication challenges
    either as multiple headers with the same key, or as one single
    header whose value list is separated by commas.
    """
    if configuration.config['auth_ntlm'] and HasCrypto:
        chals = [get_ntlm_challenge(**args)]
    else:
        chals = [
            get_basic_challenge(),
            get_digest_challenge(),
        ]
    log.debug(LOG_AUTH, "challenges %s", chals)
    return chals


def get_header_credentials (headers, key):
    """
    Return parsed credentials out of headers[key].
    """
    creds = {}
    for cred in headers.getheaders(key):
        log.debug(LOG_AUTH, "%s header credential: %s", key, cred)
        for key, data in parse_credentials(cred).iteritems():
            creds.setdefault(key, []).extend(data)
    log.debug(LOG_AUTH, "parsed credentials: %s", creds)
    return creds


def parse_credentials (creds):
    """
    Return a parsed credential dict.
    """
    auths = {}
    while creds:
        if creds.startswith('Basic'):
            auth, creds = parse_basic_credentials(creds[5:].strip())
            auths.setdefault('Basic', []).append(auth)
        elif creds.startswith('Digest'):
            auth, creds = parse_digest_credentials(creds[6:].strip())
            auths.setdefault('Digest', []).append(auth)
        elif creds.startswith('NTLM') and HasCrypto:
            auth, creds = parse_ntlm_credentials(creds[4:].strip())
            auths.setdefault('NTLM', []).append(auth)
        else:
            auth, creds = creds, None
            auths.setdefault('unknown', []).append(auth)
    return auths


def get_credentials (challenges, **attrs):
    """
    Craft a challenge response with credential data.

    @return: a challenge response with supported authentication scheme,
             or None on error or if scheme is unsupported.
    """
    if 'NTLM' in challenges and \
       configuration.config['auth_ntlm'] and HasCrypto:
        creds = get_ntlm_credentials(challenges['NTLM'][0], **attrs)
    elif 'Digest' in challenges:
        creds = get_digest_credentials(challenges['Digest'][0], **attrs)
    elif 'Basic' in challenges:
        creds = get_basic_credentials(challenges['Basic'][0], **attrs)
    else:
        creds = None
    log.debug(LOG_AUTH, "credentials: %s", creds)
    return creds


def check_credentials (creds, **attrs):
    """
    Check credentials against given attributes.
    """
    log.debug(LOG_AUTH,
        "check credentials %s with attrs %s", creds, attrs)
    if not creds:
        res = False
    elif configuration.config['auth_ntlm'] and 'NTLM' not in creds:
        # forced NTLM auth
        res = False
    elif 'NTLM' in creds and HasCrypto:
        res = check_ntlm_credentials(creds['NTLM'][0], **attrs)
    elif 'Digest' in creds:
        res = check_digest_credentials(creds['Digest'][0], **attrs)
    elif 'Basic' in creds:
        res = check_basic_credentials(creds['Basic'][0], **attrs)
    else:
        log.error(LOG_AUTH, "Unknown authentication credentials %s",
                     creds)
        res = False
    return res
