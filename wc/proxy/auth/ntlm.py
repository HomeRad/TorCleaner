# -*- coding: iso-8859-1 -*-
# Used parts form NTLM auth proxy server and NTLM.py

# NTLM.pm - An implementation of NTLM. In this version, I only
# implemented the client side functions that calculates the NTLM response.
# I will add the corresponding server side functions in the next version.
#
# This implementation was written by Yee Man Chan (ymc@yahoo.com).
# Copyright (c) 2002 Yee Man Chan. All rights reserved. This program
# is free software; you can redistribute it and/or modify it under
# the same terms as Perl itself.

# This file is part of 'NTLM Authorization Proxy Server'
# Copyright 2001 Dmitry A. Rozmanov <dima@xenon.spb.ru>
#
# NTLM APS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NTLM APS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the sofware; see the file COPYING. If not, write to the
# Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
"""
HTTP NTLM authentication routines.
"""

__all__ = ["get_ntlm_challenge", "parse_ntlm_challenge",
           "get_ntlm_credentials", "parse_ntlm_credentials",
           "check_ntlm_credentials",
           "create_lm_hashed_password", "create_nt_hashed_password",
           "NTLMSSP_INIT", "NTLMSSP_NEGOTIATE",
           "NTLMSSP_CHALLENGE", "NTLMSSP_AUTH",
 ]

import base64
import random
import struct
import time

import wc
import wc.log
from Crypto.Hash import MD4
from Crypto.Cipher import DES

random.seed()

nonces = {} # nonce to timestamp
max_noncesecs = 2*60*60 # max. lifetime of a nonce is 2 hours (and 5 minutes)

# These constants are stolen from samba-2.2.4 and other sources
NTLMSSP_SIGNATURE = 'NTLMSSP'

# NTLMSSP Message Types
NTLMSSP_INIT      = 0
NTLMSSP_NEGOTIATE = 1
NTLMSSP_CHALLENGE = 2
NTLMSSP_AUTH      = 3
NTLMSSP_UNKNOWN   = 4

# NTLMSSP Flags

# Text strings are in unicode
NTLMSSP_NEGOTIATE_UNICODE                  = 0x00000001
# Text strings are in OEM
NTLMSSP_NEGOTIATE_OEM                      = 0x00000002
# Server should return its authentication realm
NTLMSSP_REQUEST_TARGET                     = 0x00000004
# Request signature capability
NTLMSSP_NEGOTIATE_SIGN                     = 0x00000010
# Request confidentiality
NTLMSSP_NEGOTIATE_SEAL                     = 0x00000020
# Use datagram style authentication
NTLMSSP_NEGOTIATE_DATAGRAM                 = 0x00000040
# Use LM session key for sign/seal
NTLMSSP_NEGOTIATE_LM_KEY                   = 0x00000080
# NetWare authentication
NTLMSSP_NEGOTIATE_NETWARE                  = 0x00000100
# NTLM authentication
NTLMSSP_NEGOTIATE_NTLM                     = 0x00000200
# Domain Name supplied on negotiate
NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED      = 0x00001000
# Workstation Name supplied on negotiate
NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED = 0x00002000
# Indicates client/server are same machine
NTLMSSP_NEGOTIATE_LOCAL_CALL               = 0x00004000
# Sign for all security levels
NTLMSSP_NEGOTIATE_ALWAYS_SIGN              = 0x00008000
# TargetName is a domain name
NTLMSSP_TARGET_TYPE_DOMAIN                 = 0x00010000
# TargetName is a server name
NTLMSSP_TARGET_TYPE_SERVER                 = 0x00020000
# TargetName is a share name
NTLMSSP_TARGET_TYPE_SHARE                  = 0x00040000
# TargetName is a share name
NTLMSSP_NEGOTIATE_NTLM2                    = 0x00080000
# get back session keys
NTLMSSP_REQUEST_INIT_RESPONSE              = 0x00100000
# get back session key, LUID
NTLMSSP_REQUEST_ACCEPT_RESPONSE            = 0x00200000
# request non-ntsession key
NTLMSSP_REQUEST_NON_NT_SESSION_KEY         = 0x00400000
NTLMSSP_NEGOTIATE_TARGET_INFO              = 0x00800000
NTLMSSP_NEGOTIATE_128                      = 0x20000000
NTLMSSP_NEGOTIATE_KEY_EXCH                 = 0x40000000
NTLMSSP_NEGOTIATE_80000000                 = -2147483648 # 0x80000000


