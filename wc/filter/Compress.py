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

from wc.filter.Filter import Filter
from wc.filter import FILTER_RESPONSE_ENCODE
from wc import debug
from wc.debug_levels import *

orders = [FILTER_RESPONSE_ENCODE]
rulenames = []

GZIP_HEADER = '%s%s%s%s' % (
              '\037\213\010', # header
	      chr(0),         # flags
	      struct.pack('<L', long(time.time())), # time
              '\002\377',     # end header
              )
BASIC_CRC = zlib.crc32('')
COMPRESS_RE = re.compile(r'(compress|gzip|bzip2)', re.I)


def getCompressObject():
    return {'compressor': zlib.compressobj(9, zlib.DEFLATED,
                                             -zlib.MAX_WBITS,
					      zlib.DEF_MEM_LEVEL, 0),
            'header': GZIP_HEADER,
            'crc': BASIC_CRC,
            'size': 0,
           }


class Compress(Filter):
    # XXX I want to write text/*, requires re.match in mimelist matching
    mimelist = (
            'text/css',
            'text/html',
            'text/javascript',
            'text/plain',
            'text/richtext',
            'text/xml',
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
            )

    def filter(self, data, **attrs):
        """compress the string s.
        Note that compression state is saved outside of this function
        in the compression object.
        """
        compobj = attrs['compressobj']
        if compobj:
            header = compobj['header']
            if header:
                compobj['header'] = ''
                #debug(NIGHTMARE, 'writing gzip header\n')
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                #debug(NIGHTMARE, 'compressing %s\n' % `data`)
                data = header + compobj['compressor'].compress(data)
            else:
                data = header
        return data

    def finish(self, data, **attrs):
        compobj = attrs['compressobj']
        if compobj:
            if data:
                compobj['size'] += len(data)
                compobj['crc'] = zlib.crc32(data, compobj['crc'])
                #debug(NIGHTMARE, 'final compressing %s\n' % `data`)
                data = compobj['compressor'].compress(data)
            #debug(NIGHTMARE, 'finishing compressor\n')
            data += compobj['compressor'].flush() + \
	            struct.pack('<l', compobj['crc']) + \
		    struct.pack('<l', compobj['size'])
        return data

    def getAttrs(self, headers):
        if headers.has_key('content-encoding'):
            if COMPRESS_RE.search(headers['content-encoding']):
                compressobj = None
            else:
                compressobj = getCompressObject()
                headers['content-encoding'] += ', gzip'
        else:
            compressobj = getCompressObject()
            headers['content-encoding'] = 'gzip'
        return {'compressobj': compressobj}
