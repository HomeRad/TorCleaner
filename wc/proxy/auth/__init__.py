# -*- coding: iso-8859-1 -*-
"""support for different HTTP proxy authentication schemes"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.url import stripsite

# default realm for authentication
wc_realm = "unknown"

import wc
from basic import parse_basic_challenge, get_basic_challenge
from basic import parse_basic_credentials, get_basic_credentials
from digest import parse_digest_challenge, get_digest_challenge
from digest import parse_digest_credentials, get_digest_credentials
from ntlm import parse_ntlm_challenge, get_ntlm_challenge
from ntlm import parse_ntlm_credentials, get_ntlm_credentials

from basic import check_basic_credentials
from digest import check_digest_credentials
from ntlm import check_ntlm_credentials


def get_auth_uri (url):
    """return uri ready for authentication purposes"""
    return stripsite(url)[1]


def get_header_challenges (headers, key):
    """get parsed challenge(s) out of headers[key]"""
    auths = {}
    for auth in headers.getallmatchingheadervalues(key):
        wc.log.debug(wc.LOG_AUTH, "%s header challenge: %s", key, auth)
        for key, data in parse_challenges(auth).items():
            auths.setdefault(key, []).extend(data)
    wc.log.debug(wc.LOG_AUTH, "parsed challenges: %s", auths)
    return auths


def parse_challenges (challenge):
    """return a parsed challenge dict"""
    auths = {}
    while challenge:
        if challenge.startswith('Basic'):
            auth, challenge = parse_basic_challenge(challenge[5:].strip())
            auths.setdefault('Basic', []).append(auth)
        elif challenge.startswith('Digest'):
            auth, challenge = parse_digest_challenge(challenge[6:].strip())
            auths.setdefault('Digest', []).append(auth)
        elif challenge.startswith('NTLM'):
            auth, challenge = parse_ntlm_challenge(challenge[4:].strip())
            auths.setdefault('NTLM', []).append(auth)
        else:
            auth, challenge = challenge, None
            auths.setdefault('unknown', []).append(auth)
    return auths


def get_challenges (**args):
    """return list of challenges for WebCleaner proxy authentication
       Note that HTTP/1.1 allows multiple authentication challenges
       either as multiple headers with the same key, or as one single
       header whose value list is separated by commas"""
    if wc.config['auth_ntlm']:
        chals = [get_ntlm_challenge(**args)]
    else:
        chals = [get_digest_challenge(),
                 get_basic_challenge(),
                ]
    wc.log.debug(wc.LOG_AUTH, "challenges %s", chals)
    return chals


def get_header_credentials (headers, key):
    """Return parsed credentials out of headers[key]"""
    creds = {}
    for cred in headers.getallmatchingheadervalues(key):
        wc.log.debug(wc.LOG_AUTH, "%s header credential: %s", key, cred)
        for key, data in parse_credentials(cred).items():
            creds.setdefault(key, []).extend(data)
    wc.log.debug(wc.LOG_AUTH, "parsed credentials: %s", creds)
    return creds


def parse_credentials (creds):
    """return a parsed credential dict"""
    auths = {}
    while creds:
        if creds.startswith('Basic'):
            auth, creds = parse_basic_credentials(creds[5:].strip())
            auths.setdefault('Basic', []).append(auth)
        elif creds.startswith('Digest'):
            auth, creds = parse_digest_credentials(creds[6:].strip())
            auths.setdefault('Digest', []).append(auth)
        elif creds.startswith('NTLM'):
            auth, creds = parse_ntlm_credentials(creds[4:].strip())
            auths.setdefault('NTLM', []).append(auth)
        else:
            auth, creds = creds, None
            auths.setdefault('unknown', []).append(auth)
    return auths


def get_credentials (challenges, **attrs):
    """return a challenge response with supported authentication scheme
    or None if challenge could not be fulfilled (eg on error or if
    scheme is unsupported)"""
    if 'NTLM' in challenges:
        creds = get_ntlm_credentials(challenges['NTLM'][0], **attrs)
    elif 'Digest' in challenges:
        creds = get_digest_credentials(challenges['Digest'][0], **attrs)
    elif 'Basic' in challenges:
        creds = get_basic_credentials(challenges['Basic'][0], **attrs)
    else:
        creds = None
    wc.log.debug(wc.LOG_AUTH, "credentials: %s", creds)
    return creds


def check_credentials (creds, **attrs):
    """check credentials agains given attributes"""
    wc.log.debug(wc.LOG_AUTH, "check credentials %s with attrs %s", creds, attrs)
    if not creds:
        res = False
    elif wc.config['auth_ntlm'] and 'NTLM' not in creds:
        # forced NTLM auth
        res = False
    elif 'NTLM' in creds:
        res = check_ntlm_credentials(creds['NTLM'][0], **attrs)
    elif 'Digest' in creds:
        res = check_digest_credentials(creds['Digest'][0], **attrs)
    elif 'Basic' in creds:
        res = check_basic_credentials(creds['Basic'][0], **attrs)
    else:
        wc.log.error(wc.LOG_AUTH, "Unknown authentication credentials %s", creds)
        res = False
    return res

