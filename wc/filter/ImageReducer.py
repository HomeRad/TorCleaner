"""Reduce big images to JPGs to save bandwidth"""
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
from cStringIO import StringIO
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime
from wc.filter.Filter import Filter
from wc.log import *
from wc.proxy.Headers import remove_headers


class ImageReducer (Filter):
    """Reduce the image size by making low quality JPEGs"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = []
    # which mime types this filter applies to
    mimelist = [compileMime(x) for x in ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)']]

    def __init__ (self, apply_to_mimelist):
        super(ImageReducer, self).__init__(apply_to_mimelist)
        # minimal number of bytes before we start reducing
        self.minimal_size_bytes = 5120


    def filter (self, data, **attrs):
        if not attrs.has_key('buffer'): return data
        attrs['buffer'].write(data)
        return ''


    def finish (self, data, **attrs):
        if not attrs.has_key('buffer'): return data
        p = attrs['buffer']
        if data: p.write(data)
        p.seek(0)
        try:
            img = Image.open(p)
            data = StringIO()
            if attrs.get('convert'):
                img = img.convert()
            img.save(data, "JPEG", quality=10, optimize=1)
        except IOError:
            # return original image data on error
            # XXX the content type is pretty sure wrong
            return p.getvalue()
        return data.getvalue()


    def getAttrs (self, url, headers):
        # don't filter tiny images
        d = super(ImageReducer, self).getAttrs(url, headers)
        if headers.get('Content-Length', 0) < self.minimal_size_bytes:
            return d
        ctype = headers['Content-Type']
        headers['Content-Type'] = 'image/jpeg'
        remove_headers(headers, ['Content-Length'])
        d['buffer'] = StringIO()
        # some images have to be convert()ed before saving
        d['convert'] = convert(ctype)
        return d


def convert (ctype):
    return ctype in ('image/gif',)
