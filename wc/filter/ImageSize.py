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

import Image, os
from StringIO import StringIO
from wc.filter import FILTER_RESPONSE_MODIFY, compileMime, compileRegex
from wc.filter.Filter import Filter
from wc.log import *
from wc import TemplateDir, config

class ImageSize (Filter):
    """Base filter class which is using the GifParser to deanimate the
       incoming GIF stream"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [FILTER_RESPONSE_MODIFY]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = ['image']
    # which mime types this filter applies to
    mimelist = [compileMime(x) for x in ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|x-xbitmap|x-xpixmap)']]


    def __init__ (self):
        super(ImageSize, self).__init__()
        # minimal amount of image data for PIL to read header info
        # 6000 bytes should be enough, even for JPEG images
        self.min_bufsize = 6000
        fname = os.path.join(TemplateDir, config['gui_theme'])
        fname = os.path.join(fname, "blocked.png")
        f = file(fname)
        self.blockdata = f.read()
        f.close()


    def addrule (self, rule):
        super(ImageSize, self).addrule(rule)
        compileRegex(rule, "matchurl")
        compileRegex(rule, "dontmatchurl")


    def filter (self, data, **attrs):
        if not attrs.has_key('buffer'):
            # do not block this image
            return data
        if attrs['blocked']:
            # block this image
            return ''
        if attrs['buffer'].closed:
            return data
        buf = attrs['buffer']
        buf.write(data)
        if buf.tell() > self.min_bufsize:
            attrs['blocked'] = not self.check_sizes(buf, attrs['sizes'], attrs['url'])
            data = buf.getvalue()
            buf.close()
            if attrs['blocked']:
                return self.blockdata
            return data
        return ''


    def finish (self, data, **attrs):
        if not attrs.has_key('buffer'):
            # do not block this image
            return data
        if attrs['blocked']:
            # block this image
            return ''
        if attrs['buffer'].closed:
            return data
        buf = attrs['buffer']
        buf.write(data)
        attrs['blocked'] = not self.check_sizes(buf, attrs['sizes'], attrs['url'])
        data = buf.getvalue()
        buf.close()
        if attrs['blocked']:
            return self.blockdata
        return data


    def check_sizes (self, buf, sizes, url):
        if buf.tell()==0:
            error(FILTER, "Empty image data found at %s", `url`)
            return True
        try:
            buf.seek(0)
            img = Image.open(buf, 'r')
            for size, formats in sizes:
                if size==img.size:
                    # size matches, look for format restriction
                    if not formats:
                        debug(FILTER, "Blocking image size %s", str(size))
                        return False
                    elif img.format.lower() in formats:
                        debug(FILTER, "Blocking image size %s", str(size))
                        return False
        except IOError:
            exception(FILTER, "Could not get image size from %s", `url`)
        return True


    def getAttrs (self, headers, url):
        # weed out the rules that don't apply to this url
        rules = [ rule for rule in self.rules if rule.appliesTo(url) ]
        if not rules:
            return {}
        sizes = [((rule.width, rule.height), rule.formats) for rule in rules]
        return {'buffer': StringIO(),
                'sizes': sizes,
                'url': url,
                'blocked': False}

