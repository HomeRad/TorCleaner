"""deanimate GIFs"""
# Copyright (C) 2000-2003  Bastian Kleineidam
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
import base64
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, compileRegex
from wc.filter.Filter import Filter
from wc.log import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['image']
# which mime types this filter applies to
mimelist = map(compileMime, ['image/gif'])

def i16 (c):
    """merge two bytes to an integer"""
    return ord(c[0]) | (ord(c[1])<<8)


class RewindException (Exception): pass


class GifImage (Filter):
    """Base filter class which is using the GifParser to deanimate the
       incoming GIF stream"""

    def __init__ (self, mimelist):
        Filter.__init__(self, mimelist)
        self.tiny_gif = None

    def addrule (self, rule):
        Filter.addrule(self, rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")


    def filter (self, data, **attrs):
        if not attrs.has_key('gifparser'): return data
        gifparser = attrs['gifparser']
        gifparser.addData(data)
        try:
            gifparser.parse()
        except RewindException:
            pass
        return gifparser.getOutput()


    def finish (self, data, **attrs):
        if not attrs.has_key('gifparser'): return data
        if data: data = self.filter(data, **attrs)
        gifparser = attrs['gifparser']
        return data + (gifparser.finish and ';' or '')


    def getAttrs (self, headers, url):
        # first: weed out the rules that dont apply to this url
        rules = filter(lambda r, u=url: r.appliesTo(u), self.rules)
        if not rules:
            return {}
        sizes = map(lambda r: (r.width, r.height), rules)
        return {'gifparser': GifParser(sizes)}



class GifParser:
    """Here we have a parser (and filter) for GIF images.
    This parser filters all GIF image extensions (eg. comment and
    application extensions) except graphic control extensions.
    Furthermore we only allow the first frame of animated GIFs.
    Additionally you can filter images by size. If the image size is
    in the SIZES list, it gets replaced by a one-pixel transparent GIF.

    NOTE: this code can handle LZW compressed GIFs, but is not in any way
    using the patented algorithm and therefore does not have any such
    restrictions.
    """
    # parser states to allow reading image data in chunks
    # only if we have a large enough chunk we change to the next state
    SKIP = 0
    INIT = 1
    FRAME = 2
    IMAGE = 3
    DATA = 4
    NOFILTER = 5

    def strState (self):
        if self.state==GifParser.SKIP:     return 'SKIP'
        if self.state==GifParser.INIT:     return 'INIT'
        if self.state==GifParser.FRAME:    return 'FRAME'
        if self.state==GifParser.IMAGE:    return 'IMAGE'
        if self.state==GifParser.DATA:     return 'DATA'
        if self.state==GifParser.NOFILTER: return 'NOFILTER'
        return 'UNKNOWN'

    def __init__ (self, sizes=[]):
        self.state = GifParser.INIT
        self.data = self.consumed = self.output = ''
        self.finish = 0
        self.removing = 0
        self.sizes = sizes

    def addData (self, data):
        self.data += data

    def flush (self):
        if self.consumed:
            self.output += self.consumed
            self.consumed = ''

    def read (self, i):
        if i<=0: return
        if len(self.data)<i:
            # rewind and stop filtering; wait for next data chunk
            debug(FILTER, 'GIF rewinding')
            self.data = self.consumed + self.data
            self.consumed = ''
            raise RewindException, "GifImage data delay => rewinding"
        self.consumed += self.data[:i]
        self.data = self.data[i:]
        return self.consumed[-i:]

    def remove (self, i):
        self.consumed = self.consumed[:-i]

    def getOutput (self):
        if self.output:
            res = self.output
            self.output = ''
            return res
        return self.output

    def parse (self):
        """Big parse function. The trick is the usage of self.read(),
	   which throws an Exception  when it can't give enough data.
	   In this case we just bail out ('rewind'), and continue
	   the next time in the saved state with hopefully more data
           available :)"""
        while 1:
            debug(FILTER, 'GifImage state %s', self.strState())
            self.flush()
            if self.state == GifParser.NOFILTER:
                self.output += self.consumed + self.data
                self.consumed = self.data = ''
                break
            elif self.state == GifParser.INIT:
                self.header = self.read(6)
                # it seems that some animated gifs have a wrong
                # version (i.e. GIF87a, not GIF89a)
                # and it seems that Netscape animates them
                # so we ignore the version and filter nonetheless
                #if self.header != 'GIF89a':
                #    debug(FILTER, 'Non-animated GIF')
                #    self.state == GifParser.NOFILTER
                #    continue
                self.size = (i16(self.read(2)), i16(self.read(2)))
                debug(FILTER, 'GIF width=%d, height=%d', self.size[0], self.size[1])
                if self.size in self.sizes:
                    self.output = base64.decodestring(_TINY_GIF)
                    self.data = self.consumed = ''
                    self.state = GifParser.SKIP
                    break
                flags = ord(self.read(1))
                misc = self.read(2)
                bits = (flags & 7) + 1
                if flags & 128:
                    # global palette
                    self.background = ord(misc[0])
                    debug(FILTER, 'GIF background %s', self.background)
                    size = 3<<bits
                    debug(FILTER, 'GIF global palette size %d', size)
                    self.read(size)
                self.state = GifParser.FRAME
            elif self.state == GifParser.FRAME:
                s = self.read(1)
                if (not s) or s == ';':
                    self.state = GifParser.SKIP
                    continue
                elif s == '!':
                    # extensions
                    s = self.read(1)
                    debug(FILTER, 'GIF extension %d', ord(s))
                    # remove all extensions except graphic controls (249)
                    self.removing = (ord(s) != 249)
                    if self.removing:
                        self.remove(2)
                    self.state = GifParser.DATA
                    continue
                elif s == ',':
                    self.state = GifParser.IMAGE
                    continue
                error(FILTER, "unknown GIF frame %s", `s`)
            elif self.state == GifParser.IMAGE:
                #extent
                self.x0 = i16(self.read(2))
                self.y0 = i16(self.read(2))
                self.x1 = i16(self.read(2)) + self.x0
                self.y1 = i16(self.read(2)) + self.y0
                debug(FILTER, 'GIF x0=%d, y0=%d, x1=%d, y1=%d', self.x0, self.y0, self.x1, self.y1)
                flags = ord(self.read(1))
                if flags & 128:
                    # local color table
                    bits = (flags & 7) + 1
                    size = 3<<bits
                    debug(FILTER, 'GIF local palette size %d', size)
                    self.read(size)
                # image data
                misc = ord(self.read(1))
                self.state = GifParser.DATA
                self.finish = 1 # not more than one image frame :)
            elif self.state == GifParser.DATA:
                size = ord(self.read(1))
                debug(FILTER, 'GIF data size %d', size)
                if size:
                    self.read(size)
                    if self.removing:
                        self.remove(size+1)
                else:
                    if self.removing:
                        self.remove(1)
                    if self.finish:
                        self.state = GifParser.SKIP
                    else:
                        self.state = GifParser.FRAME
                    self.removing = 0
            elif self.state == GifParser.SKIP:
                if self.consumed:
                    self.output += self.consumed
                    self.consumed = ''
                self.data = ''
                break
            else:
                raise Exception("invalid GifParser state")
        # while 1
    # parse
