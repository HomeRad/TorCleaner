# -*- coding: iso-8859-1 -*-
__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

__all__ = ["get_ntlm_challenge", "parse_ntlm_challenge",
           "get_ntlm_credentials", "parse_ntlm_credentials",
           "check_ntlm_credentials"]

import des, md4, utils, base64

# nonce dictionary
# XXX regularly delete nonces
nonces = {}

def get_ntlm_challenge (**attrs):
    """return initial challenge token for ntlm authentication"""
    ctype = attrs.get('type', 0)
    if ctype not in (0, 2):
        raise IOError("Invalid NTLM challenge type")
    if ctype==0:
        # initial challenge
        return "NTLM"
    if ctype==2:
        # after getting first credentials
        return "NTLM %s" % base64.encodestring(create_message2()).strip()


def parse_ntlm_challenge (challenge):
    res = {}
    if not challenge.startswith('NTLMSSP\x00'):
        return res, challenge
    res['nonce'] = challenge[24:32]
    return res, challenge[40:]


def get_ntlm_credentials (challenge, **attrs):
    ctype = attrs.get('type', 1)
    if ctype not in (1, 3):
        raise IOError("Invalid NTLM credentials type")
    if ctype==1:
        msg = create_message1()
    elif ctype==3:
        nonce = attrs['nonce']
        domain = attrs['domain']
        username = attrs['username']
        host = attrs['host']
        msg = create_message3(nonce, domain, username, host)
    return "NTLM %s" % base64.encodestring(msg).strip()


def get_ntlm_type3_message (**attrs):
    # extract the required attributes


def parse_ntlm_credentials (credentials):
    # XXX
    pass


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


def create_message2 (flags="\x82\x01"):
    protocol = 'NTLMSSP\x00'    #name
    type = '\x02'
    msglen = '\x28'
    nonce = "%08f" % (random.random()*10)
    assert nonce not in nonces
    nonces[nonce] = None
    zero2 = '\x00' * 2
    zero7 = '\x00' * 7
    zero8 = '\x00' * 8
    return "%(protocol)s%(type)s%(zero7)s%(msglen)s%(zero2)s%(nonce)s%(zero8)s" % locals()


def create_message3 (nonce, domain, username, host, flags="\x82\x01",
                     lm_hashed_pw=None, nt_hashed_pw=None,
                     ntlm_mode=0):
    protocol = 'NTLMSSP\000'            #name
    type = '\003\000'                   #type 3
    head = protocol + type + '\000\000'
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
    if nltm_mode == 0:
        domain_offset = domain_offset + 8 + len(flags)
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


def parse_message2 (msg2):
    msg2 = base64.decodestring(msg2)
    # protocol = msg2[0:7]
    # msg_type = msg2[7:9]
    nonce = msg2[24:32]
    return nonce


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


def debug_message1 (msg):
    m_ = base64.decodestring(msg)
    m_hex = utils.str2hex(m_)
    res = '==============================================================\n'
    res += 'NTLM Message 1 report:\n'
    res += '---------------------------------\n'
    res += 'Base64: %s\n' % msg
    res += 'String: %s\n' % utils.str2prn_str(m_)
    res += 'Hex: %s\n' % m_hex
    cur = 0
    res += '---------------------------------\n'
    cur_len = 12
    res += 'Header %d/%d:\n%s\n\n' % (cur, cur_len, m_hex[0:24])
    res += '%s\nmethod name 0/8\n%s               # C string\n\n' % (m_hex[0:16], utils.str2prn_str(m_[0:8]))
    res += '0x%s%s                 # message type\n' % (m_hex[18:20], m_hex[16:18])
    res += '%s                   # delimiter (zeros)\n' % m_hex[20:24]
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 4
    res += 'Flags %d/%d\n' % (cur, cur_len)
    res += flags(m_[cur: cur + cur_len])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = len(m_) - cur
    res += 'Rest of the message %d/%d:\n' % (cur, cur_len)
    res += unknown_part(m_[cur: cur + cur_len])
    res += '\nEnd of message 1 report.\n'
    return res


