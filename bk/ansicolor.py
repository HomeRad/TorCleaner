# -*- coding: iso-8859-1 -*-
"""ANSI Color definitions and functions"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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

import os

# Escape for ANSI colors
AnsiEsc="\x1b[%sm"

# type numbers
AnsiType = {
    'bold':      '1',
    'light':     '2',
    'underline': '4',
    'blink':     '5',
    'invert':    '7',
    'concealed': '8',
}

# color numbers
AnsiColor = {
    'default': '0',
    'black':   '30',
    'red':     '31',
    'green':   '32',
    'yellow':  '33',
    'blue':    '34',
    'purple':  '35',
    'cyan':    '36',
    'white':   '37',
    'Black':   '40',
    'Red':     '41',
    'Green':   '42',
    'Yellow':  '43',
    'Blue':    '44',
    'Purple':  '45',
    'Cyan':    '46',
    'White':   '47',

}


# pc speaker beep escape code
Beep = "\007"


def esc_ansicolor (color):
    """convert a named color definition to an escaped ANSI color"""
    ctype = ''
    if ";" in color:
        ctype, color = color.split(";", 1)
        ctype = AnsiType.get(ctype, '')+";"
    cnum = AnsiColor.get(color, '0')
    return AnsiEsc % (ctype+cnum)

AnsiReset = esc_ansicolor("default")


def colorize (text, color=None):
    """return text colorized if TERM is set"""
    if (color is not None) and os.environ.get('TERM'):
        color = esc_ansicolor(color)
        return '%s%s%s' % (color, text, AnsiReset)
    else:
        return text