"""support for different HTTP proxy authentication schemes"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

try:
    from wc.proxy.Headers import get_header_values
except ImportError:
    print "using local development version"
    import sys, os
    sys.path.insert(0, os.getcwd())
    from wc.proxy.Headers import get_header_values

# default realm for authentication
wc_realm = "unknown"

from wc.log import *
from basic import *
from digest import *
from ntlm import *


def get_header_challenges (headers, key):
    auths = {}
    for auth in get_header_values(headers, key):
        debug(AUTH, "%s header challenge:\n  %s", key, auth)
        for key, data in parse_challenges(auth).items():
            auths.setdefault(key, []).extend(data)
    debug(AUTH, "parsed challenges: %s", str(auths))
    return auths


def parse_challenges (challenge):
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
    chals = [get_basic_challenge(),
             #get_digest_challenge(),
             #get_ntlm_challenge(**args),
            ]
    debug(AUTH, "challenges %s", str(chals))
    return chals



def get_header_credentials (headers, key):
    creds = {}
    for cred in get_header_values(headers, key):
        debug(AUTH, "%s header credential:\n  %s", key, cred)
        for key, data in parse_credentials(cred).items():
            creds.setdefault(key, []).extend(data)
    debug(AUTH, "parsed credentials: %s", str(creds))
    return creds


def parse_credentials (creds):
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
    debug(AUTH, "get_credentials: %s", str(creds))
    return creds


def check_credentials (creds, **attrs):
    if not creds:
        res = False
    elif 'NTLM' in creds:
        res = check_ntlm_credentials(creds['NTLM'][0], **attrs)
    elif 'Digest' in creds:
        res = check_digest_credentials(creds['Digest'][0], **attrs)
    elif 'Basic' in creds:
        res = check_basic_credentials(creds['Basic'][0], **attrs)
    else:
        error(AUTH, "Unknown authentication credentials %s", str(creds))
        res = False
    return res


def _test ():
    #print parse_credentials("Basic dGVzdDp0ZXN0")
    #attrs = {, "password_b64":"", "uri":"/", "method":"GET"}
    attrs = {"username":"wummel", "type":1,}
    challenges = get_challenges(type=0)
    print "challenges 0", challenges
    challenges = parse_challenges(", ".join(challenges))
    print "parsed challenges 0", challenges
    creds = get_credentials(challenges, **attrs)
    print "credentials 1", creds
    creds = parse_credentials(creds)
    print "parsed credentials 1", creds
    attrs['host'] = creds['NTLM'][0]['host']
    attrs['domain'] = creds['NTLM'][0]['domain']
    print check_credentials(creds, **attrs)
    creds['type'] = 2
    challenges = get_challenges(**creds)
    print "challenges 2", challenges
    challenges = parse_challenges(", ".join(challenges))
    print "parsed challenges 2", challenges
    attrs['type'] = 3
    creds = get_credentials(challenges, **attrs)
    print "credentials 3", creds
    creds = parse_credentials(creds)
    print "parsed credentials 3", creds
    print check_credentials(creds, **attrs)


if __name__=='__main__':
    _test()
