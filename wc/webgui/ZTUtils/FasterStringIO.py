##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Fast append-only String I/O"""

from StringIO import StringIO

ustr = unicode

class FasterStringIO (StringIO):
    """Append-only version of StringIO.

    This let's us have a much faster write() method.
    """
    def close (self):
        if not self.closed:
            self.write = _write_ValueError
            StringIO.close(self)

    def seek (self, pos, mode=0):
        raise RuntimeError("FasterStringIO.seek() not allowed")

    def write (self, s):
        #assert self.pos == self.len
        if not isinstance(s, unicode):
            s = ustr(s)
        self.buflist.append(s)
        self.len = self.pos = self.pos + len(s)

def _write_ValueError (s):
    raise ValueError, "I/O operation on closed file"