def str_flags (flags):
    """
    Return list of names of all set flags.
    """
    res = []
    if flags & NTLMSSP_NEGOTIATE_UNICODE:
        res.append("NTLMSSP_NEGOTIATE_UNICODE")
    if flags & NTLMSSP_NEGOTIATE_OEM:
        res.append("NTLMSSP_NEGOTIATE_OEM")
    if flags & NTLMSSP_REQUEST_TARGET:
        res.append("NTLMSSP_REQUEST_TARGET")
    if flags & NTLMSSP_NEGOTIATE_SIGN:
        res.append("NTLMSSP_NEGOTIATE_SIGN")
    if flags & NTLMSSP_NEGOTIATE_SEAL:
        res.append("NTLMSSP_NEGOTIATE_SEAL")
    if flags & NTLMSSP_NEGOTIATE_DATAGRAM:
        res.append("NTLMSSP_NEGOTIATE_DATAGRAM")
    if flags & NTLMSSP_NEGOTIATE_LM_KEY:
        res.append("NTLMSSP_NEGOTIATE_LM_KEY")
    if flags & NTLMSSP_NEGOTIATE_NETWARE:
        res.append("NTLMSSP_NEGOTIATE_NETWARE")
    if flags & NTLMSSP_NEGOTIATE_NTLM:
        res.append("NTLMSSP_NEGOTIATE_NTLM")
    if flags & NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED:
        res.append("NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED")
    if flags & NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED:
        res.append("NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED")
    if flags & NTLMSSP_NEGOTIATE_LOCAL_CALL:
        res.append("NTLMSSP_NEGOTIATE_LOCAL_CALL")
    if flags & NTLMSSP_NEGOTIATE_ALWAYS_SIGN:
        res.append("NTLMSSP_NEGOTIATE_ALWAYS_SIGN")
    if flags & NTLMSSP_TARGET_TYPE_DOMAIN:
        res.append("NTLMSSP_TARGET_TYPE_DOMAIN")
    if flags & NTLMSSP_TARGET_TYPE_SERVER:
        res.append("NTLMSSP_TARGET_TYPE_SERVER")
    if flags & NTLMSSP_TARGET_TYPE_SHARE:
        res.append("NTLMSSP_TARGET_TYPE_SHARE")
    if flags & NTLMSSP_NEGOTIATE_NTLM2:
        res.append("NTLMSSP_NEGOTIATE_NTLM2")
    if flags & NTLMSSP_REQUEST_INIT_RESPONSE:
        res.append("NTLMSSP_REQUEST_INIT_RESPONSE")
    if flags & NTLMSSP_REQUEST_ACCEPT_RESPONSE:
        res.append("NTLMSSP_REQUEST_ACCEPT_RESPONSE")
    if flags & NTLMSSP_REQUEST_NON_NT_SESSION_KEY:
        res.append("NTLMSSP_REQUEST_NON_NT_SESSION_KEY")
    if flags & NTLMSSP_NEGOTIATE_TARGET_INFO:
        res.append("NTLMSSP_NEGOTIATE_TARGET_INFO")
    if flags & NTLMSSP_NEGOTIATE_128:
        res.append("NTLMSSP_NEGOTIATE_128")
    if flags & NTLMSSP_NEGOTIATE_KEY_EXCH:
        res.append("NTLMSSP_NEGOTIATE_KEY_EXCH")
    if flags & NTLMSSP_NEGOTIATE_80000000:
        res.append("NTLMSSP_NEGOTIATE_80000000")
    return res


def check_nonces ():
    """
    Deprecate old nonces.
    """
    todelete = []
    for nonce, value in nonces.iteritems():
        noncetime = time.time() - value
        if noncetime > max_noncesecs:
            todelete.append(nonce)
    for nonce in todelete:
        del nonces[nonce]
    make_timer(300, check_nonces)


