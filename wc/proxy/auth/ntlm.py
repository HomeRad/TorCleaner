# -*- coding: iso-8859-1 -*-
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

# 4-byte NTLM message flags
NTLM_OEM =            0x00000002 # Negotiate OEM (ASCII, basically)
NTLM_REQUEST_TARGET = 0x00000004 # Request Target
NTLM_NTLM =           0x00000200 # Negotiate NTLM
NTLM_DOMAIN =         0x00001000 # Negotiate Domain Supplied
NTLM_WORKSTATION =    0x00002000 # Negotiate Workstation Supplied
NTLM_SIGN =           0x00008000 # Negotiate Always Sign


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


#########################################################################
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

def calc_resp (keys_str, plain_text):
    """takes a 21 byte array and treats it as 3 56-bit DES keys. The
       8 byte plaintext is encrypted with each key and the resulting 24
       bytes are stored in the result array

       keys_str - hashed password
       plain_text - nonce from server
    """
    res1 = des.DES(keys_str[0:7]).encrypt(plain_text[0:8])
    res2 = des.DES(keys_str[7:14]).encrypt(plain_text[0:8])
    res3 = des.DES(keys_str[14:21]).encrypt(plain_text[0:8])
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


##########################################################################
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

class record (object):

    def __init__ (self, data, offset=0):
        self.data = data
        self.len = len(data)
        self.offset = 0
        self.next_offset = self.offset + self.len

    def create_record_info (self, offset):
        """helper function for creation info field in message 3"""
        self.offset = offset
        len1 = utils.int2chrs(self.len)
        len2 = len1
        data_off = utils.int2chrs(self.offset)
        self.record_info = len1 + len2 + data_off + '\000\000'
        # looks like the length is always = 8 bytes
        self.next_offset = offset + self.len


def create_message1 ():
    # overall lenght = 48 bytes
    protocol = 'NTLMSSP\x00' # name
    type = '\x01'            # type 1
    zero3 = '\x00'*3         # zero padding
    flags="\xb2\x03"         # flags
    zero2 = '\x00'*2         # zero padding
    domain = "WORKGROUP"     # domain name
    dom_len = len(domain)    # domain length
    host = "UNKNOWN"         # hostname
    host_len = len(host)     # host length
    host_off = 32            # index of hostname in message
    dom_off = host_off + len(host) # index of domain name in message
    return "%(protocol)s%(type)s%(zero3)s%(flags)s%(zero2)s%(dom_len)02d%(dom_len)02d%(dom_off)02d00%(host_len)02d%(host_len)02d%(host_off)02d00%(host)s%(domain)s" % locals()


def create_message2 ():
    protocol = 'NTLMSSP\x00'    #name
    type = '\x02'
    zero7 = '\x00'*7
    msglen = '\x00\x28'
    zero2 = '\x00'*2
    flags="\x01\x82"
    # zero2 again
    nonce = "%08d" % (random.random()*100000000) # eight random bytes
    assert nonce not in nonces
    nonces[nonce] = time.time()
    zero8 = '\x00'*8
    return "%(protocol)s%(type)s%(zero7)s%(msglen)s%(zero2)s%(flags)s%(zero2)s%(nonce)s%(zero8)s" % locals()


def create_message3 (nonce, domain, username, host,
                     lm_hashed_pw=None, nt_hashed_pw=None, ntlm_mode=0):
    protocol = 'NTLMSSP\x00'        # name
    type = '\x03'                   # type 3
    head = protocol + type + '\x00'*3
    flags="\x01\x82"
    domain_rec = record(domain)
    user_rec = record(username)
    host_rec = record(host)
    additional_rec = record('')
    if lm_hashed_pw:
        lm_rec = record(ntlm_procs.calc_resp(lm_hashed_pw, nonce))
    else:
        lm_rec = record('')
    if nt_hashed_pw:
        nt_rec = record(ntlm_procs.calc_resp(nt_hashed_pw, nonce))
    else:
        nt_rec = record('')
    # length of the head and five infos for LM, NT, Domain, User, Host
    domain_offset = len(head) + 5 * 8
    # and unknown record info and flags' lenght
    if ntlm_mode == 0:
        domain_offset += 8 + len(flags)
    # create info fields
    domain_rec.create_record_info(domain_offset)
    user_rec.create_record_info(domain_rec.next_offset)
    host_rec.create_record_info(user_rec.next_offset)
    lm_rec.create_record_info(host_rec.next_offset)
    nt_rec.create_record_info(lm_rec.next_offset)
    additional_rec.create_record_info(nt_rec.next_offset)
    # data part of the message 3
    data_part = domain_rec.data + user_rec.data + host_rec.data + lm_rec.data + nt_rec.data
    # build message 3
    m3 = head + lm_rec.record_info + nt_rec.record_info + \
         domain_rec.record_info + user_rec.record_info + host_rec.record_info
    # Experimental feature !!!
    if ntlm_mode == 0:
        m3 += additional_rec.record_info + flags

    m3 += data_part
    # Experimental feature !!!
    if ntlm_mode == 0:
        m3 += additional_rec.data
    return m3


def item (item_str):
    item = {}
    res = ''
    item['len1'] = utils.bytes2int(item_str[0:2])
    item['len2'] = utils.bytes2int(item_str[2:4])
    item['offset'] = utils.bytes2int(item_str[4:6])
    res += '%s\n\nlength (two times), offset, delimiter\n' % (utils.str2hex(item_str))
    res += '%s decimal: %3d    # length 1\n' % (utils.int2hex_str(item['len1']), item['len1'])
    res += '%s decimal: %3d    # length 2\n' % (utils.int2hex_str(item['len2']), item['len2'])
    res += '%s decimal: %3d    # offset\n' % (utils.int2hex_str(item['offset']), item['offset'])
    res += '%s                   # delimiter (two zeros)\n\n' % utils.str2hex(item_str[-2:])
    item['string'] = res
    return item


def flags (flag_str):
    res = ''
    res += '%s\n\n' % utils.str2hex(flag_str)
    flags = utils.bytes2int(flag_str[0:2])
    res += '%s                   # flags\n' % (utils.int2hex_str(flags))
    res += 'Binary:\nlayout 87654321 87654321\n'
    res += '       %s %s\n' % (utils.byte2bin_str(flag_str[1]), utils.byte2bin_str(flag_str[0]))
    flags2 = utils.bytes2int(flag_str[2:4])
    res += '%s                   # more flags ???\n' % (utils.int2hex_str(flags2))
    res += 'Binary:\nlayout 87654321 87654321\n'
    res += '       %s %s\n' % (utils.byte2bin_str(flag_str[3]), utils.byte2bin_str(flag_str[2]))
    #res += '%s                   # delimiter ???\n' % m_hex[(cur + 2) * 2: (cur + 4) * 2]
    return res


def unknown_part (bin_str):
    res = 'Hex    :  %s\n' % utils.str2hex(bin_str, '  ')
    res += 'String :   %s\n' % utils.str2prn_str(bin_str, '   ')
    res += 'Decimal: %s\n' % utils.str2dec(bin_str, ' ')
    return res


from wc.proxy import make_timer
# check for timed out nonces every 5 minutes
make_timer(300, check_nonces)
