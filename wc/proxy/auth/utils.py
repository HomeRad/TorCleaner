# -*- coding: iso-8859-1 -*-
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

hd = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F',]


def str2hex_num (s):
    res = 0L
    for i in s:
        res = res << 8
        res += long(ord(i))
    return hex(res)


def str2hex (s, delimiter=''):
    res = ''
    for i in s:
        o = ord(i)
        b = o/16
        res += hd[b]
        res += hd[o - (b * 16)]
        res += delimiter
    return res


def str2dec (s, delimiter=''):
    res = ''
    for i in s:
        res += '%3d' % ord(i)
        res += delimiter
    return res


def hex2str (hex_str):
    res = ''
    for i in range(0, len(hex_str), 2):
        res += chr(hd.index(hex_str[i]) * 16 + hd.index(hex_str[i+1]))
    return res


def str2prn_str (bin_str, delimiter=''):
    ""
    res = ''
    for i in bin_str:
        if ord(i) > 31:
            res += i
        else:
            res += '.'
        res += delimiter
    return res


def byte2bin_str (char):
    ""
    res = ''
    t = ord(char)
    while t > 0:
        t1 = t / 2
        if t != 2 * t1:
            res = '1' + res
        else:
            res = '0' + res
        t = t1
    if len(res) < 8:
        res = '0' * (8 - len(res)) + res
    return res


def str2lst (s):
    return [ ord(i) for i in s ]


def lst2str (lst):
    return "".join([chr(i & 0xFF) for i in lst])


def int2chrs (number_int):
    return chr(number_int & 0xFF) + chr((number_int >> 8) & 0xFF)


def bytes2int (bytes):
    return ord(bytes[1]) * 256 + ord(bytes[0])


def int2hex_str (number_int16):
    res = '0x'
    ph = int(number_int16) / 256
    res += hd[ph/16]
    res += hd[ph - ((ph/16) * 16)]
    pl = int(number_int16) - (ph * 256)
    res += hd[pl/16]
    res += hd[pl - ((pl/16) * 16)]
    return res


def str2unicode (s):
    "converts ascii string to dumb unicode"
    return "".join([ c+'\x00' for c in s ])


def unicode2str (s):
    """converts dumb unicode back to ascii string"""
    return s[::2]


def _test ():
    s = "abc"
    print `str2hex_num(s)`
    print `str2hex(s)`
    print `hex2str(str2hex(s))`
    print `hex2str("65")`

if __name__=='__main__':
    _test()
