"""NTLM authentication routines"""
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

__all__ = ["get_ntlm_challenge", "parse_ntlm_challenge",
           "get_ntlm_credentials", "parse_ntlm_credentials",
           "check_ntlm_credentials",
           "NTLMSSP_INIT", "NTLMSSP_NEGOTIATE",
           "NTLMSSP_CHALLENGE", "NTLMSSP_AUTH",
 ]

import des, md4, utils, base64, random, struct, time
from wc.log import *
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
NTLMSSP_NEGOTIATE_80000000                 = 0x80000000


def check_nonces ():
    # deprecate old nonces
    for key, value in nonces.items():
        noncetime = time.time() - value
        if noncetime > max_noncesecs:
            del nonces[nonce]


def get_ntlm_challenge (**attrs):
    """return initial challenge token for ntlm authentication"""
    ctype = attrs.get('type', NTLMSSP_INIT)
    if ctype==NTLMSSP_INIT:
        # initial challenge (message type 0)
        return "NTLM"
    elif ctype==NTLMSSP_CHALLENGE:
        # after getting first credentials (message type 2)
        msg = create_message2(attrs['domain'])
        return "NTLM %s" % base64.encodestring(msg).strip()
    else:
        raise IOError("Invalid NTLM challenge type")


def parse_ntlm_challenge (challenge):
    """parse both type0 and type2 challenges"""
    if "," in challenge:
        chal, remainder = challenge.split(",", 1)
    else:
        chal, remainder = challenge, ""
    chal = chal.strip()
    reaminder = remainder.strip()
    if not chal:
        # empty challenge (type0) encountered
        res = {'type': NTLMSSP_INIT}
    else:
        msg = base64.decodestring(chal)
        res = parse_message2(msg)
        if not res:
            warn(AUTH, "invalid NTLM challenge %s", `msg`)
    return res, remainder


def get_ntlm_credentials (challenge, **attrs):
    ctype = attrs.get('type', NTLMSSP_NEGOTIATE)
    if ctype==NTLMSSP_NEGOTIATE:
        msg = create_message1()
    elif ctype==NTLMSSP_AUTH:
        nonce = challenge['nonce']
        domain = attrs['domain']
        username = attrs['username']
        host = attrs['host']
        msg = create_message3(nonce, domain, username, host)
    else:
        raise IOError("Invalid NTLM credentials type")
    return "NTLM %s" % base64.encodestring(msg).strip()


def parse_ntlm_credentials (credentials):
    """parse both type1 and type3 credentials"""
    if "," in credentials:
        creds, remainder = credentials.split(",", 1)
    else:
        creds, remainder = credentials, ""
    creds = base64.decodestring(creds.strip())
    remainder = remainder.strip()
    if not creds.startswith('%s\x00'%NTLMSSP_SIGNATURE):
        # invalid credentials, skip
        res = {}
    else:
        msgtype = getint32(creds[8:12])
        if msgtype==NTLMSSP_NEGOTIATE:
            res = parse_message1(creds)
        elif msgtype==NTLMSSP_AUTH:
            res = parse_message3(creds)
        else:
            # invalid type, skip
            res = {}
    if not res:
        warn(AUTH, "invalid NTLM credential %s", `creds`)
    return res, remainder


def check_ntlm_credentials (credentials, **attrs):
    # XXX
    return False


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
    """create negotiate message (NTLM msg type 1)"""
    # overall length is 48 bytes
    msg = '%s\x00'%NTLMSSP_SIGNATURE # name
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
    res = {'type': NTLMSSP_NEGOTIATE}
    res['flags'] = getint32(msg[12:16])
    domain_offset = getint32(msg[20:24])
    host_offset = getint32(msg[28:32])
    res['host'] = msg[host_offset:domain_offset]
    res['domain'] = msg[domain_offset:]
    return res


challenge_flags = NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
   NTLMSSP_NEGOTIATE_NTLM | \
   NTLMSSP_REQUEST_INIT_RESPONSE | \
   NTLMSSP_NEGOTIATE_UNICODE | \
   NTLMSSP_REQUEST_TARGET

def create_message2 (domain, flags=challenge_flags):
    msg = '%s\x00'% NTLMSSP_SIGNATURE # name
    msg += struct.pack("<l", NTLMSSP_CHALLENGE) # message type
    msg += struct.pack("<h", len(domain))
    msg += struct.pack("<h", len(domain))
    msg += struct.pack("<l", 48) # domain offset (always 48)
    msg += struct.pack("<l", flags) # flags
    # compute nonce
    nonce = compute_nonce() # eight random bytes
    assert nonce not in nonces
    nonces[nonce] = time.time()
    msg += nonce
    msg += struct.pack("<l", 0) # 8 bytes of reserved 0s
    msg += struct.pack("<l", 0)
    msg += struct.pack("<l", 0)    # ServerContextHandleLower
    msg += struct.pack("<l", 0x3c) # ServerContextHandleUpper
    msg += utils.str2unicode(domain)
    return msg


