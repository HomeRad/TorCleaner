# A parser for SGML, using the derived class as static DTD.

# XXX This only supports those SGML features used by HTML.

# XXX There should be a way to distinguish between PCDATA (parsed
# character data -- the normal case), RCDATA (replaceable character
# data -- only char and entity references and end tags are special)
# and CDATA (character data -- only end tags are special).

# sgmlop support added by fredrik@pythonware.com (April 6, 1998)

import re
import string

try:
    import sgmlop
except ImportError:
    sgmlop = None

# SGML parser base class -- find tags and call handler functions.
# Usage: p = SGMLParser(); p.feed(data); ...; p.close().
# The dtd is defined by deriving a class which defines methods
# with special names to handle tags: start_foo and end_foo to handle
# <foo> and </foo>, respectively, or do_foo to handle <foo> by itself.
# (Tags are converted to lower case for this purpose.)  The data
# between tags is passed to the parser by calling self.handle_data()
# with some data as argument (the data may be split up in arbutrary
# chunks).  Entity references are passed by calling
# self.handle_entityref() with the entity reference as argument.

# --------------------------------------------------------------------
# original re-based SGML parser

interesting = re.compile('[&<]')
incomplete = re.compile('&([a-zA-Z][a-zA-Z0-9]*|#[0-9]*)?|'
                        '<([a-zA-Z][^<>]*|'
                        '/([a-zA-Z][^<>]*)?|'
                        '![^<>]*)?')
