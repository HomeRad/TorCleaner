# -*- coding: iso-8859-1 -*-
"""filter images by size"""
# Copyright (C) 2000-2004  Bastian Kleineidam
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import Image
import os
import cStringIO as StringIO
import wc
import wc.filter
from wc.log import *

class ImageSize (wc.filter.Filter.Filter):
    """Base filter class which is using the GifParser to deanimate the
       incoming GIF stream"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['image']
    # which mime types this filter applies to
    mimelist = [wc.filter.compileMime(x) for x in ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)']]


    def __init__ (self):
        super(ImageSize, self).__init__()
        # minimal amount of image data for PIL to read header info:
        # 4096 bytes is enough for most images; the value is increased
        # when it is not big enough
        self.min_bufsize = 4096
        fname = os.path.join(wc.TemplateDir, wc.config['gui_theme'])
        fname = os.path.join(fname, "blocked.png")
        f = file(fname)
        self.blockdata = f.read()
        f.close()


    def filter (self, data, **attrs):
        if not data or not attrs.has_key('imgsize_buf'):
            # do not block this image
            return data
        if attrs['imgsize_blocked']:
            # block this image
            return ''
        buf = attrs['imgsize_buf']
        if buf.closed:
            # do not block this image
            return data
        buf.write(data)
        if buf.tell() > self.min_bufsize:
            # test if image is blocked
            attrs['imgsize_blocked'] = \
              not self.check_sizes(buf, attrs['imgsize_sizes'], attrs['url'])
            if buf.tell() < self.min_bufsize:
                # wait for more data
                return ''
            data = buf.getvalue()
            buf.close()
            if attrs['imgsize_blocked']:
                return self.blockdata
            return data
        return ''


    def finish (self, data, **attrs):
        # note: if attrs['blocked'] is True, then the blockdata is
        # already sent out
        if not attrs.has_key('imgsize_buf'):
            # do not block this image
            return data
        if attrs['imgsize_blocked']:
            # block this image
            return ''
        buf = attrs['imgsize_buf']
        if buf.closed:
            return data
        buf.write(data)
        url = attrs['url']
        pos = buf.tell()
        if pos <= 0:
            error(FILTER, "Empty image data found at %r", url)
        else:
            attrs['imgsize_blocked'] = \
          not self.check_sizes(buf, attrs['imgsize_sizes'], url, finish=True)
        data = buf.getvalue()
        buf.close()
        if attrs['imgsize_blocked']:
            return self.blockdata
        return data


    def check_sizes (self, buf, sizes, url, finish=False):
        pos = buf.tell()
        assert pos > 0
        try:
            buf.seek(0)
            img = Image.open(buf, 'r')
            buf.seek(pos)
            for size, formats in sizes:
                if size==img.size:
                    # size matches, look for format restriction
                    if not formats:
                        debug(FILTER, "Blocking image size %s", size)
                        return False
                    elif img.format.lower() in formats:
                        debug(FILTER, "Blocking image size %s", size)
                        return False
        except IOError:
            if finish:
                exception(FILTER, "Could not get image size from %r", url)
            else:
                assert pos > self.min_bufsize
                # wait for more data
                buf.seek(pos)
                self.min_bufsize = pos+4096
                assert buf.tell() < self.min_bufsize
        return True


    def getAttrs (self, url, headers):
        d = super(ImageSize, self).getAttrs(url, headers)
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return d
        d['imgsize_sizes'] = [((r.width, r.height), r.formats) for r in rules]
        d['imgsize_buf'] = StringIO.StringIO()
        d['imgsize_blocked'] = False
        return d