def debug_message2 (msg):
    m_ = base64.decodestring(msg)
    m_hex = utils.str2hex(m_)
    res = '==============================================================\n'
    res += 'NTLM Message 2 report:\n'
    res += '---------------------------------\n'
    res += 'Base64: %s\n' % msg
    res += 'String: %s\n' % utils.str2prn_str(m_)
    res += 'Hex: %s\n' % m_hex
    cur = 0
    res += '---------------------------------\n'
    cur_len = 12
    res += 'Header %d/%d:\n%s\n\n' % (cur, cur_len, m_hex[0:24])
    res += '%s\nmethod name 0/8\n%s               # C string\n\n' % (m_hex[0:16], utils.str2prn_str(m_[0:8]))
    res += '0x%s%s                 # message type\n' % (m_hex[18:20], m_hex[16:18])
    res += '%s                   # delimiter (zeros)\n' % m_hex[20:24]
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 8
    res += 'Lengths and Positions %d/%d\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2])
    cur_len = 8
    res += 'Domain ??? %d/%d\n' % (cur, cur_len)
    dom = item(m_[cur:cur+cur_len])
    res += dom['string']
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 4
    res += 'Flags %d/%d\n' % (cur, cur_len)
    res += flags(m_[cur: cur + cur_len])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 8
    res += 'NONCE %d/%d\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = dom['offset'] - cur
    res += 'Unknown data %d/%d:\n' % (cur, cur_len)
    res += unknown_part(m_[cur: cur + cur_len])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = dom['len1']
    res += 'Domain ??? %d/%d:\n' % (cur, cur_len)
    res += 'Hex: %s\n' % m_hex[cur * 2: (cur + cur_len) * 2]
    res += 'String: %s\n\n' % utils.str2prn_str(m_[cur : cur + cur_len])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = len(m_) - cur
    res += 'Rest of the message %d/%d:\n' % (cur, cur_len)
    res += unknown_part(m_[cur: cur + cur_len])
    res += '\nEnd of message 2 report.\n'
    return res


def debug_message3 (msg):
    m_ = base64.decodestring(msg)
    m_hex = utils.str2hex(m_)
    res = '==============================================================\n'
    res += 'NTLM Message 3 report:\n'
    res += '---------------------------------\n'
    res += 'Base64: %s\n' % msg
    res += 'String: %s\n' % utils.str2prn_str(m_)
    res += 'Hex: %s\n' % m_hex
    cur = 0
    res += '---------------------------------\n'
    cur_len = 12
    res += 'Header %d/%d:\n%s\n\n' % (cur, cur_len, m_hex[0:24])
    res += '%s\nmethod name 0/8\n%s               # C string\n\n' % (m_hex[0:16], utils.str2prn_str(m_[0:8]))
    res += '0x%s%s                 # message type\n' % (m_hex[18:20], m_hex[16:18])
    res += '%s                   # delimiter (zeros)\n' % m_hex[20:24]
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 48
    res += 'Lengths and Positions %d/%d\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2])
    cur_len = 8
    res += 'LAN Manager response %d/%d\n' % (cur, cur_len)
    lmr = item(m_[cur:cur+cur_len])
    res += lmr['string']
    cur += cur_len
    cur_len = 8
    res += 'NT response %d/%d\n' % (cur, cur_len)
    ntr = item(m_[cur:cur+cur_len])
    res += ntr['string']
    cur += cur_len
    cur_len = 8
    res += 'Domain string %d/%d\n' % (cur, cur_len)
    dom = item(m_[cur:cur+cur_len])
    res += dom['string']
    cur += cur_len
    cur_len = 8
    res += 'User string %d/%d\n' % (cur, cur_len)
    username = item(m_[cur:cur+cur_len])
    res += username['string']
    cur += cur_len
    cur_len = 8
    res += 'Host string %d/%d\n' % (cur, cur_len)
    host = item(m_[cur:cur+cur_len])
    res += host['string']
    cur += cur_len
    cur_len = 8
    res += 'Unknow item record %d/%d\n' % (cur, cur_len)
    unknown = item(m_[cur:cur+cur_len])
    res += unknown['string']
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = 4
    res += 'Flags %d/%d\n' % (cur, cur_len)
    res += flags(m_[cur: cur + cur_len])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = dom['len1'] + user['len1'] + host['len1']
    res += 'Domain, User, Host strings %d/%d\n%s\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2], utils.str2prn_str(m_[cur:cur + cur_len]))
    cur_len = dom['len1']
    res += '%s\n' % m_hex[cur * 2: (cur + cur_len) * 2]
    res += 'Domain name %d/%d:\n' % (cur, cur_len)
    res += '%s\n\n' % (utils.str2prn_str(m_[cur: (cur + cur_len)]))
    cur += cur_len
    cur_len = user['len1']
    res += '%s\n' % m_hex[cur * 2: (cur + cur_len) * 2]
    res += 'User name %d/%d:\n' % (cur, cur_len)
    res += '%s\n\n' % (utils.str2prn_str(m_[cur: (cur + cur_len)]))
    cur += cur_len
    cur_len = host['len1']
    res += '%s\n' % m_hex[cur * 2: (cur + cur_len) * 2]
    res += 'Host name %d/%d:\n' % (cur, cur_len)
    res += '%s\n\n' % (utils.str2prn_str(m_[cur: (cur + cur_len)]))
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = lmr['len1']
    res += 'LAN Manager response %d/%d\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = ntr['len1']
    res += 'NT response %d/%d\n%s\n\n' % (cur, cur_len, m_hex[cur * 2 :(cur + cur_len) * 2])
    cur += cur_len
    res += '---------------------------------\n'
    cur_len = len(m_) - cur
    res += 'Rest of the message %d/%d:\n' % (cur, cur_len)
    res += unknown_part(m_[cur: cur + cur_len])
    res += '\nEnd of message 3 report.\n'
    return res

