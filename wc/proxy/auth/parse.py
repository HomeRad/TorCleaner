"""parse basic and digest HTTP auth strings into key/value tokens"""
from wc.log import *

separators = ("()<>@,;:\\\"/[]?={} \t")
token_chars = ('!#$%&\'*+-.abcdefghijklmnopqrstuvwxyz'
               'ABCDEFGHIJKLMNOPQRSTUVWXYZ^_`0123456789|~')

def parse_token (s, tok="", relax=False, more_chars=""):
    if tok:
        if not s.startswith(tok):
            warn(PROXY, "expected %r start with %r", s, tok)
        if not relax:
            s = s[len(tok):]
    else:
        for i, c in enumerate(s):
            if c not in token_chars and c not in more_chars:
                i -= 1
                break
            tok += c
        s = s[i+1:]
    return tok, s.strip()


def parse_quotedstring (s):
    dummy, s = parse_token(s, tok='"')
    quoted = ""
    esc = False
    for i, c in enumerate(s):
        if esc:
            esc = False
        elif c=="\\":
            esc = True
            continue
        elif c=='"':
            break
        elif 31 < ord(c) < 127:
            quoted += c
    s = s[i:]
    dummy, s = parse_token(s, tok='"')
    return quoted, s.strip()


def parse_auth (auth, data):
    """generic authentication tokenizer
       auth - default dictionary
       data - string data to parse

    returns augmented auth dict and unparsed data
    """
    while data:
        key, data = parse_token(data)
        if not data.startswith("="):
            data = "%s %s" % (key, data)
            break
        dummy, data = parse_token(data, tok="=")
        if data.startswith('"'):
            value, data = parse_quotedstring(data)
        else:
            value, data = parse_token(data)
        auth[key] = value
        if data:
            dummy, data = parse_token(data, tok=",")
    return auth, data.strip()

