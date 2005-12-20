# -*- coding: iso-8859-1 -*-
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
"""
Reduce big images to JPGs to save bandwidth.
"""

import cStringIO as StringIO
import wc
import wc.filter
import wc.filter.Filter
import wc.proxy.Headers
import wc.log
if wc.HasPil:
    import Image


# XXX honor minimal_size_bytes
class ImageReducer (wc.filter.Filter.Filter):
    """
    Reduce the image size by making low quality JPEGs.
    """

    enable = wc.HasPil

    def __init__ (self):
        """
        Initialize image reducer flags.
        """
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
        self.init_image_reducer = True

    def filter (self, data, attrs):
        """
        Feed image data to buffer.
        """
        if self.init_image_reducer:
            self.set_ctype_header(attrs)
            self.init_image_reducer = False
        if not attrs.has_key('imgreducer_buf'):
            return data
        attrs['imgreducer_buf'].write(data)
        return ''

    def finish (self, data, attrs):
        """
        Feed image data to buffer, then convert it and return result.
        """
        if self.init_image_reducer:
            self.set_ctype_header(attrs)
            self.init_image_reducer = False
        if not attrs.has_key('imgreducer_buf'):
            return data
        p = attrs['imgreducer_buf']
        quality = attrs['imgreducer_quality']
        if data:
            p.write(data)
        p.seek(0)
        try:
            img = Image.open(p)
            data = StringIO.StringIO()
            # Only greyscale (L) and RGB images can be written directly to
            # JPEG. All other modes (ie. palette found in GIF and PNG)
            # have to be converted.
            if img.mode not in ('RGB', 'L'):
                img.draft("RGB", img.size)
                img = img.convert("RGB")
            img.save(data, "JPEG", quality=quality, optimize=1)
        except IOError, msg:
            # return original image data on error
            wc.log.warn(wc.LOG_FILTER,
                "I/O error reading image data %r: %s", attrs['url'], str(msg))
            # XXX the content type is pretty sure wrong
            return p.getvalue()
        return data.getvalue()

    def set_ctype_header (self, attrs):
        """
        Set Content-Type header value to JPEG.
        """
        headers = attrs['headers']
        headers['data']['Content-Type'] = 'image/jpeg'
        wc.proxy.Headers.remove_headers(headers['data'], ['Content-Length'])

    def update_attrs (self, attrs, url, localhost, stages, headers):
        """
        Initialize image reducer buffer and flags.
        """
        if not self.applies_to_stages(stages):
            return
        # don't filter tiny images
        parent = super(ImageReducer, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.applies_to_url(url) ]
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
            return
        if length < 0:
            wc.log.warn(wc.LOG_FILTER, "negative content length at %r", url)
            return
        if length == 0:
            wc.log.warn(wc.LOG_FILTER, "missing content length at %r", url)
        elif 0 < length < minimal_size_bytes:
            return
        attrs['imgreducer_buf'] = StringIO.StringIO()
        attrs['imgreducer_quality'] = quality
        attrs['imgreducer_minsize'] = minimal_size_bytes
        # remember original content type in case of error
        ctype = headers['server'].get('Content-Type')
        attrs['imgreducer_ctype'] = ctype

