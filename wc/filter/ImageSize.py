# -*- coding: iso-8859-1 -*-
# Copyright (C) 2000-2009 Bastian Kleineidam
"""
Filter images by size.
"""

import os
import cStringIO as StringIO
from .. import log, LOG_FILTER, configuration, HasPil, TemplateDir
from . import Filter, STAGE_RESPONSE_MODIFY
if HasPil:
    import Image


class ImageSize(Filter.Filter):
    """
    Base filter class which is using the GifParser to deanimate the
    incoming GIF stream.
    """

    enable = HasPil

    def __init__(self):
        """
        Initialize list of allowed sizes.
        """
        stages = [STAGE_RESPONSE_MODIFY]
        rulenames = ['image']
        mimes = ['image/(jpeg|png|gif|bmp|x-ms-bmp|pcx|tiff|'+
                 'x-xbitmap|x-xpixmap)']
        super(ImageSize, self).__init__(stages=stages, mimes=mimes,
                                        rulenames=rulenames)
        # minimal amount of image data for PIL to read header info:
        # 4096 bytes is enough for most images; the value is increased
        # when it is not big enough
        self.min_bufsize = 4096
        fname = os.path.join(TemplateDir, configuration.config['gui_theme'])
        fname = os.path.join(fname, "blocked.png")
        f = file(fname)
        self.blockdata = f.read()
        f.close()

    def filter(self, data, attrs):
        """
        See if image will be blocked.

        @return: block image data if image size is not allowed,
            or original image data
        @rtype: string
        """
        if 'imgsize_buf' not in attrs:
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

    def finish(self, data, attrs):
        """
        See if image will be blocked.

        @return: block image data if image size is not allowed,
            or original image data
        @rtype: string
        """
        # note: if attrs['blocked'] is True, then the blockdata is
        # already sent out
        if 'imgsize_buf' not in attrs:
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
            # there was no data, probably a 304 Not Modified answer
            # just return
            return ''
        attrs['imgsize_blocked'] = \
          not self.check_sizes(buf, attrs['imgsize_sizes'], url, finish=True)
        data = buf.getvalue()
        buf.close()
        if attrs['imgsize_blocked']:
            return self.blockdata
        return data

    def check_sizes(self, buf, sizes, url, finish=False):
        """
        Try to parse image size from buf and check against size list.

        @return: False if image size is blocked, else True
        @rtype: bool
        """
        pos = buf.tell()
        assert pos > 0
        try:
            buf.seek(0)
            img = Image.open(buf, 'r')
            buf.seek(pos)
            for size, formats in sizes:
                if size == img.size:
                    # size matches, look for format restriction
                    if not formats:
                        log.debug(LOG_FILTER, "Blocking image size %s", size)
                        return False
                    elif img.format.lower() in formats:
                        log.debug(LOG_FILTER, "Blocking image size %s", size)
                        return False
        except IOError:
            if finish:
                log.exception(LOG_FILTER,
                                 "Could not get image size from %r", url)
            else:
                assert pos > self.min_bufsize
                # wait for more data
                buf.seek(pos)
                self.min_bufsize = pos+4096
                assert buf.tell() < self.min_bufsize
        return True

    def update_attrs(self, attrs, url, localhost, stages, headers):
        """
        Initialize image buffer.
        """
        if not self.applies_to_stages(stages):
            return
        parent = super(ImageSize, self)
        parent.update_attrs(attrs, url, localhost, stages, headers)
        # check PIL support
        if not HasPil:
            return
        # weed out the rules that don't apply to this url
        rules = [rule for rule in self.rules if rule.applies_to_url(url)]
        if not rules:
            return
        sizes = [((r.width, r.height), r.formats) for r in rules]
        attrs['imgsize_sizes'] = sizes
        attrs['imgsize_buf'] = StringIO.StringIO()
        attrs['imgsize_blocked'] = False
