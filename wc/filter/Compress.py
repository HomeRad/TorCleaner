# -*- coding: iso-8859-1 -*-
"""compress documents on-the-fly with zlib"""
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
    """return a GZIP header string"""
    return '%s%s%s%s' % (
              '\037\213\010', # header
              chr(0),         # flags
              struct.pack('<L', long(time.time())), # time
              '\002\377',     # end header
              )


def get_compress_object ():
    """return attributes for Compress filter"""
    return {'compressor': zlib.compressobj(6, zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                              zlib.DEF_MEM_LEVEL, 0),
            'header': gzip_header(),
            'crc': 0,
            'size': 0,
           }


class Compress (wc.filter.Filter.Filter):
    """filter class compressing its input with zlib"""

    # which filter stages this filter applies to (see filter/__init__.py)
    orders = [wc.filter.FILTER_RESPONSE_ENCODE]
    # which rule types this filter applies to (see Rules.py)
    # all rules of these types get added with Filter.addrule()
    rulenames = []
    # which mime types this filter applies to
    mimelist = [wc.filter.compile_mime(x) for x in \
                [r'text/[a-z.\-+]+',
                 r'application/(postscript|pdf|x-dvi)',
                 r'audio/(basic|midi|x-wav)',
                 r'image/x-portable-(any|bit|gray|pix)map',
                 r'x-world/x-vrml',
               ]]

    def __init__ (self):
        """Set init compressor flag to True."""
        super(Compress, self).__init__()
        self.init_compressor = True

    def filter (self, data, **attrs):
        """Compress the string s.
           Note that compression state is saved outside of this function
           in the compression object.
        """
        if self.init_compressor:
            self.set_encoding_header(attrs)
            self.init_compressor = False
        if not attrs.has_key('compressobj'):
            return data
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                compobj['header'] = ''
                wc.log.debug(wc.LOG_FILTER, 'writing gzip header')
            compobj['size'] += len(data)
            compobj['crc'] = zlib.crc32(data, compobj['crc'])
            data = "%s%s" % (header, compobj['compressor'].compress(data))
        return data

    def finish (self, data, **attrs):
        """final compression of data, flush gzip buffers"""
        if not attrs.has_key('compressobj'):
            return data
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                wc.log.debug(wc.LOG_FILTER, 'final writing gzip header')
                pass
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                data = "%s%s" % (header, compobj['compressor'].compress(data))
            else:
                data = header
            wc.log.debug(wc.LOG_FILTER, 'finishing compressor')
            data += "%s%s%s" % (compobj['compressor'].flush(zlib.Z_FINISH),
                                struct.pack('<l', compobj['crc']),
                                struct.pack('<l', compobj['size']))
        return data

    def set_encoding_header (self, attrs):
        """fix headers for compression, and add a compression object
           to the filter attrs. Since the headers are modified this cannot
           be done in get_attrs() but only when it is clear that the content
           is going to be compressed.
        """
        headers = attrs['headers']
        accepts = wc.proxy.Headers.get_encoding_dict(headers['client'])
        encoding = headers['server'].get('Content-Encoding', '').lower()
        if 'gzip' not in accepts:
            # browser does not accept gzip encoding
            pass
        elif encoding and encoding not in _compress_encs:
            attrs['compressobj'] = get_compress_object()
            headers['data']['Content-Encoding'] = encoding+', gzip\r'
        else:
            attrs['compressobj'] = get_compress_object()
            headers['data']['Content-Encoding'] = 'gzip\r'

