# -*- coding: iso-8859-1 -*-
"""Header mangling"""

import re
import rfc822
import cStringIO as StringIO

import wc
import wc.log
import wc.magic
import wc.proxy.UnchunkStream
import wc.proxy.GunzipStream
import wc.proxy.DeflateStream


class WcMessage (rfc822.Message, object):
    """Represents a single RFC 2822-compliant message, adding functions
       handling multiple headers with the same name"""

    def __init__ (self, fp=None, seekable=True):
        """initialize message reading from given optional file descriptor"""
        if fp is None:
            fp = StringIO.StringIO()
        super(WcMessage, self).__init__(fp, seekable=seekable)

    def getallmatchingheadervalues (self, name):
        """return a list of all header values for the given header name"""
        name = name.lower() + ':'
        n = len(name)
        vals = []
        val = ""
        hit = False
        for line in self.headers:
            if line[:n].lower() == name:
                val = line[n:].strip()
                hit = True
            elif line[:1].isspace() and hit:
                val += " "+line.strip()
            else:
                if hit:
                    vals.append(val)
                val = ""
                hit = False
        return vals

    def addheader (self, name, value):
        """add given header name and value to the end of the header list.
        Multiple headers with the same name are supported"""
        self.headers.append("%s: %s\r\n" % (name, value))

    def __contains__(self, name):
        """Determine whether a message contains the named header."""
        return name.lower() in self.dict

    def __str__ (self):
        return "\n".join([ repr(s) for s in self.headers ])

    def copy (self):
        return WcMessage(fp=StringIO.StringIO("".join(self.headers)))


def get_content_length (headers, default=None):
    """get content length as int or None on error"""
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
    """get default webcleaner proxy request headers"""
    headers = WcMessage()
    headers['Host'] = '%s\r' % host
    headers['Accept-Encoding'] = 'gzip;q=1.0, deflate;q=0.9, identity;q=0.5\r'
    headers['Connection'] = 'Keep-Alive\r'
    headers['Keep-Alive'] = 'timeout=300\r'
    headers['User-Agent'] = 'Calzilla/6.0\r'
    return headers


def remove_headers (headers, to_remove):
    """remove entries from RFC822 headers"""
    for h in to_remove:
        if h in headers:
            # note: this removes all headers with that name
            del headers[h]


def has_header_value (headers, key, value):
    """return true iff headers contain given value, case of key or value
    is not important"""
    value = value.lower()
    for val in headers.getallmatchingheadervalues(key):
        if val.lower() == value:
            return True
    return False


########## HttpServer/Client header helper functions ##############

def set_via_header (headers):
    """set via header"""
    headers.addheader("Via", "1.1 unknown")


def remove_warning_headers (headers):
    """remove warning headers"""
    # XXX todo
    pass


def client_set_headers (headers):
    """modify client request headers"""
    client_remove_hop_by_hop_headers(headers)
    remove_warning_headers(headers)
    set_via_header(headers)


def client_remove_hop_by_hop_headers (headers):
    """Remove hop-by-hop headers"""
    to_remove = ['Proxy-Connection', 'Connection', 'Upgrade', 'Trailer', 'TE']
    hs = headers.getallmatchingheadervalues('Connection') + \
         headers.getallmatchingheadervalues('Proxy-Connection')
    for h in hs:
        for v in h.split(','):
            if v not in to_remove:
                to_remove.append(v)
    remove_headers(headers, to_remove)


def client_set_encoding_headers (headers):
    """set encoding headers and return compression type"""
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
    """remove encoding headers of client request headers"""
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
    """get Max-Forwards value as int and decrement it if its > 0"""
    try:
        mf = int(headers.get('Max-Forwards', -1))
    except ValueError:
        wc.log.error(wc.LOG_PROXY, "invalid Max-Forwards header value %s",
                     headers.get('Max-Forwards', ''))
        mf = -1
    if mf > 0:
        headers['Max-Forwards'] = "%d\r" % (mf-1)
    return mf


def server_set_headers (headers):
    """modify server response headers"""
    server_remove_hop_by_hop_headers(headers)
    set_via_header(headers)
    server_set_date_header(headers)
    remove_warning_headers(headers)


def server_remove_hop_by_hop_headers (headers):
    """Remove hop-by-hop headers"""
    # note: do not remove Proxy-Authenticate, we still need it
    to_remove = ['Connection', 'Keep-Alive', 'Upgrade', 'Trailer']
    remove_headers(headers, to_remove)


def server_set_date_header (headers):
    """add rfc2822 date if it was missing"""
    if not 'Date' in headers:
        from email import Utils
        headers['Date'] = "%s\r" % Utils.formatdate()


def server_set_content_headers (headers, mime_types, url):
    """add missing content-type headers"""
    origmime = headers.get('Content-Type', None)
    if not origmime:
        wc.log.warn(wc.LOG_PROXY, _("Missing content type in %r"), url)
    if not mime_types:
        return
    matching_mimes = [m for m in mime_types if origmime.startswith(m)]
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
    """set encoding headers"""
    bytes_remaining = get_content_length(headers)
    # remove content length
    if rewrite:
        remove_headers(headers, ['Content-Length'])
    # add decoders
    if headers.has_key('Transfer-Encoding'):
        # chunked encoded
        tenc = headers['Transfer-Encoding']
        if tenc != 'chunked':
            wc.log.error(wc.LOG_PROXY,
              "unknown transfer encoding %r, assuming chunked encoding", tenc)
        decoders.append(wc.proxy.UnchunkStream.UnchunkStream())
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
            decoders.append(wc.proxy.DeflateStream.DeflateStream())
        else:
            decoders.append(wc.proxy.GunzipStream.GunzipStream())
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
