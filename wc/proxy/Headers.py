# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
Header mangling.
"""

import re
import time
import urlparse
import mimetypes

from .. import log, LOG_PROXY
from ..http.header import WcMessage
from ..http import date as dateutil, parse_http_warning
from .decoder import UnchunkStream, GunzipStream, DeflateStream


def get_content_length(headers, default=None):
    """Get content length as int or None on error."""
    if "Content-Length" not in headers:
        if has_header_value(headers, "Transfer-Encoding", "chunked"):
            return None
        return default
    try:
        return int(headers['Content-Length'])
    except ValueError:
        log.info(LOG_PROXY, "invalid Content-Length value %r",
                    headers['Content-Length'])
    return None


def get_content_type(headers, url, default="application/octet-stream"):
    """
    Get a mime type for this url.  First check the response headers.
    If not found, try to deduce from the file extension.
    If all else fails, return default value.
    """
    ctype = headers.get('Content-Type')
    if ctype is None:
        path = urlparse.urlparse (url) [2]
        ctype = mimetypes.guess_type(path)[0]
    if ctype is None:
        return default
    return ctype


def get_wc_client_headers(host):
    """Get default webcleaner proxy request headers."""
    headers = WcMessage()
    headers['Host'] = '%s\r' % host
    headers['Accept-Encoding'] = 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5\r'
    headers['Connection'] = 'Keep-Alive\r'
    headers['Keep-Alive'] = 'timeout=300\r'
    headers['User-Agent'] = 'Calzilla/6.0\r'
    return headers


def remove_headers(headers, to_remove):
    """
    Remove entries from RFC822 headers.
    """
    for h in to_remove:
        if h in headers:
            # note: this removes all headers with that name
            del headers[h]


def has_header_value(headers, name, value):
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

def set_via_header(headers):
    """
    Set "Via:" header.
    """
    headers.addheader("Via", "1.1 unknown\r")


def remove_warning_headers(headers):
    """
    Remove old warning headers.
    """
    if "Warning" not in headers:
        return
    tokeep = []
    date = dateutil.parse_http_date(headers['Date'])
    for warning in headers.getheaders("Warning"):
        parsed = parse_http_warning(warning)
        if parsed is None:
            log.info(LOG_PROXY, "could not parse warning %r", warning)
        else:
            warndate = parsed[3]
            if warndate is None or warndate == date:
                tokeep.append(warning)
            else:
                log.debug(LOG_PROXY,
                    "delete warning %s from %s", warning, headers)
    del headers['Warning']
    for warning in tokeep:
        headers.addheader('Warning', warning+"\r")


forbidden_trailer_names = ("transfer-encoding", "content-length", "trailer")
def check_trailer_headers(headers):
    """
    Message header fields listed in the Trailer header field MUST NOT
    include the following header fields:
      . Transfer-Encoding
      . Content-Length
      . Trailer
    """
    if "Trailer" not in headers:
        return
    tokeep = []
    for trailer in headers.getheaders("Trailer"):
        if trailer.lower() not in forbidden_trailer_names:
            tokeep.append(trailer)
    del headers['Trailer']
    for trailer in tokeep:
        headers.addheader('Trailer', trailer+'\r')


def client_set_headers(headers, url):
    """
    Modify client request headers.
    """
    client_remove_multiple_headers(headers, url)
    client_remove_hop_by_hop_headers(headers)
    set_via_header(headers)


def client_remove_multiple_headers(headers, url):
    # remove dangerous double entries
    for name in ['Content-Length', 'Age', 'Date', 'Host']:
        if headers.remove_multiple_headers(name):
            log.info(LOG_PROXY,
                        "%r sent multiple %r client headers", url, name)


def server_remove_multiple_headers(headers, url):
    # remove dangerous double entries
    for name in ['Content-Length', 'Age', 'Date', 'Host']:
        if headers.remove_multiple_headers(name):
            log.info(LOG_PROXY,
                        "%r sent multiple %r server headers", url, name)

def client_remove_hop_by_hop_headers(headers):
    """
    Remove hop-by-hop headers.
    """
    to_remove = [
        'Proxy-Connection',
        'Connection',
        'Keep-Alive',
        'Upgrade',
        'Trailer',
        'TE',
    ]
    hs = headers.getheaders('Connection') + \
         headers.getheaders('Proxy-Connection')
    for h in hs:
        for v in h.split(','):
            if v not in to_remove:
                to_remove.append(v)
    remove_headers(headers, to_remove)


def client_set_encoding_headers(headers):
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


def client_remove_encoding_headers(headers):
    """
    Remove encoding headers of client request headers.
    """
    # remove encoding header
    to_remove = ["Transfer-Encoding"]
    if "Content-Length" in headers:
        log.info(LOG_PROXY,
                    'chunked encoding should not have Content-Length')
        to_remove.append("Content-Length")
    remove_headers(headers, to_remove)
    # add warning
    headers['Warning'] = "214 Transformation applied\r"


def client_get_max_forwards(headers):
    """
    Get Max-Forwards value as int and decrement it if its > 0.
    """
    try:
        mf = int(headers.get('Max-Forwards', -1))
    except ValueError:
        log.info(LOG_PROXY, "invalid Max-Forwards header value %s",
                    headers.get('Max-Forwards', ''))
        mf = -1
    if mf > 0:
        headers['Max-Forwards'] = "%d\r" % (mf-1)
    return mf


def server_set_headers(headers, url):
    """
    Modify server response headers.
    """
    server_remove_multiple_headers(headers, url)
    server_remove_hop_by_hop_headers(headers)
    set_via_header(headers)
    server_set_date_header(headers)
    remove_warning_headers(headers)
    check_trailer_headers(headers)


def server_remove_hop_by_hop_headers(headers):
    """
    Remove hop-by-hop headers.
    """
    to_remove = [
        'Connection',
        'Proxy-Authenticate',
        'Keep-Alive',
        'Upgrade',
        'Trailer',
    ]
    remove_headers(headers, to_remove)


def server_set_date_header(headers):
    """
    Add rfc2822 date if it was missing.
    """
    if 'Date' not in headers:
        now = time.time()
        headers['Date'] = "%s\r" % dateutil.get_date_rfc1123(now)


def server_set_content_headers(status, headers, mime_types, url):
    """
    Add missing content-type headers.
    """
    origmime = headers.get('Content-Type', None)
    if not origmime:
        log.info(LOG_PROXY, "Missing content type in %r", url)
    if not mime_types:
        return
    matching_mimes = [m for m in mime_types
                      if origmime and origmime.startswith(m)]
    if len(matching_mimes) > 0:
        return
    # we have a mime type override, pick the first one out of the list
    mime = mime_types[0]
    if origmime:
        if 200 <= status < 300:
            log.info(LOG_PROXY,
            _("Change content type of %r from %r to %r"), url, origmime, mime)
    else:
        log.info(LOG_PROXY,
                    _("Set content type of %r to %r"), url, mime)
    headers['Content-Type'] = "%s\r" % mime


def server_set_encoding_headers(server, filename=None):
    """
    Set encoding headers.
    """
    rewrite = server.is_rewrite()
    bytes_remaining = get_content_length(server.headers)
    to_remove = set()
    if 'Transfer-Encoding' in server.headers:
        to_remove.add('Transfer-Encoding')
        tencs = server.headers['Transfer-Encoding'].lower()
        for tenc in tencs.split(","):
            tenc = tenc.strip()
            if ";" in tenc:
                tenc = tenc.split(";", 1)[0]
            if not tenc or tenc == 'identity':
                continue
            if tenc == 'chunked':
                server.decoders.append(UnchunkStream.UnchunkStream(server))
            elif tenc in ('x-gzip', 'gzip'):
                server.decoders.append(GunzipStream.GunzipStream(server))
            elif tenc == 'deflate':
                server.decoders.append(DeflateStream.DeflateStream(server))
            else:
                log.info(LOG_PROXY,
                            "unsupported transfer encoding in %r", tencs)
        if "Content-Length" in server.headers:
            log.info(LOG_PROXY,
                        'Transfer-Encoding should not have Content-Length')
            to_remove.add("Content-Length")
        bytes_remaining = None
    if rewrite:
        to_remove.add('Content-Length')
    remove_headers(server.headers, to_remove)
    if 'Content-Length' not in server.headers:
        server.headers['Connection'] = 'close\r'
    to_remove = set()
    #if server.protocol == "HTTP/1.1":
    #    # To make pipelining possible, enable chunked encoding.
    #    server.headers['Transfer-Encoding'] = "chunked\r"
    #    server.encoders.append(ChunkStream.ChunkStream(server))
    # Compressed content (uncompress only for rewriting modules)
    if 'Content-Encoding' in server.headers:
        to_remove.add('Content-Encoding')
        cencs = server.headers['Content-Encoding'].lower()
        for cenc in cencs.split(","):
            cenc = cenc.strip()
            if ";" in cenc:
                cenc = cenc.split(";", 1)[0]
            if not cenc or cenc == 'identity':
                continue
            if filename is not None and \
               (filename.endswith(".gz") or filename.endswith(".tgz")):
                continue
            # note: do not gunzip .gz files
            if cenc in ('gzip', 'x-gzip'):
                server.decoders.append(GunzipStream.GunzipStream())
            elif cenc == 'deflate':
                server.decoders.append(DeflateStream.DeflateStream())
            else:
                log.info(LOG_PROXY,
                            "unsupported content encoding in %r", cenc)
        # remove no-transform cache control
        if server.headers.get('Cache-Control', '').lower() == 'no-transform':
            to_remove.add('Cache-Control')
        # add warning
        server.headers['Warning'] = "214 Transformation applied\r"
        if "Content-Length" in server.headers:
            to_remove.add("Content-Length")
    remove_headers(server.headers, to_remove)
    return bytes_remaining


def get_encoding_dict(msg):
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