def get_ntlm_challenge (**attrs):
    """
    Return initial challenge token for ntlm authentication.
    """
    ctype = attrs.get('type', NTLMSSP_INIT)
    if ctype == NTLMSSP_INIT:
        # initial challenge (message type 0)
        return "NTLM"
    elif ctype == NTLMSSP_CHALLENGE:
        # after getting first credentials (message type 2)
        msg = create_message2(attrs['domain'])
        return "NTLM %s" % base64.encodestring(msg).strip()
    else:
        raise IOError("Invalid NTLM challenge type")


def parse_ntlm_challenge (challenge):
    """
    Parse both type0 and type2 challenges.
    """
    if "," in challenge:
        chal, remainder = challenge.split(",", 1)
    else:
        chal, remainder = challenge, ""
    chal = chal.strip()
    remainder = remainder.strip()
    if not chal:
        # empty challenge (type0) encountered
        res = {'type': NTLMSSP_INIT}
    else:
        msg = base64.decodestring(chal)
        res = parse_message2(msg)
        if not res:
            wc.log.warn(wc.LOG_AUTH, "invalid NTLM challenge %r", msg)
    return res, remainder


def get_ntlm_credentials (challenge, **attrs):
    """
    Return NTLM credentials for given challenge.
    """
    ctype = attrs.get('type', NTLMSSP_NEGOTIATE)
    if ctype == NTLMSSP_NEGOTIATE:
        msg = create_message1()
    elif ctype == NTLMSSP_AUTH:
        nonce = challenge['nonce']
        domain = attrs['domain']
        username = attrs['username']
        host = attrs['host']
        password = base64.decodestring(attrs['password_b64'])
        lm_hpw = create_lm_hashed_password(password)
        nt_hpw = create_nt_hashed_password(password)
        msg = create_message3(nonce, domain, username, host, lm_hpw, nt_hpw)
    else:
        raise IOError("Invalid NTLM credentials type")
    return "NTLM %s" % base64.encodestring(msg).strip()


def parse_ntlm_credentials (credentials):
    """
    Parse both type1 and type3 credentials.
    """
    if "," in credentials:
        creds, remainder = credentials.split(",", 1)
    else:
        creds, remainder = credentials, ""
    creds = base64.decodestring(creds.strip())
    remainder = remainder.strip()
    if not creds.startswith('%s\x00' % NTLMSSP_SIGNATURE):
        # invalid credentials, skip
        res = {}
    else:
        msgtype = getint32(creds[8:12])
        if msgtype == NTLMSSP_NEGOTIATE:
            res = parse_message1(creds)
        elif msgtype == NTLMSSP_AUTH:
            res = parse_message3(creds)
        else:
            # invalid type, skip
            res = {}
    if not res:
        wc.log.warn(wc.LOG_AUTH, "invalid NTLM credential %r", creds)
    return res, remainder


def check_ntlm_credentials (credentials, **attrs):
    """
    Return True if given credentials validate with given attrs.
    """
    if credentials.has_key('host') and credentials['host'] != "UNKNOWN":
        wc.log.warn(wc.LOG_AUTH, "NTLM wrong host %r", credentials['host'])
        return False
    if credentials.has_key('domain') and credentials['domain'] != 'WORKGROUP':
        wc.log.warn(wc.LOG_AUTH, "NTLM wrong domain %r",
                    credentials['domain'])
        return False
    if credentials['username'] != attrs['username']:
        wc.log.warn(wc.LOG_AUTH, "NTLM wrong username")
        return False
    nonce = attrs['nonce']
    password = base64.decodestring(attrs['password_b64'])
    nt_hashed_pw = create_nt_hashed_password(password)
    lm_hashed_pw = create_lm_hashed_password(password)
    nt_resp = calc_resp(nt_hashed_pw, nonce)
    lm_resp = calc_resp(lm_hashed_pw, nonce)
    if nt_resp != credentials['nt_resp']:
        return False
    if lm_resp != credentials['lm_resp']:
        return False
    return True


################## message construction and parsing ####################

negotiate_flags = NTLMSSP_NEGOTIATE_80000000 | \
   NTLMSSP_NEGOTIATE_128 | \
   NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
   NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED | \
   NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED | \
   NTLMSSP_NEGOTIATE_NTLM | \
   NTLMSSP_NEGOTIATE_UNICODE | \
   NTLMSSP_NEGOTIATE_OEM | \
   NTLMSSP_REQUEST_TARGET

