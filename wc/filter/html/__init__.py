# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
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
Check for typos in HTML tags.
"""

import re
import wc.levenshtein
import wc.HtmlParser.htmllib
import wc.log

# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
STARTENDTAG = 4

# tag part ids
TAG = 0        # the tag inclusive the <>
TAGNAME = 1    # the tag name
ATTR = 2       # a complete attribute
ATTRVAL = 3    # attribute value
ATTRNAME = 4   # attribute name
COMPLETE = 5   # start/end tag and content
ENCLOSED = 6   # only enclosed content


def _startout (out, item, start=u"<", end=u">"):
    """
    Write given item data on output stream as HTML start tag.
    """
    out.write(start)
    out.write(item[1])
    for name, val in item[2].items():
        out.write(u' %s' % name)
        if val:
            out.write(u'="%s"' % wc.HtmlParser.htmllib.quote_attrval(val))
    out.write(end)


def tagbuf2data (tagbuf, out, entities=None):
    """
    Write tag buffer items to output stream out and returns out.
    """
    for item in tagbuf:
        if item[0] == DATA:
            out.write(item[1])
        elif item[0] == STARTTAG:
            _startout(out, item)
        elif item[0] == STARTENDTAG:
            _startout(out, item, end=u"/>")
        elif item[0] == ENDTAG:
            out.write(u"</%s>" % item[1])
        elif item[0] == COMMENT:
            out.write(u"<!--%s-->" % item[1])
        else:
            wc.log.error(wc.LOG_FILTER, "unknown buffer element %s", item[0])
    return out


# checker for namespaces
is_other_namespace = re.compile(r"^(?i)[-a-z_.]+:").search
# tag garbage filter
filter_tag_garbage = re.compile(r"(?P<tag>^[a-z][-a-z0-9.:_]*)").search

# HTML 4.01 tags
HtmlTags = {
    "a" : None,
    "abbr" : None,
    "acronym" : None,
    "address" : None,
    "applet" : None,
    "area" : None,
    "b" : None,
    "base" : None,
    "basefont" : None,
    "bdo" : None,
    "big" : None,
    "blockquote" : None,
    "body" : None,
    "br" : None,
    "button" : None,
    "caption" : None,
    "center" : None,
    "cite" : None,
    "code" : None,
    "col" : None,
    "colgroup" : None,
    "dd" : None,
    "del" : None,
    "dfn" : None,
    "dir" : None,
    "div" : None,
    "dl" : None,
    "dt" : None,
    "em" : None,
    "fieldset" : None,
    "font" : None,
    "form" : None,
    "frame" : None,
    "frameset" : None,
    "h1" : None,
    "h2" : None,
    "h3" : None,
    "h4" : None,
    "h5" : None,
    "h6" : None,
    "head" : None,
    "hr" : None,
    "html" : None,
    "i" : None,
    "iframe" : None,
    "img" : None,
    "input" : None,
    "ins" : None,
    "isindex" : None,
    "kbd" : None,
    "label" : None,
    "legend" : None,
    "li" : None,
    "link" : None,
    "map" : None,
    "menu" : None,
    "meta" : None,
    "noframes" : None,
    "noscript" : None,
    "object" : None,
    "ol" : None,
    "optgroup" : None,
    "option" : None,
    "p" : None,
    "param" : None,
    "pre" : None,
    "q" : None,
    "s" : None,
    "samp" : None,
    "script" : None,
    "select" : None,
    "small" : None,
    "span" : None,
    "strike" : None,
    "strong" : None,
    "style" : None,
    "sub" : None,
    "sup" : None,
    "table" : None,
    "tbody" : None,
    "td" : None,
    "textarea" : None,
    "tfoot" : None,
    "th" : None,
    "thead" : None,
    "title" : None,
    "tr" : None,
    "tt" : None,
    "u" : None,
    "ul" : None,
    "var" : None,
}

# MathML tags
MathTags = {
    "abs" : None,
    "and" : None,
    "annotation" : None,
    "annotation-xml" : None,
    "apply" : None,
    "arccos" : None,
    "arcsin" : None,
    "arctan" : None,
    "bvar" : None,
    "ci" : None,
    "cn" : None,
    "compose" : None,
    "condition" : None,
    "conjugate" : None,
    "cos" : None,
    "cosh" : None,
    "cot" : None,
    "coth" : None,
    "csc" : None,
    "csch" : None,
    "declare" : None,
    "degree" : None,
    "determinant" : None,
    "diff" : None,
    "divide" : None,
    "eq" : None,
    "exists" : None,
    "exp" : None,
    "factorial" : None,
    "fn" : None,
    "forall" : None,
    "gcd" : None,
    "geq" : None,
    "gt" : None,
    "ident" : None,
    "implies" : None,
    "in" : None,
    "int" : None,
    "intersect" : None,
    "interval" : None,
    "inverse" : None,
    "lambda" : None,
    "leq" : None,
    "limit" : None,
    "list" : None,
    "ln" : None,
    "log" : None,
    "logbase" : None,
    "lowlimit" : None,
    "lt" : None,
    "maction" : None,
    "maligngroup" : None,
    "malignmark" : None,
    "math" : None,
    "matrix" : None,
    "matrixrow" : None,
    "max" : None,
    "mean" : None,
    "median" : None,
    "merror" : None,
    "mfenced" : None,
    "mfrac" : None,
    "mi" : None,
    "min" : None,
    "minus" : None,
    "mmultiscripts" : None,
    "mn" : None,
    "mo" : None,
    "mode" : None,
    "moment" : None,
    "mover" : None,
    "mpadded" : None,
    "mphantom" : None,
    "mprescripts" : None,
    "mroot" : None,
    "mrow" : None,
    "ms" : None,
    "mspace" : None,
    "msqrt" : None,
    "mstyle" : None,
    "msub" : None,
    "msubsup" : None,
    "msup" : None,
    "mtable" : None,
    "mtd" : None,
    "mtext" : None,
    "mtr" : None,
    "munder" : None,
    "munderover" : None,
    "neq" : None,
    "none" : None,
    "not" : None,
    "notin" : None,
    "notprsubset" : None,
    "notsubset" : None,
    "or" : None,
    "partialdiff" : None,
    "plus" : None,
    "power" : None,
    "product" : None,
    "prsubset" : None,
    "quotient" : None,
    "reln" : None,
    "rem" : None,
    "root" : None,
    "sdev" : None,
    "sec" : None,
    "sech" : None,
    "selector" : None,
    "semantics" : None,
    "sep" : None,
    "set" : None,
    "setdiff" : None,
    "sin" : None,
    "sinh" : None,
    "subset" : None,
    "sum" : None,
    "tan" : None,
    "tanh" : None,
    "tendsto" : None,
    "times" : None,
    "transpose" : None,
    "union" : None,
    "uplimit" : None,
    "variance" : None,
    "vector" : None,
    "xor" : None,
}

# old tags
OldTags = {
    "bgsound": None, # IE 2.x-6.x
    "blink" : None, # Netscape Navigator
    "embed" : None, # Netscape Navigator 4
    "ilayer" : None, # Netscape Navigator 4
    "keygen" : None, # Netscape Navigator
    "layer" : None, # Netscape Navigator 4
    "listing" : None, # HTML 3.2
    "marquee" : None, # IE 4.x
    "multicol" : None, # Netscape Navigator 3
    "nobr" : None, # Netscape Navigator 1.1
    "nbr" : None, # deprecated, unknown origin
    "noembed" : None, # Netscape Navigator 4
    "nolayer" : None, # Netscape Navigator 4
    "plaintext" : None, # HTML 3.2
    "spacer" : None, # Netscape Navigator 3
    "wbr" : None, # Netscape Navigator 1.1
    "xmp" : None, # HTML 3.2
}

# known invalid tags (to prevent correction)
KnownInvalidTags = {
    "cadv" : None, # www.heise.de
    "contentbanner" : None, # www.heise.de
    "forum" : None, # www.heise.de
    "heiseadvert" : None, # www.heise.de
    "heisetext" : None, # www.heise.de
    "image": None, # imdb.com
    "skyscraper" : None, # www.heise.de
    "u2uforen" : None, # www.heise.de
    "update" : None, # slashdot.org
    "htmlpromo" : None, # www.pcworld.com
    "noindex": None, # atomz.com software
    "quote": None, # xhtml 2.0 (draft)
}


def check_spelling (tag, url):
    """
    Check if tag (must be lowercase) is a valid HTML tag and if not,
    tries to correct it to the first tag with a levenshtein distance of 1.
    """
    if tag in HtmlTags or tag in MathTags:
        return tag
    if tag in OldTags:
        #wc.log.warn(wc.LOG_FILTER, "non-HTML4 tag %r at %r", tag, url)
        return tag
    if tag in KnownInvalidTags:
        #wc.log.warn(wc.LOG_FILTER, "known invalid tag %r at %r", tag, url)
        return tag
    if is_other_namespace(tag):
        # ignore other namespaces
        return tag
    # encode for levenshtein method
    # since tag names should be ascii anyway, ignore encoding errors
    enctag = tag.encode("ascii", "ignore")
    for htmltag in HtmlTags.keys()+OldTags.keys()+MathTags.keys():
        if wc.levenshtein.distance(enctag, htmltag) == 1:
            wc.log.warn(wc.LOG_FILTER,
                      "HTML tag %r corrected to %r at %r", tag, htmltag, url)
            return htmltag
    wc.log.warn(wc.LOG_FILTER, "unknown HTML tag %r at %r", tag, url)
    # filter possibly trailing garbage the parser accepted
    mo = filter_tag_garbage(tag)
    if mo:
        return mo.group("tag")
    return tag

