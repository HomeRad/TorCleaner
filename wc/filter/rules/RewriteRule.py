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

from UrlRule import UrlRule
from wc import _, debug, xmlify, unxmlify
from wc.debug_levels import *

# tag ids
STARTTAG = 0
ENDTAG = 1
DATA = 2
COMMENT = 3
# tag part ids
TAG = 0
TAGNAME = 1
ATTR = 2
ATTRVAL = 3
COMPLETE = 4
ENCLOSED = 5
# tags where close tag is missing
# note that this means that if the ending tag is there, it will not
# be filtered...
NO_CLOSE_TAGS = ('img', 'image', 'meta', 'br', 'link', 'area')

def part_num (s):
    """translation: tag name ==> tag number"""
    if s=='tag':
        return TAG
    if s=='tagname':
        return TAGNAME
    if s=='attr':
        return ATTR
    if s=='attrval':
        return ATTRVAL
    if s=='complete':
        return COMMENT
    if s=='enclosed':
        return ENCLOSED

def num_part (s):
    """translation: tag number ==> tag name"""
    if s==TAG:
        return 'tag'
    if s==TAGNAME:
        return 'tagname'
    if s==ATTR:
        return 'attr'
    if s==ATTRVAL:
        return 'attrval'
    if s==COMPLETE:
        return 'complete'
    if s==ENCLOSED:
        return 'enclosed'
    return 'unknown'

