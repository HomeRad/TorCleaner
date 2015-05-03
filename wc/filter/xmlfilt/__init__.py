# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Numeric constants for XML/HTML document parts.
"""

from ... import log, LOG_XML
from wc.XmlUtils import xmlquote, xmlquoteattr

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

def _startout(out, item, start=u"<", end=u">"):
    """
    Write given item data on output stream as HTML start tag.
    """
    out.write(start)
    out.write(xmlquote(item[1]))
    for name, val in item[2].iteritems():
        if val is None:
            out.write(u' %s' % xmlquote(name))
        else:
            out.write(u' %s="%s"' % (xmlquote(name), xmlquoteattr(val)))
    out.write(end)


def tagbuf2data(tagbuf, out, entities=None):
    """
    Write tag buffer items to output stream out and returns out.
    """
    for item in tagbuf:
        if item[0] == DATA:
            out.write(xmlquote(item[1]))
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
            log.error(LOG_XML, "unknown buffer element %s", item[0])
    return out
