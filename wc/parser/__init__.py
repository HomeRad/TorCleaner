"""Fast HTML parser module written in C"""
# Copyright (C) 2000-2002  Bastian Kleineidam
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import re

def _resolve_entity (mo):
    """resolve one &#XXX; entity"""
    # convert to number
    ent = mo.group()
    num = mo.group("num")
    if ent.startswith('#x'):
        radix = 16
    else:
        radix = 10
    num = int(num, radix)
    # check ASCII char range
    if 0<=num<=255:
        return chr(num)
    # not in range
    return ent


def resolve_entities (s):
    """resolve &#XXX; entities"""
    return re.sub(r'(?i)&#x?(?P<num>\d+);', _resolve_entity, s)


def _test ():
    print resolve_entities("&#%d;"%ord('a'))

if __name__=='__main__':
    _test()