def create_message1 (flags=negotiate_flags):
    """
    Create and return NTLM message type 2 (NTLMSSP_NEGOTIATE).
    """
    # overall length is 48 bytes
    msg = '%s\x00' % NTLMSSP_SIGNATURE # name
    msg += struct.pack("<l", NTLMSSP_NEGOTIATE) # message type
    msg += struct.pack("<l", flags) # flags
    offset = len(msg) + 8*2
    domain = "WORKGROUP"     # domain name
    host = "UNKNOWN"         # hostname
    msg += struct.pack("<h", len(domain)) # domain name length
    msg += struct.pack("<h", len(domain)) # given twice
    msg += struct.pack("<l", offset + len(host)) # domain offset
    msg += struct.pack("<h", len(host)) # host name length
    msg += struct.pack("<h", len(host)) # given twice
    msg += struct.pack("<l", offset) # host offset
    msg += host + domain
    return msg


def parse_message1 (msg):
    """
    Parse and return NTLM message type 1 (NTLMSSP_NEGOTIATE).
    """
    res = {'type': NTLMSSP_NEGOTIATE}
    res['flags'] = getint32(msg[12:16])
    assert None == wc.log.debug(wc.LOG_AUTH, "msg1 flags %s",
                 "\n".join(str_flags(res['flags'])))
    if res['flags'] & NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED:
        domain_offset = getint32(msg[20:24])
        res['domain'] = msg[domain_offset:]
        if res['flags'] & NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED:
            host_offset = getint32(msg[28:32])
            res['host'] = msg[host_offset:domain_offset]
    elif res['flags'] & NTLMSSP_REQUEST_TARGET:
        res['host'] = 'imadoofus'
        res['domain'] = 'WORKGROUP'
    return res


challenge_flags = NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
   NTLMSSP_NEGOTIATE_NTLM | \
   NTLMSSP_REQUEST_INIT_RESPONSE | \
   NTLMSSP_NEGOTIATE_UNICODE | \
   NTLMSSP_REQUEST_TARGET


def create_message2 (domain, flags=challenge_flags):
    """
    Create and return NTLM message type 2 (NTLMSSP_SIGNATURE).
    """
    msg = '%s\x00'% NTLMSSP_SIGNATURE # name
    msg += struct.pack("<l", NTLMSSP_CHALLENGE) # message type
    if flags & NTLMSSP_TARGET_TYPE_DOMAIN:
        msg += struct.pack("<h", 2*len(domain))
        msg += struct.pack("<h", 2*len(domain))
        msg += struct.pack("<l", 48) # domain offset
    else:
        msg += struct.pack("<h", 0)
        msg += struct.pack("<h", 0)
        msg += struct.pack("<l", 40) # domain offset
    msg += struct.pack("<l", flags) # flags
    # compute nonce
    nonce = compute_nonce() # eight random bytes
    assert nonce not in nonces
    nonces[nonce] = time.time()
    msg += nonce
    msg += struct.pack("<l", 0) # 8 bytes of reserved 0s
    msg += struct.pack("<l", 0)
    if flags & NTLMSSP_TARGET_TYPE_DOMAIN:
        msg += struct.pack("<l", 0)    # ServerContextHandleLower
        msg += struct.pack("<l", 0x3c) # ServerContextHandleUpper
        msg += str2unicode(domain)
    return msg


def parse_message2 (msg):
    """
    Parse and return NTLM message type 2 (NTLMSSP_SIGNATURE).
    """
    res = {}
    if not msg.startswith('%s\x00' % NTLMSSP_SIGNATURE):
        wc.log.warn(wc.LOG_AUTH, "NTLM challenge signature not found %r", msg)
        return res
    if getint32(msg[8:12]) != NTLMSSP_CHALLENGE:
        wc.log.warn(wc.LOG_AUTH, "NTLM challenge type not found %r", msg)
        return res
    res['type'] = NTLMSSP_CHALLENGE
    res['flags'] = getint32(msg[20:24])
    assert None == wc.log.debug(wc.LOG_AUTH, "msg2 flags %s",
                 "\n".join(str_flags(res['flags'])))
    res['nonce'] = msg[24:32]
    if res['flags'] & NTLMSSP_TARGET_TYPE_DOMAIN:
        offset = getint32(msg[16:20])
        res['domain'] = unicode2str(msg[offset:])
    return res


