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
        for key, data in parse_challenges(auth).items():
            auths.setdefault(key, []).extend(data)
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
    return [get_basic_challenge(args),
            get_digest_challenge(args),
            get_ntlm_challenge(args)]


def get_header_credentials (headers, key):
    creds = {}
    for cred in get_header_values(headers, key):
        for key, data in parse_credentials(cred).items():
            creds.setdefault(key, []).extend(data)
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
        return get_ntlm_credentials(challenges['NTLM'][0], **attrs)
    if 'Digest' in challenges:
        return get_digest_credentials(challenges['Digest'][0], **attrs)
    if 'Basic' in challenges:
        return get_basic_credentials(challenges['Basic'][0], **attrs)
    return None


def check_credentials (creds, **attrs):
    if not creds:
        return False
    if 'Digest' in creds:
        return check_digest_credentials(creds['Digest'][0], **attrs)
    if 'Basic' in creds:
        return check_basic_credentials(creds['Basic'][0], **attrs)
    if 'NTLM' in creds:
        return check_ntlm_credentials(creds['NTLM'][0], **attrs)
    warn(PROXY, "Unknown authentication credentials %s", str(creds))
    return False


def _test ():
    print parse_credentials("Basic dGVzdDp0ZXN0")
    #attrs = {"username":"wummel", "password_b64":"", "uri":"/", "method":"GET"}
    #challenges = get_challenges()
    #print "challenges", challenges
    #challenges = parse_challenges(", ".join(challenges))
    #print "parsed challenges", challenges
    #creds = get_credentials(challenges, **attrs)
    #print "credentials", creds
    #creds = parse_credentials(creds)
    #print "parsed credentials", creds
    #print check_credentials(creds, **attrs)


if __name__=='__main__':
    _test()
