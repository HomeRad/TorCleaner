# -*- coding: iso-8859-1 -*-
"""convert"""
#    Convert - Python module to convert number and data type
#
#    Copyright (C) 2002 Thomas Mangin
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys

_oct='01234567'
_dec='0123456789'
_hex='0123456789abcdefABCDEF'

_size = { 10:0, 8:1, 16:2 }

# Assume that the string have the appropriate length for tests

def _is_cross (char):
    return char in "xX"

def _is_digit_start (char):
    return char in "0\\"

def _is_oct_digit (char):
    return char in _oct

def _is_dec_digit (char):
    return char in _dec

def _is_hex_digit (char):
    return char in _hex


def _is_oct_start (text):
    return _is_digit_start(text[0]) and _is_oct_digit(text[1])

def _is_dec_start (text):
    return _is_dec_digit(text[0])

def _is_hex_start (text):
    return _is_digit_start(text[0]) and _is_cross(text[1]) and  _is_hex_digit(text[2])


def _is_number_start (text):
    # The order of the test are important as they can raise exceptions
    return _is_dec_start(text) or \
           _is_oct_start(text) or \
           _is_hex_start(text)

# End of Assume

def base10 (text, base):
    number = str(text).lower()
    result = 0L
    for digit in number:
        result *= base
        pos = _hex.index(digit)
        result += pos
    return result


def which_base (text):
    # return the base in (8,10,16) or 0 if not a number
    length = len(text)
    text.lower()
    if length > 2 and _is_hex_start(text):
        return 16
    if length > 1 and _is_oct_start(text):
        return 8
    if length > 0 and _is_dec_start(text):
        return 10
    return 0


def start_base (text):
    return which_base(text) != 0


def size_base (base):
    return _size[base]


def size_number (text):
    text = text.lower()
    base = which_base(text)
    if base == 0:
        return 0
    length = len(text)
    size = size_base(base)
    end = size+1
    while end < length and text[end] in _hex[:base]:
        end += 1
    return end-size


def index_number (text):
    index = 0
    try:
        while True:
            if _is_number_start(text[index:]):
                break
            index += 1
    except IndexError:
        # for the offstring access
        index = -1
    return index


def convert (text):
    base = which_base(text)
    start = size_base(base)
    end = start+size_number(text)
    return base10(text[start:end], base)


# Special function to extract numbers from strings
# Should not be really be here !

def is_final_dash (text):
    if len(text) < 2:
        return text[-1] == '\\'
    else:
        return text[-1] == '\\' and text[-2] != '\\'

def is_c_escape (text):
    if len(text) < 2:
        return False
    elif text[0] != '\\':
        return False
    # I am probably missing some but do not have C book nearby
    if text[1] in "nrb0":
        return True
    return False


# End special function

def little2 (number):
    low = ord(number[0])
    high = ord(number[1])
    return (high << 8) + low


def little4 (number):
    low = long(little2(number))
    high = long(little2(number[2:]))
    return (high << 16) + low


def big2 (number):
    low = ord(number[1])
    high = ord(number[0])
    return (high << 8) + low


def big4 (number):
    low = long(big2(number[2:]))
    high = long(big2(number))
    return (high << 16) + low


def local2 (number):
    if sys.byteorder == 'big':
        return big2(number)
    return little2(number)


def local4 (number):
    if sys.byteorder == 'big':
        return big4(number)
    return little4(number)

