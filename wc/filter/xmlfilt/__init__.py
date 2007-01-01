# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2007 Bastian Kleineidam
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
Numeric constants for XML/HTML document parts.
"""

import wc.log
import wc.XmlUtils

# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
STARTENDTAG = 4
STARTDOCUMENT = 5
ENDDOCUMENT = 6
CDATA = 7
INSTRUCTION = 8

def _startout (out, item, start=u"<", end=u">"):
    """
    Write given item data on output stream as HTML start tag.
    """
    quote = wc.XmlUtils.xmlquote
    quoteattr = wc.XmlUtils.xmlquoteattr
    out.write(start)
    out.write(quote(item[1]))
    for name, val in item[2].iteritems():
        out.write(u' %s="%s"' % (quote(name), quoteattr(val)))
    out.write(end)


def tagbuf2data (tagbuf, out, entities=None):
    """
    Write tag buffer items to output stream out and returns out.
    """
    for item in tagbuf:
        if item[0] == DATA:
            out.write(wc.XmlUtils.xmlquote(item[1]))
        elif item[0] == CDATA:
            # ']]>' must not occur in item[1]
            out.write(u"<![CDATA[%s]]>" % item[1])
        elif item[0] == STARTTAG:
            _startout(out, item)
        elif item[0] == ENDTAG:
            out.write(u"</%s>" % item[1])
        elif item[0] == COMMENT:
            out.write(u"<!--%s-->" % item[1])
        elif item[0] == STARTENDTAG:
            _startout(out, item, end=u"/>")
        elif item[0] == STARTDOCUMENT:
            _startout(out, item, start=u"<?", end=u"?>\n")
        elif item[0] == INSTRUCTION:
            out.write(u"<?%s %s?>\n" % (item[1], item[2]))
        else:
            wc.log.error(wc.LOG_FILTER, "unknown buffer element %s", item[0])
    return out
