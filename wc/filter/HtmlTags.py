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
    "blink" : None,
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

# invalid and old tags
OldTags = {
    "image" : None, # ??? unknown
    "layer" : None, # Netscape Navigator 4
    "listing" : None, # HTML 3.2
    "nobr" : None, # Netscape Navigator 1.1
    "plaintext" : None, # HTML 3.2
    "wbr" : None, # Netscape Navigator 1.1
    "xmp" : None, # HTML 3.2
}

def check_spelling (tag, url):
    """check if tag (must be lowercase) is a valid HTML tag and if not,
    tries to correct it to the first tag with a levenshtein distance of 1
    """
    if tag in HtmlTags:
        return tag
    if tag in OldTags:
        print >>sys.stderr, "Warning: non-HTML4 tag", `tag`, "at", `url`
        return tag
    for htmltag in HtmlTags.keys():
         if distance(tag, htmltag)==1:
             print >>sys.stderr, "Warning: HTML tag", `tag`, \
                                 "corrected to", `htmltag`
             return htmltag
    print >>sys.stderr, "Error: unknown HTML tag", `tag`
    return tag


if __name__=='__main__':
    for tag in ["blink", "bllnk", "htmm", "hu", ]:
        print tag, check_spelling(tag)