auth_flags = NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
   NTLMSSP_NEGOTIATE_NTLM | \
   NTLMSSP_NEGOTIATE_UNICODE | \
   NTLMSSP_REQUEST_TARGET

def create_message3 (nonce, domain, username, host,
                     lm_hashed_pw, nt_hashed_pw, flags=auth_flags):
    """
    Create and return NTLM message type 3 (NTLMSSP_AUTH).
    """
    if lm_hashed_pw:
        lm_resp = calc_resp(lm_hashed_pw, nonce)
    else:
        lm_resp = ''
    if nt_hashed_pw:
        nt_resp = calc_resp(nt_hashed_pw, nonce)
    else:
        nt_resp = ''
    session_key = get_session_key()
    # name
    msg = '%s\x00'% NTLMSSP_SIGNATURE
    # message type
    msg += struct.pack("<l", NTLMSSP_AUTH)
    offset = len(msg) + 8*6 + 4
    msg += struct.pack("<h", len(lm_resp))
    msg += struct.pack("<h", len(lm_resp))
    lm_offset = offset + 2*len(domain) + 2*len(username) + 2*len(host) + \
                len(session_key)
    msg += struct.pack("<l", lm_offset)
    msg += struct.pack("<h", len(nt_resp))
    msg += struct.pack("<h", len(nt_resp))
    nt_offset = lm_offset + len(lm_resp)
    msg += struct.pack("<l", nt_offset)
    msg += struct.pack("<h", 2*len(domain))
    msg += struct.pack("<h", 2*len(domain))
    # domain offset
    msg += struct.pack("<l", offset)
    msg += struct.pack("<h", 2*len(username))
    msg += struct.pack("<h", 2*len(username))
    # username offset
    msg += struct.pack("<l", offset + 2*len(domain))
    msg += struct.pack("<h", 2*len(host))
    msg += struct.pack("<h", 2*len(host))
    # host offset
    msg += struct.pack("<l", offset + 2*len(domain) + 2*len(username))
    msg += struct.pack("<h", len(session_key))
    msg += struct.pack("<h", len(session_key))
    # session offset
    msg += struct.pack("<l", offset + 2*len(domain) + 2*len(username) +
                       2*len(host)+ 48)
    # flags
    msg += struct.pack("<l", flags)
    msg += str2unicode(domain)
    msg += str2unicode(username)
    msg += str2unicode(host)
    msg += lm_resp + nt_resp + session_key
    return msg


def parse_message3 (msg):
    """
    Parse and return NTLM message type 3 (NTLMSSP_AUTH).
    """
    res = {'type': NTLMSSP_AUTH}
    lm_offset = getint32(msg[16:20])
    nt_len = getint16(msg[20:22])
    nt_offset = getint32(msg[24:28])
    domain_offset = getint32(msg[32:36])
    username_offset = getint32(msg[40:44])
    host_offset = getint32(msg[48:52])
    session_offset = getint32(msg[56:60])
    res['flags'] = getint16(msg[60:62])
    assert None == wc.log.debug(wc.LOG_AUTH, "msg3 flags %s",
                 "\n".join(str_flags(res['flags'])))
    res['domain'] = unicode2str(msg[domain_offset:username_offset])
    res['username'] = unicode2str(msg[username_offset:host_offset])
    res['host'] = unicode2str(msg[host_offset:lm_offset])
    res['lm_resp'] = msg[lm_offset:nt_offset]
    res['nt_resp'] = msg[nt_offset:(nt_offset+nt_len)]
    res['session_key'] = msg[session_offset:]
    return res


############################ helper functions ###########################

def compute_nonce ():
    """
    Return a random nonce integer value as 8-byte string.
    """
    return "%08d" % (random.random() * 100000000)


def get_session_key ():
    """
    Return ntlm session key.
    """
    # XXX not implemented
    return ""


