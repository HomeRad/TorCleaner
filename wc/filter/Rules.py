"""configuration classes for all available filter modules."""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
from wc import _, debug, error, xmlify, unxmlify
from wc.debug_levels import *
from types import StringType, IntType
import re

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
NO_CLOSE_TAGS = ('img', 'meta', 'br', 'link')
# all parts of a URL
Netlocparts = ['scheme','host','port','path','parameters','query','fragment']

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

# global counter in case the .zap rules dont yet have the oid entry
rulecounter = 1

class Rule:
    """Basic rule class for filtering.
    A basic rule has:
       title - the title
       oid - identification number, also used for sorting
       desc - the description
       disable - flag to disable this rule
       urlre - regular expression that matches urls applicable for this rule.
               leave empty to apply to all urls.
       parent - the parent folder (if any); look at FolderRule class
    """
    def __init__ (self, title="No title", desc="", disable=0, parent=None, oid=0):
        self.title = title
        global rulecounter
        if not oid:
            self.oid = rulecounter
            rulecounter += 1
        else:
            self.oid = oid
	    if oid >= rulecounter:
	        rulecounter = oid+1
        self.desc = desc
        self.disable = disable
        self.parent = parent
        self.attrnames = ['title', 'desc', 'disable', 'oid']
        self.intattrs = ['disable', 'oid']

    def __cmp__ (self, other):
        return cmp(self.oid, other.oid)

    def fill_attrs (self, attrs, name):
        for attr in self.attrnames:
            if attrs.has_key(attr):
                val = unxmlify(attrs[attr]).encode('iso8859-1')
                setattr(self, attr, val)
        for attr in self.intattrs:
            val = getattr(self, attr)
            if val and type(val) != IntType:
                setattr(self, attr, int(getattr(self, attr)))

    def fill_data (self, data, name):
        pass

    def fromFactory (self, factory):
        return factory.fromRule(self)

    def get_name (self):
        """class name without "Rule" suffix, in lowercase"""
        return self.__class__.__name__[:-4].lower()

    def toxml (self):
        s = "<"+self.get_name()
        s += ' title="%s"' % xmlify(self.title)
	s += ' oid="%d"' % self.oid
        if self.desc:
            s += '\n desc="%s"' % xmlify(self.desc)
        if self.disable:
            s += '\n disable="1"'
        return s

    def __str__ (self):
        s = self.get_name()+"\n"
        s += "title   %s\n" % self.title
	s += "oid     %d\n" % self.oid
        s += "desc    %s\n" % self.desc
        s += "disable %d\n" % self.disable
        return s


