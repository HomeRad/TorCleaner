"""compress documents on-the-fly with zlib"""
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
import re, struct, time, zlib

from wc.filter import FILTER_RESPONSE_ENCODE, compileMime
from wc.filter.Filter import Filter
from wc import remove_headers
from wc.log import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_ENCODE]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = []
# which mime types this filter applies to
mimelist = map(compileMime,  [r'text/[a-z.\-+]+',
            'application/(postscript|pdf|x-dvi)',
            'audio/(basic|midi|x-wav)',
            'image/x-portable-(any|bit|gray|pix)map',
            'x-world/x-vrml',
            ])

_compress_encs = ('gzip', 'x-gzip', 'compress', 'x-compress', 'deflate')

def gzip_header ():
    return '%s%s%s%s' % (
              '\037\213\010', # header
	      chr(0),         # flags
	      struct.pack('<L', long(time.time())), # time
              '\002\377',     # end header
              )


def getCompressObject ():
    return {'compressor': zlib.compressobj(6, zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                              zlib.DEF_MEM_LEVEL, 0),
            'header': gzip_header(),
            'crc': 0,
            'size': 0,
           }


class Compress (Filter):

    def filter (self, data, **attrs):
        """compress the string s.
        Note that compression state is saved outside of this function
        in the compression object.
        """
        if not attrs.has_key('compressobj'): return data
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                compobj['header'] = ''
                debug(FILTER, 'writing gzip header')
            compobj['size'] += len(data)
            compobj['crc'] = zlib.crc32(data, compobj['crc'])
            data = "%s%s"%(header, compobj['compressor'].compress(data))
        return data

    def finish (self, data, **attrs):
        if not attrs.has_key('compressobj'): return data
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                debug(FILTER, 'final writing gzip header')
                pass
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                data = "%s%s"%(header, compobj['compressor'].compress(data))
            else:
                data = header
            debug(FILTER, 'finishing compressor')
            data += "%s%s%s" % (compobj['compressor'].flush(zlib.Z_FINISH),
                                struct.pack('<l', compobj['crc']),
                                struct.pack('<l', compobj['size']))
        return data

    def getAttrs (self, headers, url):
        compressobj = None
        accept = headers.get('Accept-Encoding', '')
        encoding = headers.get('Content-Encoding', '').lower()
        if accept!='gzip':
            pass
        elif encoding and encoding not in _compress_encs:
            compressobj = getCompressObject()
            headers['Content-Encoding'] = encoding+', gzip\r'
        else:
            compressobj = getCompressObject()
            headers['Content-Encoding'] = 'gzip\r'
        debug(FILTER, "compress object %s", str(compressobj))
        d = Filter.getAttrs(self, headers, url)
        d['compressobj'] = compressobj
        return d
