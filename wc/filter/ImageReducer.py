# -*- coding: iso-8859-1 -*-
"""Reduce big images to JPGs to save bandwidth"""
# Copyright (C) 2000-2005  Bastian Kleineidam
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
import wc.log


class ImageReducer (wc.filter.Filter.Filter):
    """Reduce the image size by making low quality JPEGs"""

    def __init__ (self):
        """initialize image reducer flags"""
        stages = [wc.filter.STAGE_RESPONSE_MODIFY]
        rulenames = ["imagereduce"]
        mimes = ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|'+
                 'x-xbitmap|x-xpixmap)']
        super(ImageReducer, self).__init__(stages=stages, mimes=mimes,
                                           rulenames=rulenames)
        # minimal number of bytes before we start reducing
        self.minimal_size_bytes = 5120
        # reduced JPEG quality (in percent)
        self.quality = 20

    def filter (self, data, attrs):
        """feed image data to buffer"""
        if not attrs.has_key('imgreducer_buf'):
            return data
        attrs['imgreducer_buf'].write(data)
        return ''

    def finish (self, data, attrs):
        """feed image data to buffer, then convert it and return result"""
        if not attrs.has_key('imgreducer_buf'):
            return data
        p = attrs['imgreducer_buf']
        if data:
            p.write(data)
        p.seek(0)
        try:
            img = Image.open(p)
            data = StringIO.StringIO()
            if attrs.get('imgreducer_convert'):
                img = img.convert()
            img.save(data, "JPEG", quality=self.quality, optimize=1)
        except IOError:
            # return original image data on error
            # XXX the content type is pretty sure wrong
            return p.getvalue()
        return data.getvalue()

    def get_attrs (self, url, localhost, stages, headers):
        """initialize image reducer buffer and flags"""
        if not self.applies_to_stages(stages):
            return {}
        # don't filter tiny images
        d = super(ImageReducer, self).get_attrs(url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.applies_to(url) ]
        if rules:
            if len(rules) > 1:
                wc.log.warn(wc.LOG_FILTER,
                        "more than one rule matched %r: %s", url, str(rules))
            # first rule wins
            quality = rules[0].quality
            minimal_size_bytes = rules[0].minimal_size_bytes
        else:
            quality = self.quality
            minimal_size_bytes = self.minimal_size_bytes
        try:
            length = int(headers['server'].get('Content-Length', 0))
        except ValueError:
            wc.log.warn(wc.LOG_FILTER, "invalid content length at %r", url)
            return d
        if length < 0:
            wc.log.warn(wc.LOG_FILTER, "negative content length at %r", url)
            return d
        if length == 0:
            wc.log.warn(wc.LOG_FILTER, "missing content length at %r", url)
        elif 0 < length < minimal_size_bytes:
            return d
        ctype = headers['server']['Content-Type']
        headers['data']['Content-Type'] = 'image/jpeg'
        wc.proxy.Headers.remove_headers(headers['data'], ['Content-Length'])
        d['imgreducer_buf'] = StringIO.StringIO()
        # some images have to be convert()ed before saving
        d['imgreducer_convert'] = convert(ctype)
        return d


def convert (ctype):
    """return True if an image has to be convert()ed before saving"""
    return ctype in ('image/gif',)
