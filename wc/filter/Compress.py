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
Compress documents on-the-fly with zlib.
"""

import struct
import time
import zlib
import wc
import wc.log
import wc.filter
import wc.filter.Filter
import wc.proxy.Headers


_compress_encs = ('gzip', 'x-gzip', 'compress', 'x-compress', 'deflate')

def gzip_header ():
    """
    Return a GZIP header string.
    """
    return '%s%s%s%s' % (
              '\037\213\010', # header
              chr(0),         # flags
              struct.pack('<L', long(time.time())), # time
              '\002\377',     # end header
              )


def get_compress_object ():
    """
    Return attributes for Compress filter.
    """
    return {'compressor': zlib.compressobj(9, zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                              zlib.DEF_MEM_LEVEL, 0),
            'header': gzip_header(),
            'crc': 0,
            'size': 0,
           }

def compress (data, compobj):
    """
    Compress data and adjust CRC of the compressor.

    @return: compressed data
    @rtype: string
    """
    if data:
        wc.log.debug(wc.LOG_FILTER, "compressing %d bytes", len(data))
        compobj['size'] += len(data)
        compobj['crc'] = zlib.crc32(data, compobj['crc'])
        compressed = compobj['compressor'].compress(data)
    else:
        compressed = ""
    if compobj['header']:
        wc.log.debug(wc.LOG_FILTER, 'writing gzip header')
        compressed = compobj['header'] + compressed
        compobj['header'] = ''
    return compressed


class Compress (wc.filter.Filter.Filter):
    """
    Filter class compressing its input with zlib.
    """

    enable = True

    def __init__ (self):
        """
        Set init compressor flag to True.
        """
        stages = [wc.filter.STAGE_RESPONSE_ENCODE]
        mimes = [r'text/[a-z.\-+]+',
                 r'application/(postscript|pdf|x-dvi)',
                 r'audio/(basic|midi|x-wav)',
                 r'image/x-portable-(any|bit|gray|pix)map',
                 r'x-world/x-vrml',
                ]
        super(Compress, self).__init__(stages=stages, mimes=mimes)
        self.init_compressor = True

    def filter (self, data, attrs):
        """
        Compress the string s.
        Note that compression state is saved outside of this function
        in the compression object.
        """
        if self.init_compressor:
            self.set_encoding_header(attrs)
            self.init_compressor = False
        if not attrs.has_key('compressobj'):
            wc.log.debug(wc.LOG_FILTER, 'nothing to compress')
            return data
        return compress(data, attrs['compressobj'])

    def finish (self, data, attrs):
        """
        Final compression of data, flush gzip buffers.
        """
        if self.init_compressor:
            self.set_encoding_header(attrs)
            self.init_compressor = False
        if not attrs.has_key('compressobj'):
            wc.log.debug(wc.LOG_FILTER, 'nothing to compress')
            return data
        compobj = attrs['compressobj']
        compressed = compress(data, compobj)
        wc.log.debug(wc.LOG_FILTER, 'finishing compressor')
        compressed += "%s%s%s" % (compobj['compressor'].flush(),
                                  struct.pack('<l', compobj['crc']),
                                  struct.pack('<l', compobj['size']))
        return compressed

    def set_encoding_header (self, attrs):
        """
        Fix headers for compression, and add a compression object
        to the filter attrs. Since the headers are modified this cannot
        be done in get_attrs() but only when it is clear that the content
        is going to be compressed.
        """
        headers = attrs['headers']
        accepts = wc.proxy.Headers.get_encoding_dict(headers['client'])
        encoding = headers['server'].get('Content-Encoding', '')
        encoding = encoding.strip().lower()
        if 'gzip' not in accepts:
            # browser does not accept gzip encoding
            assert 'compressobj' not in attrs, \
                "unexpected gzip compress object: "+headers
        elif encoding and encoding not in _compress_encs:
            attrs['compressobj'] = get_compress_object()
            headers['data']['Content-Encoding'] = encoding+', gzip\r'
        else:
            attrs['compressobj'] = get_compress_object()
            headers['data']['Content-Encoding'] = 'gzip\r'