class UrlRule(Rule):
    """rule which applies only to urls which match a regular expression"""
    def __init__ (self, title="No title", desc="", disable=0, matchurl="",
                  dontmatchurl="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.matchurl = matchurl
        self.dontmatchurl = dontmatchurl
        self.attrnames.extend(('matchurl', 'dontmatchurl'))

    def appliesTo (self, url):
        if self.matchurl:
            return self.matchurl.search(url)
        if self.dontmatchurl:
            return not self.dontmatchurl.search(url)
        return 1

    def toxml (self):
        s = Rule.toxml(self)
        if self.matchurl:
            s += '\n matchurl="%s"' % xmlify(self.matchurl)
        if self.dontmatchurl:
            s += '\n dontmatchurl="%s"' % xmlify(self.dontmatchurl)
        return s

    def __str__ (self):
        s = Rule.__str__(self)
        s += "matchurl %s\n" % `self.matchurl`
        s += "dontmatchurl %s\n" % `self.dontmatchurl`
        return s


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
        #debug(NIGHTMARE, "original tag", tag, "attrs", attrs)
        #debug(NIGHTMARE, "replace", num_part(part), "with", self.replace[1])
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


class AllowRule (Rule):
    def __init__ (self, title="No title", desc="", disable=0, scheme="",
                  host="", port="", path="", parameters="", query="",
		  fragment="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path
        self.parameters = parameters
        self.query = query
        self.fragment = fragment
        self.attrnames.extend(('scheme','host','port','path','parameters',
                                'query','fragment'))

    def fromFactory (self, factory):
        return factory.fromAllowRule(self)

    def toxml (self):
        return "%s%s/>"%(Rule.toxml(self),self.netlocxml())

    def netlocxml (self):
        s = ""
        for attr in Netlocparts:
            a = getattr(self, attr)
            if a is not None:
                s += '\n %s="%s"' % (attr, xmlify(a))
        return s


class BlockRule (AllowRule):
    def __init__ (self, title="No title", desc="", disable=0, scheme="",
                  host="", port="", path="", parameters="", query="",
		  fragment="", url="", oid=0):
        AllowRule.__init__(self, title=title, desc=desc, disable=disable,
                           scheme=scheme, host=host, port=port, path=path,
                           parameters=parameters, query=query,
                           fragment=fragment, oid=oid)
        self.url = url

    def fill_data (self, data, name):
        if name=='block':
            self.url += umxlify(data).encode('iso8859-1')

    def fromFactory (self, factory):
        return factory.fromBlockRule(self)

    def toxml (self):
        s = Rule.toxml(self)+self.netlocxml()
        if self.url:
            return s+">"+xmlify(self.url)+"</block>"
        return s+"/>"


class HeaderRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, name="",
                  value="", oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.name = name
        self.value = value
        self.attrnames.append('name')

    def fill_data (self, data, name):
        if name=='header':
            self.value = unxmlify(data).encode('iso8859-1')

    def fromFactory (self, factory):
        return factory.fromHeaderRule(self)

    def toxml (self):
        s = '%s\n name="%s"'%(UrlRule.toxml(self), xmlify(self.name))
        if self.value:
            return s+">"+xmlify(self.value)+"</header>"
        return s+"/>"


class ImageRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, width=0,
                  height=0, type="gif", url="", oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.width=width
        self.height=height
        self.intattrs.extend(('width','height'))
        self.type=type
        self.url = url
        self.attrnames.extend(('type','url','width','height'))

    def fromFactory (self, factory):
        return factory.fromImageRule(self)

    def toxml (self):
        s = UrlRule.toxml(self)
        if self.width:
            s += '\n width="%d"' % self.width
        if self.height:
            s += '\n height="%d"' % self.height
        if self.type!='gif':
            s += '\n type="%s"\n' % self.type
        if self.url:
            return s+">"+xmlify(self.url)+"</image>\n"
        return s+"/>"


class NocommentsRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0, oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)

    def fromFactory (self, factory):
        return factory.fromNocommentsRule(self)

    def toxml (self):
	return UrlRule.toxml(self) + "/>"


class ReplacerRule (UrlRule):
    def __init__ (self, title="No title", desc="", disable=0,
                  search="", replace="", oid=0):
        UrlRule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.search = search
        self.replace = replace
        self.attrnames.append('search')

    def fill_data (self, data, name):
        if name=='replacer':
            self.replace += unxmlify(data).encode('iso8859-1')

    def fromFactory (self, factory):
        return factory.fromReplacerRule(self)

    def toxml (self):
	s = UrlRule.toxml(self);
        if self.search:
            s += '\n search="%s"'%xmlify(self.search)
        if self.replace:
            return s+">"+xmlify(self.replace)+"</replacer>"
        return s+"/>"


class FolderRule (Rule):
    def __init__ (self, title="No title", desc="", disable=0, lang="",
                  filename="", oid=0):
        Rule.__init__(self, title=title, desc=desc, disable=disable, oid=oid)
        self.filename = filename
        self.lang = lang
        self.rules = []

    def fromFactory (self, factory):
        return factory.fromFolderRule(self)

    def append_rule (self, r):
        self.rules.append(r)
        r.parent = self

    def delete_rule (self, i):
        r = self.rules[i]
        del self.rules[i]

    def sort (self):
        self.rules.sort()
        recalc_oids(self.rules)

    def toxml (self):
        s = """<?xml version="1.0"?>
<!DOCTYPE filter SYSTEM "filter.dtd">
""" + Rule.toxml(self)
        if self.lang:
            s += '\n lang="%s"' % self.lang
        s += ">\n"
        for r in self.rules:
            s += "\n%s\n"%r.toxml()
        return s+"</folder>\n"


def recalc_oids (rules):
    i = 0
    for r in rules:
        r.oid = i
        i += 1