def parse_message2 (msg):
    res = {}
    if not msg.startswith('%s\x00'%NTLMSSP_SIGNATURE):
        warn(AUTH, "NTLM challenge signature not found %s", `msg`)
        return res
    if getint32(msg[8:12])!=NTLMSSP_CHALLENGE:
        warn(AUTH, "NTLM challenge type not found %s", `msg`)
        return res
    res['type'] = NTLMSSP_CHALLENGE
    res['flags'] = getint32(msg[20:24])
    res['nonce'] = msg[24:32]
    res['domain'] = utils.unicode2str(msg[48:])
    return res


auth_flags = NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
   NTLMSSP_NEGOTIATE_NTLM | \
   NTLMSSP_NEGOTIATE_UNICODE | \
   NTLMSSP_REQUEST_TARGET

def create_message3 (nonce, domain, username, host,
                     lm_hashed_pw=None, nt_hashed_pw=None, flags=auth_flags):
    if lm_hashed_pw:
        lm_resp = calc_resp(lm_hashed_pw, nonce)
    else:
        lm_resp = ''
    if nt_hashed_pw:
        nt_resp = calc_resp(nt_hashed_pw, nonce)
    else:
        nt_resp = ''
    session_key = get_session_key()
    msg = '%s\x00'% NTLMSSP_SIGNATURE # name
    msg += struct.pack("<l", NTLMSSP_AUTH) # message type
    offset = len(msg) + 8*6 + 4
    lm_offset = offset + 2*len(domain) + 2*len(username) + 2*len(host) + len(session_key)
    nt_offset = lm_offset + len(lm_resp)
    msg += struct.pack("<h", len(lm_resp))
    msg += struct.pack("<h", len(lm_resp))
    msg += struct.pack("<l", lm_offset)
    msg += struct.pack("<h", len(nt_resp))
    msg += struct.pack("<h", len(nt_resp))
    msg += struct.pack("<l", nt_offset)
    msg += struct.pack("<l", flags) # flags
    msg += utils.str2unicode(domain)
    msg += utils.str2unicode(username)
    msg += utils.str2unicode(host)
    msg += lm_resp + nt_resp + session_key
    return msg


def parse_message3 (msg):
    res = {'type': NTLMSSP_AUTH}
    lm_offset = getint32(msg[16:20])
    nt_len = getint16(msg[20:22])
    nt_offset = getint32(msg[24:28])
    res['flags'] = getint32(msg[28:32])
    res['lm_resp'] = msg[lm_offset:nt_offset]
    res['nt_resp'] = msg[nt_offset:(nt_offset+nt_len)]
    res['session_key'] = msg[(nt_offset+nt_len):]
    return res


############################ helper functions ###########################

def compute_nonce ():
    return "%08d" % (random.random()*100000000)


def get_session_key ():
    """return ntlm session key"""
    # XXX not implemented
    return ""


def calc_resp (key, nonce):
    """takes a 21 byte array and treats it as 3 56-bit DES keys. The
       8 byte plaintext is encrypted with each key and the resulting 24
       bytes are stored in the result array

       key - hashed password
       nonce - nonce from server
    """
    assert len(key)==21, "key must be 21 bytes long"
    assert len(nonce)==8, "nonce must be 21 bytes long"
    res1 = des.DES(key[0:7]).encrypt(nonce[0:8])
    res2 = des.DES(key[7:14]).encrypt(nonce[0:8])
    res3 = des.DES(key[14:21]).encrypt(nonce[0:8])
    return "%s%s%s" % (res1, res2, res3)


def getint32 (s):
    """called internally to get a 32-bit integer in an NTLM message"""
    assert len(s)==4
    return struct.unpack("<l", s)[0]


def getint16 (s):
    """called internally to get a 16-bit integer in an NTLM message"""
    assert len(s)==2
    return struct.unpack("<h", s)[0]


def create_LM_hashed_password (passwd):
    "setup LanManager password"
    "create LanManager hashed password"
    passwd = passwd.upper()
    if len(passwd) < 14:
        lm_pw = passwd + ('\x00'*(len(passwd)-14))
    else:
        lm_pw = passwd[0:14]
    # do hash
    magic_lst = [0x4B, 0x47, 0x53, 0x21, 0x40, 0x23, 0x24, 0x25]
    magic_str = utils.lst2str(magic_lst)
    lm_hpw = des.DES(convert_key(lm_pw[0:7])).encrypt(magic_str)
    lm_hpw += des.DES(convert_key(lm_pw[7:14])).encrypt(magic_str)
    # adding zeros for padding
    lm_hpw += '\x00'*5
    return lm_hpw


def create_NT_hashed_password (passwd):
    "create NT hashed password"
    # we have to have UNICODE password
    pw = utils.str2unicode(passwd)
    # do MD4 hash
    md4_context = md4.new()
    md4_context.update(pw)
    nt_hpw = md4_context.digest()
    # adding zeros for padding
    nt_hpw += '\x00'*5
    return nt_hpw


from wc.proxy import make_timer
# check for timed out nonces every 5 minutes
make_timer(300, check_nonces)
