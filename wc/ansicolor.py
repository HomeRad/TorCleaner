# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2005  Bastian Kleineidam
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
"""
ANSI Color definitions and functions.

From Term::ANSIColor, applies also to this module:

The codes generated by this module are standard terminal control codes,
complying with ECMA-48 and ISO 6429 (generally referred to as ``ANSI color''
for the color codes). The non-color control codes (bold, dark, italic,
underline, and reverse) are part of the earlier ANSI X3.64 standard for
control sequences for video terminals and peripherals.

Note that not all displays are ISO 6429-compliant, or even X3.64-compliant
(or are even attempting to be so). This module will not work as expected on
displays that do not honor these escape sequences, such as cmd.exe, 4nt.exe,
and command.com under either Windows NT or Windows 2000. They may just be
ignored, or they may display as an ESC character followed by some apparent
garbage.

Jean Delvare provided the following table of different common terminal
emulators and their support for the various attributes and others have
helped me flesh it out::

              clear    bold     dark    under    blink   reverse  conceal
 ------------------------------------------------------------------------
 xterm         yes      yes      no      yes     bold      yes      yes
 linux         yes      yes      yes    bold      yes      yes      no
 rxvt          yes      yes      no      yes  bold/black   yes      no
 dtterm        yes      yes      yes     yes    reverse    yes      yes
 teraterm      yes    reverse    no      yes    rev/red    yes      no
 aixterm      kinda   normal     no      yes      no       yes      yes
 PuTTY         yes     color     no      yes      no       yes      no
 Windows       yes      no       no      no       no       yes      no
 Cygwin SSH    yes      yes      no     color    color    color     yes

Windows is Windows telnet, and Cygwin SSH is the OpenSSH implementation under
Cygwin on Windows NT. Where the entry is other than yes or no, that
emulator displays the given attribute as something else instead. Note that
on an aixterm, clear doesn't reset colors; you have to explicitly set the
colors back to what you want. More entries in this table are welcome.

Note that codes 3 (italic), 6 (rapid blink), and 9 (strikethrough) are
specified in ANSI X3.64 and ECMA-048 but are not commonly supported by
most displays and emulators and therefore aren't supported by this module
at the present time. ECMA-048 also specifies a large number of other
attributes, including a sequence of attributes for font changes, Fraktur
characters, double-underlining, framing, circling, and overlining. As none
of these attributes are widely supported or useful, they also aren't
currently supported by this module.

SEE ALSO

ECMA-048 is available on-line (at least at the time of this writing) at
http://www.ecma-international.org/publications/standards/ECMA-048.HTM.

ISO 6429 is available from ISO for a charge; the author of this module does
not own a copy of it. Since the source material for ISO 6429 was ECMA-048
and the latter is available for free, there seems little reason to obtain
the ISO standard.

The current version of this module is always available from its web site at
http://www.eyrie.org/~eagle/software/ansicolor/. It is also part of the Perl
core distribution as of 5.6.0.
"""

import os
import logging
import types

# Escape for ANSI colors
AnsiEsc = "\x1b[%sm"

# type numbers
AnsiType = {
    'bold':      '1',
    'light':     '2',
    'underline': '4',
    'blink':     '5',
    'invert':    '7',
    'concealed': '8',
}

# color numbers; capitalized colors are inverse
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


def has_colors (fp):
    """
    Test if given file is an ANSI color enabled tty.
    """
    # note: the isatty() function ensures that we do not colorize
    # redirected streams, as this is almost never what we want
    if hasattr(fp, "isatty") and fp.isatty():
        if os.name == 'nt':
            # XXX disabled for windows platforms
            return False
            #return has_colors_nt()
        try:
            import curses
            curses.setupterm()
            if curses.tigetnum("colors") >= 8:
                # more than 8 colors: allright!
                return True
        except ImportError:
            # no curses :(
            pass
    return False


def has_colors_nt ():
    """
    Check if running in a Windows environment which supports ANSI colors.
    Do this by searching for a loaded ANSI driver.
    """
    _in = None
    _out = None
    try:
        _in, _out = os.popen4("mem /c")
        line = _out.readline()
        while line:
            if "ANSI" in line:
                return True
            line = _out.readline()
        return False
    finally:
        if _in is not None:
            _in.close()
        if _out is not None:
            _out.close()


def colorize (text, color=None):
    """
    Colorize text with given color. If color is None, leave the
    text as-is.
    """
    if color is not None:
        return '%s%s%s' % (esc_ansicolor(color), text, AnsiReset)
    else:
        return text


class Colorizer (object):
    """
    Prints colored messages to streams.
    """

    def __init__ (self, fp):
        """
        Initialize with given stream (file-like object).
        """
        super(Colorizer, self).__init__()
        self._fp = fp

    def write (self, s, color=None):
        """
        Writes message s in color if output stream is
        a console stream (stderr or stdout).
        Else writes without color (i.e. black/white).
        """
        if has_colors(self._fp):
            # stdout or stderr can be colorized
            s = colorize(s, color=color)
        self._fp.write(s)

    def __getattr__ (self, name):
        """
        Delegate attribute access to the stored stream object.
        """
        return getattr(self._fp, name)


class ColoredStreamHandler (logging.StreamHandler, object):
    """Send colored log messages to streams (file-like objects)."""

    def __init__ (self, strm=None):
        """
        Log to given stream (a file-like object) or to stderr if
        strm is None.
        """
        super(ColoredStreamHandler, self).__init__(strm=strm)
        self.stream = Colorizer(self.stream)
        # standard log level colors (used by get_color)
        self.colors = {
            logging.WARN: 'bold;yellow',
            logging.ERROR: 'light;red',
            logging.CRITICAL: 'bold;red',
            logging.DEBUG: 'white',
        }

    def get_color (self, record):
        """
        Get appropriate color according to log level.
        """
        return self.colors.get(record.levelno, 'default')

    def emit (self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline
        [N.B. this may be removed depending on feedback].
        """
        color = self.get_color(record)
        msg = self.format(record)
        if not hasattr(types, "UnicodeType"): #if no unicode support...
            self.stream.write("%s" % msg, color=color)
        else:
            try:
                self.stream.write("%s" % msg, color=color)
            except UnicodeError:
                self.stream.write("%s" % msg.encode("UTF-8"),
                                  color=color)
        self.stream.write(os.linesep)
        self.flush()