class RewriteRule (UrlRule):
    """A rewrite rule applies to a specific tag, optional with attribute
       constraints (stored in self.attrs) or a regular expression to
       match the enclosed block (self.enclosed).
       The replacement part and value is stored in a list with length
       two (self.replace == [repl. part, repl. string]).
    """
    def __init__ (self, title="No title", desc="", disable=0, tag="a",
                  attrs=None, enclosed="", replace=[COMPLETE,""], oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.tag = tag
        if attrs is None:
            self.attrs = {}
        else:
            self.attrs = attrs
        self.replace = list(replace)
        self.enclosed = enclosed
        if self.enclosed and self.tag in NO_CLOSE_TAGS:
            raise ValueError, _("Dont specify <enclose> with tag name %s")%tag
        self.attrnames.append('tag')

    def fill_attrs (self, attrs, name):
        if name=='rewrite':
            UrlRule.fill_attrs(self, attrs, name)
        elif name=='attr':
            val = unxmlify(attrs.get('name', 'href')).encode('iso8859-1')
            self.current_attr = val
            self.attrs[self.current_attr] = ""
        elif name=='replace' and attrs.has_key('part'):
            self.replace[0] = part_num(unxmlify(attrs['part']).encode('iso8859-1'))

    def fill_data (self, data, name):
        data = unxmlify(data).encode('iso8859-1')
        if name=='attr':
            self.attrs[self.current_attr] += data
        elif name=='enclosed':
            self.enclosed += data
        elif name=='replace':
            self.replace[1] += data

    def fromFactory (self, factory):
        return factory.fromRewriteRule(self)

    def _compute_start_sufficient (self):
        if self.tag in NO_CLOSE_TAGS:
            return 1
        part = self.replace[0]
        if part not in [ENCLOSED, COMPLETE, TAG, TAGNAME]:
            return 1
        return 0

    def set_start_sufficient (self):
        self.start_sufficient = self._compute_start_sufficient()

    def match_tag (self, tag):
        return self.tag == tag

    def match_attrs (self, attrs):
        occurred = []
        for attr,val in attrs.items():
            # attr or val could be None
            if attr is None: attr = ''
            if val is None: val = ''
            occurred.append(attr)
            ro = self.attrs.get(attr)
            if ro and not ro.search(val):
                return 0
        for attr in self.attrs.keys():
            if attr not in occurred:
                return 0
        return 1

    def match_complete (self, i, buf):
        """We know that the tag (and tag attributes) match. Now match
	   the enclosing block."""
        if not self.enclosed:
            # no enclosed expression => match
            return 1
        # check every data for a match (data is _not_ chunked)
        for n in buf[i:]:
            if n[0]==DATA and self.enclosed.search(n[1]):
                return 1
        return 0

    def filter_tag (self, tag, attrs):
        #debug(NIGHTMARE, "rule %s filter_tag" % self.title)
        part = self.replace[0]
        #debug(NIGHTMARE, "original tag", `tag`, "attrs", attrs)
        #debug(NIGHTMARE, "replace", num_part(part), "with", `self.replace[1]`)
        if part==TAGNAME:
            return (STARTTAG, self.replace[1], attrs)
        if part==TAG:
            return (DATA, self.replace[1])
        if part==ENCLOSED:
            return (STARTTAG, tag, attrs)
        if part==COMPLETE:
            return [DATA, ""]
        newattrs = {}
        # look for matching tag attributes
        for attr,val in attrs.items():
            ro = self.attrs.get(attr)
            if ro:
                mo = ro.search(val)
                if mo:
                    if part==ATTR:
                        if self.replace[1]:
                            newattrs[self.replace[1][0]] = self.replace[1][1]
                    else:
                        # part has to be ATTRVAL
                        # Python has named submatches
                        if mo.groupdict().has_key('replace'):
                            newattrs[attr] = mo.groupdict()['replace']
                        else:
                            newattrs[attr] = self.replace[1]
                    continue
            # nothing matched, just append the attribute as is
            newattrs[attr] = val
        #debug(NIGHTMARE, "filtered tag", tag, "attrs", newattrs)
        return (STARTTAG, tag, newattrs)

    def filter_complete (self, i, buf):
        #debug(NIGHTMARE, "rule %s filter_complete" % self.title)
        part = self.replace[0]
        #debug(NIGHTMARE, "original buffer", `buf`)
        #debug(NIGHTMARE, "part",num_part(part))
        if part==COMPLETE:
            buf[i:] = [[DATA, self.replace[1]]]
        elif part==TAG:
            buf[i] = [DATA, self.replace[1]]
            buf[-1] = [DATA, self.replace[1]]
        elif part==TAGNAME:
            buf[i] = (STARTTAG, self.replace[1], {})
            buf[-1] = (ENDTAG, self.replace[1])
        elif part==ENCLOSED:
            buf[i+1:-1] = [(DATA, self.replace[1])]
        #debug(NIGHTMARE, "filtered buffer", `buf`)

    def toxml (self):
        s = UrlRule.toxml(self)
        if self.tag!='a':
            s += '\n tag="%s"' % self.tag
        if not (self.attrs or self.replace or self.enclosed):
            return s+"/>\n"
        s += ">\n"
        for key,val in self.attrs.items():
            s += "<attr"
            if key!='href':
                s += ' name="%s"' % key
            if val:
                s += ">"+xmlify(val)+"</attr>\n"
            else:
                s += "/>\n"
        if self.enclosed:
            s += "<enclosed>"+xmlify(self.enclosed)+"</enclosed>\n"
        if not self.replace[0]==COMPLETE or self.replace[1]:
            s += "<replace"
            if self.replace[0]!=COMPLETE:
                s += ' part="%s"' % num_part(self.replace[0])
            if self.replace[1]:
                if self.replace[0]==ATTR:
                    val = self.replace[0][0]+'="'+self.replace[0][1]+'"'
                else:
                    val = self.replace[1]
                s += '>'+xmlify(val)+"</replace>\n"
            else:
                s += "/>\n"
        return s + "</rewrite>"

    def __str__ (self):
        s = UrlRule.__str__(self)
        s += "tag %s\n" % self.tag
        for key,val in self.attrs.items():
            s += "attr: %s, %s\n" % (key,`val`)
        s += "enclosed %s\n" % `self.enclosed`
        s+= "replace [%s,%s]\n" % \
	    (num_part(self.replace[0]), `self.replace[1]`)
        s += "start suff. %d" % self.start_sufficient
        return s