entityref = re.compile('&([a-zA-Z][a-zA-Z0-9]*)[^a-zA-Z0-9]')
charref = re.compile('&#([0-9]+)[^0-9]')
starttagopen = re.compile('<[>a-zA-Z]')
shorttagopen = re.compile('<[a-zA-Z][a-zA-Z0-9]*/')
shorttag = re.compile('<([a-zA-Z][a-zA-Z0-9]*)/([^/]*)/')
endtagopen = re.compile('</[<>a-zA-Z]')
endbracket = re.compile('[>]')
special = re.compile('<![^<>]*>')
commentopen = re.compile('<!--')
commentclose = re.compile(r'--\s*>')
tagfind = re.compile('[a-zA-Z][a-zA-Z0-9]*')
attrfind = re.compile(
    r'\s*([a-zA-Z_][-.a-zA-Z_0-9]*)'
    r'(\s*=\s*'
    r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./:+*%?!\(\)_#=~]*))?')


class SlowSGMLParser:

    # Interface -- initialize and reset this instance
    def __init__(self, verbose=0):
        self.verbose = verbose
        self.reset()

    # Interface -- reset this instance.  Loses all unprocessed data
    def reset(self):
        self.rawdata = ''
        self.lasttag = '???'
        self.nomoretags = 0
        self.literal = 0

    # For derived classes only -- enter literal mode (CDATA) till EOF
    def setnomoretags(self):
        self.nomoretags = self.literal = 1

    # For derived classes only -- enter literal mode (CDATA)
    def setliteral(self, *args):
        self.literal = 1

    # Interface -- feed some data to the parser.  Call this as
    # often as you want, with as little or as much text as you
    # want (may include '\n').  (This just saves the text, all the
    # processing is done by goahead().)
    def feed(self, data):
        self.rawdata = self.rawdata + data
        self.goahead(0)

    # Interface -- handle the remaining data
    def close(self):
        self.goahead(1)

    # Internal -- handle data as far as reasonable.  May leave state
    # and data to be processed by a subsequent call.  If 'end' is
    # true, force handling all data as if followed by EOF marker.
    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            if self.nomoretags:
                self.handle_data(rawdata[i:n])
                i = n
                break
            match = interesting.search(rawdata, i)
            if match: j = match.start(0)
            else: j = n
            if i < j: self.handle_data(rawdata[i:j])
            i = j
            if i == n: break
            if rawdata[i] == '<':
                if starttagopen.match(rawdata, i):
                    if self.literal:
                        self.handle_data(rawdata[i])
                        i = i+1
                        continue
                    k = self.parse_starttag(i)
                    if k < 0: break
                    i = k
                    continue
                if endtagopen.match(rawdata, i):
                    k = self.parse_endtag(i)
                    if k < 0: break
                    i =  k
                    self.literal = 0
                    continue
                if commentopen.match(rawdata, i):
                    if self.literal:
                        self.handle_data(rawdata[i])
                        i = i+1
                        continue
                    k = self.parse_comment(i)
                    if k < 0: break
                    i = i+k
                    continue
                match = special.match(rawdata, i)
                if match:
                    if self.literal:
                        self.handle_data(rawdata[i])
                        i = i+1
                        continue
                    i = match.end(0)
                    continue
            elif rawdata[i] == '&':
                match = charref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_charref(name)
                    i = match.end(0)
                    if rawdata[i-1] != ';': i = i-1
                    continue
                match = entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    self.handle_entityref(name)
                    i = match.end(0)
                    if rawdata[i-1] != ';': i = i-1
                    continue
            else:
                raise RuntimeError, 'neither < nor & ??'
            # We get here only if incomplete matches but
            # nothing else
            match = incomplete.match(rawdata, i)
            if not match:
                self.handle_data(rawdata[i])
                i = i+1
                continue
            j = match.end(0)
            if j == n:
                break # Really incomplete
            self.handle_data(rawdata[i:j])
            i = j
        # end while
        if end and i < n:
            self.handle_data(rawdata[i:n])
            i = n
        self.rawdata = rawdata[i:]

    # Internal -- parse comment, return length or -1 if not terminated
    def parse_comment(self, i):
        rawdata = self.rawdata
        if rawdata[i:i+4] <> '<!--':
            raise RuntimeError, 'unexpected call to handle_comment'
        match = commentclose.search(rawdata, i+4)
        if not match:
            return -1
        j = match.start(0)
        self.handle_comment(rawdata[i+4: j])
        j = match.end(0)
        return j-i

    # Internal -- handle starttag, return length or -1 if not terminated
    def parse_starttag(self, i):
        rawdata = self.rawdata
        if shorttagopen.match(rawdata, i):
            # SGML shorthand: <tag/data/ == <tag>data</tag>
            # XXX Can data contain &... (entity or char refs)?
            # XXX Can data contain < or > (tag characters)?
            # XXX Can there be whitespace before the first /?
            match = shorttag.match(rawdata, i)
            if not match:
                return -1
            tag, data = match.group(1, 2)
            tag = string.lower(tag)
            self.unknown_starttag(tag, [])
            self.handle_data(data)
            self.unknown_endtag(tag)
            k = match.end(0)
            return k
        # XXX The following should skip matching quotes (' or ")
        quote = 0
        for j in range(i+1, len(rawdata)):
            if rawdata[j]=='"' or rawdata[j]=="'":
                quote = not quote
            elif rawdata[j]==">" and not quote:
                break
        if rawdata[j]!='>': return -1
        #match = endbracket.search(rawdata, i+1)
        #if not match:
        #    return -1
        #j = match.start(0)
        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        if rawdata[i:i+2] == '<>':
            # SGML shorthand: <> == <last open tag seen>
            k = j
            tag = self.lasttag
        else:
            match = tagfind.match(rawdata, i+1)
            if not match:
                raise RuntimeError, 'unexpected call to parse_starttag'
            k = match.end(0)
            tag = string.lower(rawdata[i+1:k])
            self.lasttag = tag
        while k < j:
            match = attrfind.match(rawdata, k)
            if not match: break
            attrname, rest, attrvalue = match.group(1, 2, 3)
            if not rest:
                attrvalue = attrname
            elif attrvalue[:1] == '\'' == attrvalue[-1:] or \
                 attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
            attrs.append((string.lower(attrname), attrvalue))
            k = match.end(0)
        if rawdata[j] == '>':
            j = j+1
        self.unknown_starttag(tag, attrs)
        return j

    # Internal -- parse endtag
    def parse_endtag(self, i):
        rawdata = self.rawdata
        match = endbracket.search(rawdata, i+1)
        if not match:
            return -1
        j = match.start(0)
        tag = string.lower(string.strip(rawdata[i+2:j]))
        if rawdata[j] == '>':
            j = j+1
        self.unknown_endtag(tag)
        return j

    # handlers, can be overridden
    def handle_entityref(self, name): pass
    def handle_charref(self, name):   pass
    def handle_proc(self, name):      pass
    def handle_special(self, name):   pass
    def handle_data(self, data):      pass
    def handle_cdata(self, data):     pass
    def handle_comment(self, data):   pass
    def unknown_starttag(self, tag, attrs): pass
    def unknown_endtag(self, tag):    pass
    def unknown_charref(self, ref):   pass
    def unknown_entityref(self, ref): pass


# --------------------------------------------------------------------
# accelerated SGML parser

class FastSGMLParser:
    # Interface -- initialize and reset this instance
    def __init__(self):
        self.parser = sgmlop.SGMLParser(self)
        self.feed = self.parser.feed
        self.reset = self.parser.reset

    # XXX For derived classes only -- enter literal mode (CDATA) till EOF
    def setnomoretags(self):
        pass

    # XXX For derived classes only -- enter literal mode (CDATA)
    def setliteral(self, *args):
        pass

    # Interface -- handle the remaining data
    def close(self):
        try:
            self.parser.close()
        finally:
            self.parser = None

    # handlers, can be overridden
    def handle_entityref(self, name): pass
    def handle_charref(self, name):   pass
    def handle_proc(self, name):      pass
    def handle_special(self, name):   pass
    def handle_data(self, data):      pass
    def handle_cdata(self, data):     pass
    def handle_comment(self, data):   pass
    def unknown_starttag(self, tag, attrs): pass
    def unknown_endtag(self, tag):    pass
    def unknown_charref(self, ref):   pass
    def unknown_entityref(self, ref): pass


# pick a suitable parser
if sgmlop:
    SGMLParser = FastSGMLParser
else:
    SGMLParser = SlowSGMLParser

if __name__ == '__main__':
    print "Ok"
