# -*- coding: iso-8859-1 -*-
"""Reduce big images to JPGs to save bandwidth"""
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

import Image
import cStringIO as StringIO
import wc.filter
import wc.filter.Filter
import wc.proxy.Headers


class ImageReducer (wc.filter.Filter.Filter):
    """Reduce the image size by making low quality JPEGs"""
    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = []
    # which mime types this filter applies to
    mimelist = [wc.filter.compileMime(x) for x in ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)']]

    def __init__ (self):
        """initialize image reducer flags"""
        super(ImageReducer, self).__init__()
        # minimal number of bytes before we start reducing
        self.minimal_size_bytes = 5120


    def filter (self, data, **attrs):
        """feed image data to buffer"""
        if not attrs.has_key('imgreducer_buf'): return data
        attrs['imgreducer_buf'].write(data)
        return ''


    def finish (self, data, **attrs):
        """feed image data to buffer, then convert it and return result"""
        if not attrs.has_key('imgreducer_buf'): return data
        p = attrs['imgreducer_buf']
        if data: p.write(data)
        p.seek(0)
        try:
            img = Image.open(p)
            data = StringIO.StringIO()
            if attrs.get('imgreducer_convert'):
                img = img.convert()
            img.save(data, "JPEG", quality=10, optimize=1)
        except IOError:
            # return original image data on error
            # XXX the content type is pretty sure wrong
            return p.getvalue()
        return data.getvalue()


    def getAttrs (self, url, headers):
        """initialize image reducer buffer and flags"""
        # don't filter tiny images
        d = super(ImageReducer, self).getAttrs(url, headers)
        length = headers.get('Content-Length')
        if length is not None and length < self.minimal_size_bytes:
            return d
        ctype = headers['Content-Type']
        headers['Content-Type'] = 'image/jpeg'
        wc.proxy.Headers.remove_headers(headers, ['Content-Length'])
        d['imgreducer_buf'] = StringIO.StringIO()
        # some images have to be convert()ed before saving
        d['imgreducer_convert'] = convert(ctype)
        return d


def convert (ctype):
    """return True if an image has to be convert()ed before saving"""
    return ctype in ('image/gif',)
