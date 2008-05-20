# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2008 Bastian Kleineidam
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
from ... import log, LOG_FILTER, levenshtein
from wc.HtmlParser.htmllib import quote_attrval

# tag ids
# XXX make enum
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
STARTENDTAG = 4

# tag part ids
# XXX make enum
TAG = 0        # the tag inclusive the <>
TAGNAME = 1    # the tag name
ATTR = 2       # a complete attribute
ATTRVAL = 3    # attribute value
ATTRNAME = 4   # attribute name
COMPLETE = 5   # start/end tag and content
ENCLOSED = 6   # only enclosed content
MATCHED = 7    # only matched content


def _startout (out, item, start=u"<", end=u">"):
    """
    Write given item data on output stream as HTML start tag.
    """
    out.write(start)
    out.write(item[1])
    for name, val in item[2].iteritems():
        out.write(u' %s' % name)
        if val is not None:
            out.write(u'="%s"' % quote_attrval(val))
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
            log.error(LOG_FILTER, "unknown buffer element %s", item[0])
    return out


# checker for namespaces
is_other_namespace = re.compile(r"^(?i)[-a-z_.]+:").search
# tag garbage filter
filter_tag_garbage = re.compile(r"(?P<tag>^[a-z][-a-z0-9.:_]*)").search

# HTML 4.01 tags
HtmlTags = set([
    "a",
    "abbr",
    "acronym",
    "address",
    "applet",
    "area",
    "b",
    "base",
    "basefont",
    "bdo",
    "big",
    "blockquote",
    "body",
    "br",
    "button",
    "caption",
    "center",
    "cite",
    "code",
    "col",
    "colgroup",
    "dd",
    "del",
    "dfn",
    "dir",
    "div",
    "dl",
    "dt",
    "em",
    "fieldset",
    "font",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "isindex",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "map",
    "menu",
    "meta",
    "noframes",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "pre",
    "q",
    "s",
    "samp",
    "script",
    "select",
    "small",
    "span",
    "strike",
    "strong",
    "style",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "tt",
    "u",
    "ul",
    "var",
])

# MathML tags
MathTags = set([
    "abs",
    "and",
    "annotation",
    "annotation-xml",
    "apply",
    "arccos",
    "arcsin",
    "arctan",
    "bvar",
    "ci",
    "cn",
    "compose",
    "condition",
    "conjugate",
    "cos",
    "cosh",
    "cot",
    "coth",
    "csc",
    "csch",
    "declare",
    "degree",
    "determinant",
    "diff",
    "divide",
    "eq",
    "exists",
    "exp",
    "factorial",
    "fn",
    "forall",
    "gcd",
    "geq",
    "gt",
    "ident",
    "implies",
    "in",
    "int",
    "intersect",
    "interval",
    "inverse",
    "lambda",
    "leq",
    "limit",
    "list",
    "ln",
    "log",
    "logbase",
    "lowlimit",
    "lt",
    "maction",
    "maligngroup",
    "malignmark",
    "math",
    "matrix",
    "matrixrow",
    "max",
    "mean",
    "median",
    "merror",
    "mfenced",
    "mfrac",
    "mi",
    "min",
    "minus",
    "mmultiscripts",
    "mn",
    "mo",
    "mode",
    "moment",
    "mover",
    "mpadded",
    "mphantom",
    "mprescripts",
    "mroot",
    "mrow",
    "ms",
    "mspace",
    "msqrt",
    "mstyle",
    "msub",
    "msubsup",
    "msup",
    "mtable",
    "mtd",
    "mtext",
    "mtr",
    "munder",
    "munderover",
    "neq",
    "none",
    "not",
    "notin",
    "notprsubset",
    "notsubset",
    "or",
    "partialdiff",
    "plus",
    "power",
    "product",
    "prsubset",
    "quotient",
    "reln",
    "rem",
    "root",
    "sdev",
    "sec",
    "sech",
    "selector",
    "semantics",
    "sep",
    "set",
    "setdiff",
    "sin",
    "sinh",
    "subset",
    "sum",
    "tan",
    "tanh",
    "tendsto",
    "times",
    "transpose",
    "union",
    "uplimit",
    "variance",
    "vector",
    "xor",
])

# old tags
OldTags = set([
    "bgsound", # IE 2.x-6.x
    "blink", # Netscape Navigator
    "embed", # Netscape Navigator 4
    "ilayer", # Netscape Navigator 4
    "keygen", # Netscape Navigator
    "layer", # Netscape Navigator 4
    "listing", # HTML 3.2
    "marquee", # IE 4.x
    "multicol", # Netscape Navigator 3
    "nobr", # Netscape Navigator 1.1
    "nbr", # deprecated, unknown origin
    "noembed", # Netscape Navigator 4
    "nolayer", # Netscape Navigator 4
    "plaintext", # HTML 3.2
    "spacer", # Netscape Navigator 3
    "wbr", # Netscape Navigator 1.1
    "xmp", # HTML 3.2
])

# known invalid tags (to prevent correction)
KnownInvalidTags = set([
    "cadv", # www.heise.de
    "contentbanner", # www.heise.de
    "forum", # www.heise.de
    "heiseadvert", # www.heise.de
    "heisetext", # www.heise.de
    "image", # imdb.com
    "skyscraper", # www.heise.de
    "u2uforen", # www.heise.de
    "update", # slashdot.org
    "htmlpromo", # www.pcworld.com
    "noindex", # atomz.com software
    "quote", # xhtml 2.0 (draft)
    "csscriptdict", # GoLive
    "csactiondict", # GoLive
    "csobj", # GoLive
    "x-claris-window", # Claris
    "x-claris-tagview", # Claris
    "x-sas-window", # Claris
    "nyt_copyright", # Times
])

# tags to ignore
IgnoreTags = HtmlTags | MathTags | OldTags | KnownInvalidTags
CheckTags = HtmlTags | OldTags | MathTags

def check_spelling (tag, url):
    """
    Check if tag (must be lowercase) is a valid HTML tag and if not,
    tries to correct it to the first tag with a levenshtein distance of 1.
    """
    if tag in IgnoreTags or is_other_namespace(tag):
        # do not check tag
        return tag
    # encode for levenshtein method
    # since tag names should be ascii anyway, ignore encoding errors
    enctag = tag.encode("ascii", "ignore")
    for htmltag in CheckTags:
        if levenshtein.distance(enctag, htmltag) == 1:
            log.info(LOG_FILTER,
                      "HTML tag %r corrected to %r at %r", tag, htmltag, url)
            return htmltag
    log.info(LOG_FILTER, "unknown HTML tag %r at %r", tag, url)
    # filter possibly trailing garbage the parser accepted
    mo = filter_tag_garbage(tag)
    if mo:
        return mo.group("tag")
    return tag
