"""support for different HTTP proxy authentication schemes"""
# -*- coding: iso-8859-1 -*-

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

try:
    from wc.proxy import stripsite
except ImportError:
    print "using local development version"
    import sys, os
    sys.path.insert(0, os.getcwd())
    from wc.proxy import stripsite

# default realm for authentication
wc_realm = "unknown"

from wc.log import *
from wc import config
from basic import *
from digest import *
from ntlm import *


def get_auth_uri (url):
    return stripsite(url)[1]


def get_header_challenges (headers, key):
    auths = {}
    for auth in headers.getallmatchingheadervalues(key):
        debug(AUTH, "%s header challenge: %s", key, auth)
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
    if config['auth_ntlm']:
        chals = [get_ntlm_challenge(**args)]
    else:
        chals = [get_digest_challenge(),
                 get_basic_challenge(),
                ]
    debug(AUTH, "challenges %s", str(chals))
    return chals



def get_header_credentials (headers, key):
    creds = {}
    for cred in headers.getallmatchingheadervalues(key):
        debug(AUTH, "%s header credential: %s", key, cred)
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
    debug(AUTH, "credentials: %s", str(creds))
    return creds


def check_credentials (creds, **attrs):
    debug(AUTH, "check credentials %s with attrs %s", str(creds), str(attrs))
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
    from wc.log import initlog
    initlog("test/logging.conf")
    _test_ntlm()


def _test_ntlm ():
    import base64, pprint
    challenges = get_challenges(type=NTLMSSP_INIT)
    print "challenges type 0"
    pprint.pprint(challenges)
    challenges = parse_challenges(", ".join(challenges))
    print "parsed challenges type 0"
    pprint.pprint(challenges)
    print
    attrs = {"username": "calvin", "type": NTLMSSP_NEGOTIATE,}
    creds = get_credentials(challenges, **attrs)
    print "credentials type 1"
    pprint.pprint(creds)
    creds = parse_credentials(creds)
    print "parsed credentials type 1"
    pprint.pprint(creds)
    print
    attrs['host'] = creds['NTLM'][0]['host']
    attrs['domain'] = creds['NTLM'][0]['domain']
    attrs['type'] = NTLMSSP_CHALLENGE
    challenges = get_challenges(**attrs)
    print "challenges type 2"
    pprint.pprint(challenges)
    challenges = parse_challenges(", ".join(challenges))
    print "parsed challenges type 2"
    pprint.pprint(challenges)
    print
    attrs['type'] = NTLMSSP_AUTH
    attrs['nonce'] = challenges['NTLM'][0]['nonce']
    attrs['password_b64'] = base64.encodestring("Beeblebrox")
    creds = get_credentials(challenges, **attrs)
    print "credentials type 3"
    print `creds`
    creds = parse_credentials(creds)
    print "parsed credentials type 3"
    pprint.pprint(creds)
    print "Check:", check_credentials(creds, **attrs)


def _test_digest ():
    chals = parse_challenges("Digest realm=\"This is my digest auth\", nonce=\"i5tbP9h2RAiGbccW\", qop=\"auth\", stale=false")
    print "chals:", chals
    attrs = {"username": "calvin", "password_b64": "Y2Fsdmlu",
             "uri":"/logo.gif", "method":"GET"}
    # test credentials recorded from mozilla session
    mozcreds = {"username":"calvin",  "realm":"This is my digest auth",
            "nonce":"i5tbP9h2RAiGbccW", "uri":"/logo.gif",
            "response":"73b8f33cd4ef569ec05dca533209a647",
            "qop":"auth", "nc":"00000001", "cnonce":"5993211954416e83"}
    creds = get_credentials(chals, **attrs)
    print "creds:", creds
    creds = parse_credentials(creds)
    for key, item in creds['Digest'][0].items():
        if key not in mozcreds:
            print "key", key, "is not in mozcreds"
        elif item != mozcreds[key]:
            print "key", key, "creds=", item, "mozcreds=", mozcreds[key]


if __name__=='__main__':
    _test()
