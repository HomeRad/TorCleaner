"""compress documents on-the-fly with zlib"""
# Copyright (C) 2000,2001  Bastian Kleineidam
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
import re,struct,time,zlib,wc

from wc.filter import FILTER_RESPONSE_ENCODE, Filter, compileMime
from wc import debug
from wc.debug_levels import *

# which filter stages this filter applies to (see filter/__init__.py)
orders = [FILTER_RESPONSE_ENCODE]
# which rule types this filter applies to (see Rules.py)
# all rules of these types get added with Filter.addrule()
rulenames = []
# which mime types this filter applies to
mimelist = map(compileMime,  ['text/.+',
            'application/postscript',
            'application/pdf',
            'application/x-dvi',
            'audio/basic',
            'audio/midi',
            'audio/x-wav',
            'image/x-portable-anymap',
            'image/x-portable-bitmap',
            'image/x-portable-graymap',
            'image/x-portable-pixmap',
            'x-world/x-vrml',
            ])

def gzip_header ():
    return '%s%s%s%s' % (
              '\037\213\010', # header
	      chr(0),         # flags
	      struct.pack('<L', long(time.time())), # time
              '\002\377',     # end header
              )
BASIC_CRC = zlib.crc32('')
COMPRESS_RE = re.compile(r'(?i)(compress|gzip|bzip2)')


def getCompressObject ():
    return {'compressor': zlib.compressobj(6, zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
                                              zlib.DEF_MEM_LEVEL, 0),
            'header': gzip_header(),
            'crc': BASIC_CRC,
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
                #debug(NIGHTMARE, 'writing gzip header')
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                #debug(NIGHTMARE, 'compressing', `data`)
                data = "%s%s"%(header, compobj['compressor'].compress(data))
            else:
                data = header
        return data

    def finish (self, data, **attrs):
        if not attrs.has_key('compressobj'): return data
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                #debug(NIGHTMARE, 'final writing gzip header')
                pass
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                #debug(NIGHTMARE, 'final compressing', `data`)
                data = "%s%s"%(header,
                               compobj['compressor'].compress(data))
            else:
                data = header
            #debug(NIGHTMARE, 'finishing compressor')
            data += compobj['compressor'].flush(zlib.Z_FINISH) + \
	            struct.pack('<l', compobj['crc']) + \
		    struct.pack('<l', compobj['size'])
        return data

    def getAttrs (self, headers, url):
        if headers.has_key('content-encoding'):
            if COMPRESS_RE.search(headers['content-encoding']):
                compressobj = None
            else:
                compressobj = getCompressObject()
                headers['Content-Encoding'] += ', gzip'
        else:
            compressobj = getCompressObject()
            headers['Content-Encoding'] = 'gzip\r'
        #debug(HURT_ME_PLENTY, "compress filter getAttrs", `headers.headers`)
        d = Filter.getAttrs(self, headers, url)
        d['compressobj'] = compressobj
        return d
