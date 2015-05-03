# -*- coding: iso-8859-1 -*-
# Copyright (C) 2002 Thomas Mangin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# modified by Bastian Kleineidam <calvin@users.sourceforge.net>
"""
Convert number and data type.
"""
import sys
import re


#_oct = '01234567'
#_dec = '0123456789'
_hex = '0123456789abcdefABCDEF'

_is_oct_start = re.compile(r"^[0\\][1-7]").match
_is_dec_start = re.compile(r"^([1-9]|0$)").match
_is_hex_start = re.compile(r"^[0\\][xX][1-9a-fA-F]").match
_is_number_start = re.compile(r"^([0\\]([1-7]|[xX][1-9a-fA-F])|[1-9])").match


def which_base(text):
    """
    Return the base of string number in (8,10,16) or 0 if not a number.
    """
    if _is_hex_start(text):
        return 16
    if _is_dec_start(text):
        return 10
    if _is_oct_start(text):
        return 8
    return 0


_size = {10:0, 8:1, 16:2}
def size_base(base):
    return _size[base]


def size_number(text):
    text = text.lower()
    base = which_base(text)
    if base == 0:
        return 0
    length = len(text)
    size = size_base(base)
    end = size + 1
    while end < length and text[end] in _hex[:base]:
        end += 1
    return end-size


def index_number(text):
    for index in xrange(len(text)):
        if _is_number_start(text[index:]) or not text[index:]:
            return index
    return -1


def convert(text):
    base = which_base(text)
    if base == 0:
        return text
    start = size_base(base)
    end = start + size_number(text)
    return int(text[start:end], base)


# Special function to extract numbers from strings
# Should not be really be here !

def is_final_dash(text):
    if len(text) < 2:
        return text[-1] == '\\'
    else:
        return text[-1] == '\\' and text[-2] != '\\'


def is_c_escape(text):
    if len(text) < 2:
        return False
    elif text[0] != '\\':
        return False
    # I am probably missing some but do not have C book nearby
    if text[1] in "ftvnrb0":
        return True
    return False


# End special function

def little2(number):
    low = ord(number[0])
    high = ord(number[1])
    return (high << 8) + low


def little4(number):
    low = long(little2(number))
    high = long(little2(number[2:]))
    return (high << 16) + low


def big2(number):
    low = ord(number[1])
    high = ord(number[0])
    return (high << 8) + low


def big4(number):
    low = long(big2(number[2:]))
    high = long(big2(number))
    return (high << 16) + low


def local2(number):
    if sys.byteorder == 'big':
        return big2(number)
    return little2(number)


def local4(number):
    if sys.byteorder == 'big':
        return big4(number)
    return little4(number)
