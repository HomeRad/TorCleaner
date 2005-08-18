# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005  Bastian Kleineidam
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
Header mangling.
"""

import re
import rfc822
import cStringIO as StringIO

import wc
import wc.log
import wc.http.header
import wc.magic
import wc.proxy.decoder.UnchunkStream
import wc.proxy.decoder.GunzipStream
import wc.proxy.decoder.DeflateStream


def get_content_length (headers, default=None):
    """
    Get content length as int or None on error.
    """
    if not headers.has_key("Content-Length"):
        if has_header_value(headers, "Transfer-Encoding", "chunked"):
            return None
        return default
    try:
        return int(headers['Content-Length'])
    except ValueError:
        wc.log.warn(wc.LOG_PROXY, "invalid Content-Length value %r",
                    headers['Content-Length'])
    return None


def get_wc_client_headers (host):
    """
    Get default webcleaner proxy request headers.
    """
    headers = wc.http.header.WcMessage()
    headers['Host'] = '%s\r' % host
    headers['Accept-Encoding'] = 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5\r'
    headers['Connection'] = 'Keep-Alive\r'
    headers['Keep-Alive'] = 'timeout=300\r'
    headers['User-Agent'] = 'Calzilla/6.0\r'
    return headers


def remove_headers (headers, to_remove):
    """
    Remove entries from RFC822 headers.
    """
    for h in to_remove:
        if h in headers:
            # note: this removes all headers with that name
            del headers[h]


def has_header_value (headers, name, value):
    """
    Return true iff headers contain given value, case of key or value
    is not important.
    """
    value = value.lower()
    for val in headers.getheaders(name):
        if val.lower() == value:
            return True
    return False


########## HttpServer/Client header helper functions ##############

def set_via_header (headers):
    """
    Set "Via:" header.
    """
    headers.addheader("Via", "1.1 unknown")


def remove_warning_headers (headers):
    """
    Remove warning headers.
    """
    # XXX todo
    pass


def client_set_headers (headers):
    """
    Modify client request headers.
    """
    client_remove_double_entries(headers)
    client_remove_hop_by_hop_headers(headers)
    remove_warning_headers(headers)
    set_via_header(headers)


def client_remove_double_entries (headers):
    # remove dangerous double entries
    for name in ['Content-Length', 'Age', 'Date', 'Host']:
        if headers.remove_multiple_headers(name):
            wc.log.warn(wc.LOG_PROXY, "removed multiple %r headers", name);


def client_remove_hop_by_hop_headers (headers):
    """
    Remove hop-by-hop headers.
    """
    to_remove = ['Proxy-Connection', 'Connection', 'Upgrade', 'Trailer', 'TE']
    hs = headers.getheaders('Connection') + \
         headers.getheaders('Proxy-Connection')
    for h in hs:
        for v in h.split(','):
            if v not in to_remove:
                to_remove.append(v)
    remove_headers(headers, to_remove)


def client_set_encoding_headers (headers):
    """
    Set encoding headers and return compression type.
    """
    # remember if client understands gzip
    compress = 'identity'
    encodings = headers.get('Accept-Encoding', '')
    for accept in encodings.split(','):
        if ';' in accept:
            accept, q = accept.split(';', 1)
        if accept.strip().lower() in ('gzip', 'x-gzip'):
            compress = 'gzip'
            break
    # we understand gzip, deflate and identity
    headers['Accept-Encoding'] = 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5\r'
    return compress


def client_remove_encoding_headers (headers):
    """
    Remove encoding headers of client request headers.
    """
    # remove encoding header
    to_remove = ["Transfer-Encoding"]
    if headers.has_key("Content-Length"):
        wc.log.warn(wc.LOG_PROXY,
                    'chunked encoding should not have Content-Length')
        to_remove.append("Content-Length")
    remove_headers(headers, to_remove)
    # add warning
    headers['Warning'] = "214 Transformation applied\r"


def client_get_max_forwards (headers):
    """
    Get Max-Forwards value as int and decrement it if its > 0.
    """
    try:
        mf = int(headers.get('Max-Forwards', -1))
    except ValueError:
        wc.log.warn(wc.LOG_PROXY, "invalid Max-Forwards header value %s",
                    headers.get('Max-Forwards', ''))
        mf = -1
    if mf > 0:
        headers['Max-Forwards'] = "%d\r" % (mf-1)
    return mf


def server_set_headers (headers):
    """
    Modify server response headers.
    """
    server_remove_hop_by_hop_headers(headers)
    set_via_header(headers)
    server_set_date_header(headers)
    remove_warning_headers(headers)


def server_remove_hop_by_hop_headers (headers):
    """
    Remove hop-by-hop headers.
    """
    # note: do not remove Proxy-Authenticate, we still need it
    to_remove = ['Connection', 'Keep-Alive', 'Upgrade', 'Trailer']
    remove_headers(headers, to_remove)


def server_set_date_header (headers):
    """
    Add rfc2822 date if it was missing.
    """
    if not 'Date' in headers:
        from email import Utils
        headers['Date'] = "%s\r" % Utils.formatdate()


def server_set_content_headers (headers, mime_types, url):
    """
    Add missing content-type headers.
    """
    origmime = headers.get('Content-Type', None)
    if not origmime:
        wc.log.warn(wc.LOG_PROXY, _("Missing content type in %r"), url)
    if not mime_types:
        return
    matching_mimes = [m for m in mime_types
                      if origmime and origmime.startswith(m)]
    if len(matching_mimes) > 0:
        return
    # we have a mime type override, pick the first one out of the list
    mime = mime_types[0]
    if origmime:
        wc.log.warn(wc.LOG_PROXY,
            _("Change content type of %r from %r to %r"), url, origmime, mime)
    else:
        wc.log.warn(wc.LOG_PROXY,
                    _("Set content type of %r to %r"), url, mime)
    headers['Content-Type'] = "%s\r" % mime


def server_set_encoding_headers (headers, rewrite, decoders, bytes_remaining,
                                 filename=None):
    """
    Set encoding headers.
    """
    bytes_remaining = get_content_length(headers)
    # remove content length
    if rewrite:
        remove_headers(headers, ['Content-Length'])
    # add decoders
    if headers.has_key('Transfer-Encoding'):
        # chunked encoded
        tenc = headers['Transfer-Encoding']
        if tenc != 'chunked':
            wc.log.warn(wc.LOG_PROXY,
              "unknown transfer encoding %r, assuming chunked encoding", tenc)
        decoders.append(wc.proxy.decoder.UnchunkStream.UnchunkStream())
        # remove encoding header
        to_remove = ["Transfer-Encoding"]
        if headers.has_key("Content-Length"):
            wc.log.warn(wc.LOG_PROXY,
                        'chunked encoding should not have Content-Length')
            to_remove.append("Content-Length")
            bytes_remaining = None
        remove_headers(headers, to_remove)
        # add warning
        headers['Warning'] = "214 Transformation applied\r"
    # only decompress on rewrite
    if not rewrite:
        return bytes_remaining
    # Compressed content (uncompress only for rewriting modules)
    encoding = headers.get('Content-Encoding', '').lower()
    # note: do not gunzip .gz files
    if encoding in ('gzip', 'x-gzip', 'deflate') and \
       (filename is None or not filename.endswith(".gz")):
        if encoding == 'deflate':
            decoders.append(wc.proxy.decoder.DeflateStream.DeflateStream())
        else:
            decoders.append(wc.proxy.decoder.GunzipStream.GunzipStream())
        # remove encoding because we unzip the stream
        to_remove = ['Content-Encoding']
        # remove no-transform cache control
        if headers.get('Cache-Control', '').lower() == 'no-transform':
            to_remove.append('Cache-Control')
        remove_headers(headers, to_remove)
        # add warning
        headers['Warning'] = "214 Transformation applied\r"
    elif encoding and encoding!='identity':
        wc.log.warn(wc.LOG_PROXY, _("unsupported encoding: %r"), encoding)
        # do not disable filtering for unknown content-encodings
        # this could result in a DoS attack (server sending garbage
        # as content-encoding)
    if not headers.has_key('Content-Length'):
        headers['Connection'] = 'close\r'
    return bytes_remaining


def get_encoding_dict (msg):
    """
    Get encodings and their associated preference values.
    """
    res = {}
    encs = msg.get('Accept-Encoding', '').split(",")
    for enc in encs:
        enc = enc.strip()
        pref = None
        if ";" in enc:
            enc, pref = enc.split(";")
            pref = pref.strip()
        res[enc.lower()] = pref
    return res


is_header = re.compile("\s*[-a-zA-Z_]+:\s+").search
