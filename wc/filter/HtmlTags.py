"""check for typos in HTML tags."""
# Copyright (C) 2003  Bastian Kleineidam
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

import sys
if __name__=='__main__':
    import os
    sys.path.insert(0, os.getcwd())
from wc.levenshtein import distance

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
    "mspace" : None,
    "mprescripts" : None,
    "none" : None,
    "malignmark" : None,
    "maligngroup" : None,
    "sep" : None,
    "inverse" : None,
    "ident" : None,
    "compose" : None,
    "exp" : None,
    "abs" : None,
    "conjugate" : None,
    "factorial" : None,
    "minus" : None,
    "quotient" : None,
    "divide" : None,
    "power" : None,
    "rem" : None,
    "plus" : None,
    "max" : None,
    "min" : None,
    "times" : None,
    "gcd" : None,
    "root" : None,
    "exists" : None,
    "forall" : None,
    "and" : None,
    "or" : None,
    "xor" : None,
    "not" : None,
    "implies" : None,
    "log" : None,
    "int" : None,
    "diff" : None,
    "partialdiff" : None,
    "ln" : None,
    "setdiff" : None,
    "union" : None,
    "intersect" : None,
    "sum" : None,
    "product" : None,
    "limit" : None,
    "sin" : None,
    "cos" : None,
    "tan" : None,
    "sec" : None,
    "csc" : None,
    "cot" : None,
    "sinh" : None,
    "cosh" : None,
    "tanh" : None,
    "sech" : None,
    "csch" : None,
    "coth" : None,
    "arcsin" : None,
    "arccos" : None,
    "arctan" : None,
    "mean" : None,
    "sdev" : None,
    "variance" : None,
    "median" : None,
    "mode" : None,
    "moment" : None,
    "determinant" : None,
    "transpose" : None,
    "selector" : None,
    "neq" : None,
    "eq" : None,
    "gt" : None,
    "lt" : None,
    "geq" : None,
    "leq" : None,
    "in" : None,
    "notin" : None,
    "notsubset" : None,
    "notprsubset" : None,
    "subset" : None,
    "prsubset" : None,
    "tendsto" : None,
    "ci" : None,
    "cn" : None,
    "apply" : None,
    "reln" : None,
    "lambda" : None,
    "condition" : None,
    "declare" : None,
    "semantics" : None,
    "annotation" : None,
    "annotation-xml" : None,
    "interval" : None,
    "set" : None,
    "list" : None,
    "vector" : None,
    "matrix" : None,
    "matrixrow" : None,
    "fn" : None,
    "lowlimit" : None,
    "uplimit" : None,
    "bvar" : None,
    "degree" : None,
    "logbase" : None,
    "mstyle" : None,
    "merror" : None,
    "mphantom" : None,
    "mrow" : None,
    "mfrac" : None,
    "msqrt" : None,
    "mroot" : None,
    "msub" : None,
    "msup" : None,
    "msubsup" : None,
    "mmultiscripts" : None,
    "munder" : None,
    "mover" : None,
    "munderover" : None,
    "mtable" : None,
    "mtr" : None,
    "mtd" : None,
    "maction" : None,
    "mfenced" : None,
    "mpadded" : None,
    "mi" : None,
    "mn" : None,
    "mo" : None,
    "mtext" : None,
    "ms" : None,
    "math" : None,
}

# invalid and old tags
OldTags = {
    "blink" : None, # Netscape Navigator
    "embed" : None, # Netscape Navigator 4
    "keygen" : None, # Netscape Navigator
    "layer" : None, # Netscape Navigator 4
    "listing" : None, # HTML 3.2
    "multicol" : None, # Netscape Navigator 3
    "nobr" : None, # Netscape Navigator 1.1
    "noembed" : None, # Netscape Navigator 4
    "nolayer" : None, # Netscape Navigator 4
    "plaintext" : None, # HTML 3.2
    "spacer" : None, # Netscape Navigator 3
    "wbr" : None, # Netscape Navigator 1.1
    "xmp" : None, # HTML 3.2
}

def check_spelling (tag, url):
    """check if tag (must be lowercase) is a valid HTML tag and if not,
    tries to correct it to the first tag with a levenshtein distance of 1
    """
    if tag in HtmlTags or tag in MathTags:
        return tag
    if tag in OldTags:
        print >>sys.stderr, "Warning: non-HTML4 tag", `tag`, "at", `url`
        return tag
    for htmltag in HtmlTags.keys():
         if distance(tag, htmltag)==1:
             print >>sys.stderr, "Warning: HTML tag", `tag`, \
                                 "corrected to", `htmltag`, "at", `url`
             return htmltag
    print >>sys.stderr, "Error: unknown HTML tag", `tag`, "at", `url`
    return tag


if __name__=='__main__':
    for tag in ["blink", "bllnk", "htmm", "hu", ]:
        print tag, check_spelling(tag)