def calc_resp (key, nonce):
    """
    Takes a 21 byte array and treats it as 3 56-bit DES keys. The
    8 byte plaintext is encrypted with each key and the resulting 24
    bytes are stored in the result array

    @param key: hashed password
    @param nonce: nonce from server
    """
    assert len(key) == 21, "key must be 21 bytes long"
    assert len(nonce) == 8, "nonce must be 8 bytes long"
    res1 = DES.new(convert_key(key[0:7])).encrypt(nonce)
    res2 = DES.new(convert_key(key[7:14])).encrypt(nonce)
    res3 = DES.new(convert_key(key[14:21])).encrypt(nonce)
    return "%s%s%s" % (res1, res2, res3)


def getint32 (s):
    """
    Called internally to get a 32-bit integer in an NTLM message.
    """
    assert len(s) == 4
    return struct.unpack("<l", s)[0]


def getint16 (s):
    """
    Called internally to get a 16-bit integer in an NTLM message.
    """
    assert len(s) == 2
    return struct.unpack("<h", s)[0]


def str2unicode (s):
    """
    Converts ascii string to dumb unicode.
    """
    return "".join([ c+'\x00' for c in s ])


def unicode2str (s):
    """
    Converts dumb unicode back to ascii string.
    """
    return s[::2]


def lst2str (lst):
    """
    Converts a string to ascii string.
    """
    return "".join([chr(i & 0xFF) for i in lst])


def convert_key (key):
    """
    Converts a 7-bytes key to an 8-bytes key based on an algorithm.
    """
    assert len(key) == 7, "NTLM convert_key needs 7-byte key"
    bytes = [key[0],
             chr(((ord(key[0]) << 7) & 0xFF) | (ord(key[1]) >> 1)),
             chr(((ord(key[1]) << 6) & 0xFF) | (ord(key[2]) >> 2)),
             chr(((ord(key[2]) << 5) & 0xFF) | (ord(key[3]) >> 3)),
             chr(((ord(key[3]) << 4) & 0xFF) | (ord(key[4]) >> 4)),
             chr(((ord(key[4]) << 3) & 0xFF) | (ord(key[5]) >> 5)),
             chr(((ord(key[5]) << 2) & 0xFF) | (ord(key[6]) >> 6)),
             chr( (ord(key[6]) << 1) & 0xFF),
            ]
    return "".join([ set_odd_parity(b) for b in bytes ])


def set_odd_parity (byte):
    """
    Turns one-byte into odd parity. Odd parity means that a number in
    binary has odd number of 1's.
    """
    assert len(byte) == 1
    parity = 0
    ordbyte = ord(byte)
    for dummy in range(8):
        if (ordbyte & 0x01) != 0:
            parity += 1
        ordbyte >>= 1
    ordbyte = ord(byte)
    if parity % 2 == 0:
        if (ordbyte & 0x01) != 0:
            ordbyte &= 0xFE
        else:
            ordbyte |= 0x01
    return chr(ordbyte)


def create_lm_hashed_password (passwd):
    """
    Create LanManager hashed password.
    """
    # get 14-byte LanManager-suitable password
    lm_pw = create_lm_password(passwd)
    # do hash
    magic_lst = [0x4B, 0x47, 0x53, 0x21, 0x40, 0x23, 0x24, 0x25]
    magic_str = lst2str(magic_lst)
    lm_hpw = DES.new(convert_key(lm_pw[0:7])).encrypt(magic_str)
    lm_hpw += DES.new(convert_key(lm_pw[7:14])).encrypt(magic_str)
    # adding zeros for padding
    lm_hpw += '\x00'*5
    return lm_hpw


def create_lm_password (passwd):
    """
    Create Lan Manager hashed password.
    """
    passwd = passwd.upper()
    if len(passwd) < 14:
        lm_pw = passwd + ('\x00'*(14-len(passwd)))
    else:
        lm_pw = passwd[0:14]
    assert len(lm_pw) == 14, "NTLM invalid password length %d"%len(lm_pw)
    return lm_pw


def create_nt_hashed_password (passwd):
    """
    Create NT hashed password.
    """
    # we have to have UNICODE password
    pw = str2unicode(passwd)
    # do MD4 hash
    md4_context = MD4.new()
    md4_context.update(pw)
    nt_hpw = md4_context.digest()
    # adding zeros for padding
    nt_hpw += '\x00'*5
    return nt_hpw


from wc.proxy.timer import make_timer
def init ():
    """
    Check for timed out nonces every 5 minutes.
    """
    make_timer(300, check_nonces)
