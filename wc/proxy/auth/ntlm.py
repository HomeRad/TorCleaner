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
           "check_ntlm_credentials"]

import des, md4, utils, base64, random
from wc.log import *
random.seed()

nonces = {} # nonce to timestamp
max_noncesecs = 2*60*60 # max. lifetime of a nonce is 2 hours (and 5 minutes)

# These constants are stolen from samba-2.2.4 and other sources
NTLMSSP_SIGNATURE = 'NTLMSSP'

# NTLMSSP Message Types
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
    # deprecate old nonce
    for key, value in nonces.items():
        noncetime = time.time() - value
        if noncetime > max_noncesecs:
            del nonces[nonce]


def get_ntlm_challenge (**attrs):
    """return initial challenge token for ntlm authentication"""
    ctype = attrs.get('type', 0)
    if ctype==0:
        # initial challenge
        return "NTLM"
    elif ctype==2:
        # after getting first credentials
        return "NTLM %s" % base64.encodestring(create_message2()).strip()
    else:
        raise IOError("Invalid NTLM challenge type")


def parse_ntlm_challenge (challenge):
    """parse both type0 and type2 challenges"""
    res = {}
    if "," in challenge:
        chal, remainder = challenge.split(",", 1)
    else:
        chal, remainder = challenge, ""
    chal = base64.decodestring(chal.strip())
    if not chal.startswith('NTLMSSP\x00'):
        # empty challenge (type0) encountered
        res['type'] = 0
        return res, challenge
    res['type'] = 2
    res['nonce'] = chal[24:32]
    return res, remainder.strip()


def get_ntlm_credentials (challenge, **attrs):
    ctype = attrs.get('type', 1)
    if ctype==1:
        msg = create_message1()
    elif ctype==3:
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
    res = {}
    if "," in credentials:
        creds, remainder = credentials.split(",", 1)
    else:
        creds, remainder = credentials, ""
    creds = base64.decodestring(creds.strip())
    if not creds.startswith('NTLMSSP\x00'):
        # invalid credentials, skip
        return res, remainder.strip()
    msgtype = ord(creds[8])
    if msgtype==1:
        res['type'] = 1
        debug(AUTH, "ntlm msgtype 1 %s", `creds`)
        domain_len = int(creds[16:18])
        domain_off = int(creds[20:22])
        host_len = int(creds[24:26])
        host_off = int(creds[28:30])
        res['host'] = creds[host_off:host_off+host_len]
        res['domain'] = creds[domain_off:domain_off+domain_len]
    elif msgtype==3:
        res['type'] = 3
        debug(AUTH, "ntlm msgtype 3 %s", `creds`)
        lm_res_len = int(creds[12:14])
        # XXX
    else:
        # invalid credentials, skip
        return res, remainder.strip()
    return res, remainder.strip()


def check_ntlm_credentials (credentials, **attrs):
    # XXX
    return False


def compute_nonce ():
    return "%08d" % (random.random()*100000000)


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


def create_LM_hashed_password (passwd):
    "setup LanManager password"
    "create LanManager hashed password"
    lm_pw = '\000' * 14
    passwd = passwd.upper()
    if len(passwd) < 14:
        lm_pw = passwd + lm_pw[len(passwd) - 14:]
    else:
        lm_pw = passwd[0:14]
    # do hash
    magic_lst = [0x4B, 0x47, 0x53, 0x21, 0x40, 0x23, 0x24, 0x25]
    magic_str = utils.lst2str(magic_lst)
    res1 = des.DES(lm_pw[0:7]).encrypt(magic_str)
    res2 = des.DES(lm_pw[7:14]).encrypt(magic_str)
    # adding zeros to get 21 bytes string
    return "%s%s%s" % (res1, res2, '\000' * 5)


def create_NT_hashed_password (passwd):
    "create NT hashed password"
    # we have to have UNICODE password
    pw = utils.str2unicode(passwd)
    # do MD4 hash
    md4_context = md4.new()
    md4_context.update(pw)
    res = md4_context.digest()
    # adding zeros to get 21 bytes string
    return "%s%s" % (res, '\000' * 5)


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
    msg = '%s\x00'% NTLMSSP_SIGNATURE # name
    msg += struct.pack("<l", NTLMSSP_NEGOTIATE) # message type
    msg += struct.pack("<l", flags) # flags
    offset = len(msg) + 8*2
    domain = "WORKGROUP"     # domain name
    host = "UNKNOWN"         # hostname
    msg += struct.pack("<h", len(domain)) # domain name length
    msg += struct.pack("<h", len(domain)) # given twice
    msg += struct.pack("<l", offset + len(host)) # offset
    msg += struct.pack("<h", len(host)) # host name length
    msg += struct.pack("<h", len(host)) # given twice
    msg += struct.pack("<l", offset);
    msg += host + domain
    return msg


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
    msg += struct.pack("<l", 48)
    msg += struct.pack("<l", flags) # flags
    # compute nonce
    nonce = compute_nonce() # eight random bytes
    assert nonce not in nonces
    nonces[nonce] = time.time()
    msg += nonce
    msg += struct.pack("<l<l", 0, 0) # 8 bytes of reserved 0s
    msg += struct.pack("<l", 0)      # ServerContextHandleLower
    msg += struct.pack("<l", 0x3c)   # ServerContextHandleUpper
    msg += unicode(domain)
    return msg


def create_message3 (nonce, domain, username, host,
                     lm_hashed_pw=None, nt_hashed_pw=None):
    if lm_hashed_pw:
        lm_resp = calc_resp(lm_hashed_pw, nonce)
    else:
        lm_resp = ''
    if nt_hashed_pw:
        nt_resp = calc_resp(nt_hashed_pw, nonce)
    else:
        nt_resp = ''
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
    msg += unicode(domain) + unicode(username) + unicode(host)
    msg += lm_resp + nt_resp + session_key
    return msg



from wc.proxy import make_timer
# check for timed out nonces every 5 minutes
make_timer(300, check_nonces)
