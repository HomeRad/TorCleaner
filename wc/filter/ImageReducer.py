"""Reduce big images to JPGs to save bandwidth"""
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
import re, os, sys, base64, ImageFile, cStringIO
from wc.filter import FILTER_RESPONSE_MODIFY, FilterException, \
                      compileMime, compileRegex
from wc.filter.Filter import Filter
from wc.debug import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_MODIFY]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = []
# which mime types this filter applies to
mimelist = map(compileMime, ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)'])


class ImageReducer (Filter):
    """Reduce the image size by making low quality JPEGs"""

    def __init__ (self, mimelist):
        Filter.__init__(self, mimelist)
        # minimal number of bytes before we start reducing
        self.minimal_size_bytes = 10240


    def filter (self, data, **attrs):
        if not (attrs.has_key('parser') and data): return data
        # XXX catch IOError
        attrs['parser'].feed(data)
        return ''


    def finish (self, data, **attrs):
        if not attrs.has_key('parser'): return data
        p = attrs['parser']
        if data: p.feed(data)
        img = p.close()
        data = cStringIO.StringIO()
        if attrs.get('convert'):
            img = img.convert()
        img.save(data, "JPEG", quality=10, optimize=1)
        return data.getvalue()


    def getAttrs (self, headers, url):
        # don't filter tiny images
        if headers.get('Content-Size', 0) < self.minimal_size_bytes:
            return {}
        ctype = headers['Content-Type']
        headers['Content-Type'] = 'image/jpeg'
        return {
            'parser': ImageFile.Parser(),
            # some images have to be convert()ed before saving
            'convert': convert(ctype),
        }


def convert (ctype):
    return ctype in ('image/gif',)
