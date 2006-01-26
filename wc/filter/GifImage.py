# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2006 Bastian Kleineidam
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
Deanimate GIF images.
"""

import base64
import wc.log
import wc.filter
import wc.filter.Filter


def i16 (c):
    """
    Merge two bytes to an integer.
    """
    return ord(c[0]) | (ord(c[1]) << 8)


class RewindException (Exception):
    """
    Exception saying that more image data is needed for parsing.
    """
    pass


class GifImage (wc.filter.Filter.Filter):
    """
    Base filter class which is using the GifParser to deanimate the
    incoming GIF stream.
    """

    enable = True

    def __init__ (self):
        """
        Init GIF stages and mimes.
        """
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        mimes = ['image/gif']
        super(GifImage, self).__init__(stages=stages, mimes=mimes)

    def filter (self, data, attrs):
        """
        Feed data to GIF image parser, return processed data.
        """
        if 'gifparser' not in attrs:
            return data
        gifparser = attrs['gifparser']
        gifparser.add_data(data)
        try:
            gifparser.parse()
        except RewindException:
            # wait for more data
            pass
        return gifparser.get_output()

    def finish (self, data, attrs):
        """
        Feed data to GIF image parser, flush it and return processed data.
        """
        if 'gifparser' not in attrs:
            return data
        if data:
            data = self.filter(data, attrs)
        gifparser = attrs['gifparser']
        return data + (gifparser.finish and ';' or '')

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        Add GIF parser to attributes.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(GifImage, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        attrs['gifparser'] = GifParser(url)


# little 1x1 transparent GIF
_TINY_GIF = """R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs="""


class GifParser (object):
    """
    Here we have a parser (and filter) for GIF images.
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

    def __init__ (self, url, sizes=None):
        """
        Initialize GIF parser buffers and flags.
        """
        self.url = url
        self.state = GifParser.INIT
        self.data = self.consumed = self.output = ''
        self.finish = False
        self.removing = False
        if sizes is None:
            self.sizes = []
        else:
            self.sizes = sizes

    def str_state (self):
        """
        Return string representation of parser state.
        """
        if self.state == GifParser.SKIP:
            return 'SKIP'
        if self.state == GifParser.INIT:
            return 'INIT'
        if self.state == GifParser.FRAME:
            return 'FRAME'
        if self.state == GifParser.IMAGE:
            return 'IMAGE'
        if self.state == GifParser.DATA:
            return 'DATA'
        if self.state == GifParser.NOFILTER:
            return 'NOFILTER'
        return 'UNKNOWN'

    def add_data (self, data):
        """
        Add image data to internal parse buffer.
        """
        self.data += data

    def flush (self):
        """
        Flush already parsed image data to output buffer.
        """
        if self.consumed:
            self.output += self.consumed
            self.consumed = ''

    def read (self, i):
        """
        Read i data from internal buffer.

        @raise: RewindException if not enough data.
        """
        if i <= 0:
            return
        if len(self.data)<i:
            # rewind and stop filtering; wait for next data chunk
            assert wc.log.debug(wc.LOG_FILTER, 'GIF rewinding')
            self.data = self.consumed + self.data
            self.consumed = ''
            raise RewindException("GifImage data delay => rewinding")
        self.consumed += self.data[:i]
        self.data = self.data[i:]
        return self.consumed[-i:]

    def remove (self, i):
        """
        Remove i bytes from already parsed image data.
        """
        self.consumed = self.consumed[:-i]

    def get_output (self):
        """
        Get output buffer data and flush it.
        """
        if self.output:
            res = self.output
            self.output = ''
            return res
        return self.output

    def parse (self):
        """
        Big parse function. The trick is the usage of self.read(),
        which throws a RewindException when it can't give enough data.
        In this case we just bail out (aka rewind), and continue
        the next time in the saved state with hopefully more data
        available :).

        @raise: RewindException if not enough data.
        """
        while 1:
            assert wc.log.debug(wc.LOG_FILTER,
                                'GifImage state %s', self.str_state())
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
                # so ignore the version number here and check only for
                # the GIF prefix
                if not self.header.startswith('GIF'):
                    assert wc.log.debug(wc.LOG_FILTER,
                                 "No GIF file, switch to nofilter mode")
                    self.state = GifParser.NOFILTER
                    continue
                self.size = (i16(self.read(2)), i16(self.read(2)))
                assert wc.log.debug(wc.LOG_FILTER,
                        'GIF width=%d, height=%d', self.size[0], self.size[1])
                if self.size in self.sizes:
                    self.output = base64.decodestring(_TINY_GIF)
                    self.data = self.consumed = ''
                    self.state = GifParser.SKIP
                    break
                flags = ord(self.read(1))
                misc = self.read(2)
                bits = (flags & 7) + 1
                if (flags & 128)!=0:
                    # global palette
                    self.background = ord(misc[0])
                    assert wc.log.debug(wc.LOG_FILTER,
                                 'GIF background %s', self.background)
                    size = 3 << bits
                    assert wc.log.debug(wc.LOG_FILTER,
                                 'GIF global palette size %d', size)
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
                    assert wc.log.debug(wc.LOG_FILTER,
                                        'GIF extension %d', ord(s))
                    # remove all extensions except graphic controls (249)
                    self.removing = (ord(s) != 249)
                    if self.removing:
                        self.remove(2)
                    self.state = GifParser.DATA
                    continue
                elif s == ',':
                    self.state = GifParser.IMAGE
                    continue
                wc.log.warn(wc.LOG_FILTER,
                            "unknown GIF frame %r at %r", s, self.url)
            elif self.state == GifParser.IMAGE:
                #extent
                self.x0 = i16(self.read(2))
                self.y0 = i16(self.read(2))
                self.x1 = i16(self.read(2)) + self.x0
                self.y1 = i16(self.read(2)) + self.y0
                assert wc.log.debug(wc.LOG_FILTER,
                             'GIF x0=%d, y0=%d, x1=%d, y1=%d',
                             self.x0, self.y0, self.x1, self.y1)
                flags = ord(self.read(1))
                if (flags & 128) != 0:
                    # local color table
                    bits = (flags & 7) + 1
                    size = 3 << bits
                    assert wc.log.debug(wc.LOG_FILTER,
                                 'GIF local palette size %d', size)
                    self.read(size)
                # image data
                misc = ord(self.read(1))
                self.state = GifParser.DATA
                self.finish = True # not more than one image frame :)
            elif self.state == GifParser.DATA:
                size = ord(self.read(1))
                assert wc.log.debug(wc.LOG_FILTER, 'GIF data size %d', size)
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
                    self.removing = False
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
