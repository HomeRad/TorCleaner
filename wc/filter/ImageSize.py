"""filter images by size"""
# -*- coding: iso-8859-1 -*-
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

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

import Image
from StringIO import StringIO
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, compileRegex
from wc.filter.Filter import Filter
from wc.log import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = ['image']
# which mime types this filter applies to
mimelist = map(compileMime, ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)'])

class ImageSize (Filter):
    """Base filter class which is using the GifParser to deanimate the
       incoming GIF stream"""


    def __init__ (self, mimelist):
        super(ImageSize, self).__init__(mimelist)
        # minimal amount of image data for PIL to read header info
        # 6000 bytes should be enough, even for JPEG images
        self.min_bufsize = 6000


    def addrule (self, rule):
        super(ImageSize, self).addrule(rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")


    def filter (self, data, **attrs):
        if not attrs.has_key('buffer') or attrs['buffer'].closed:
            # we do not block this image
            # or we do not have enough buffer data yet
            return data
        buf = attrs['buffer']
        buf.write(data)
        if buf.tell() > self.min_bufsize:
            if self.check_sizes(buf, attrs['sizes']):
                # size is ok
                data = buf.getvalue()
                buf.close()
                return data
        return ''


    def finish (self, data, **attrs):
        if not attrs.has_key('buffer') or attrs['buffer'].closed:
            # we do not block this image
            return data
        buf = attrs['buffer']
        buf.write(data)
        if self.check_sizes(buf, attrs['sizes']):
            # size is ok
            data = buf.getvalue()
            buf.close()
            return data
        return ''


    def check_sizes (self, buf, sizes):
        try:
            buf.seek(0)
            img = Image.open(buf, 'r')
            for size, formats in sizes:
                if size==img.size:
                    # size matches, look for format restriction
                    if not formats:
                        return False
                    elif img.format.lower() in formats:
                        return False
        except IOError:
            exception(FILTER, "Could not get image size")
        return True


    def getAttrs (self, headers, url):
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return {}
        sizes = [((rule.width, rule.height), rule.formats) for rule in rules]
        return {'buffer': StringIO(),
                'sizes': sizes}

