# -*- coding: iso-8859-1 -*-
"""Header mangling"""

__version__ = "$Revision$"[11:-2]
__date__    = "$Date$"[7:-2]

from wc.log import *
from rfc822 import Message
from UnchunkStream import UnchunkStream
from GunzipStream import GunzipStream
from DeflateStream import DeflateStream
import mimetypes
# add bzip encoding
mimetypes.encodings_map['.bz2'] = 'x-bzip2'


class WcMessage (Message):
    """Represents a single RFC 2822-compliant message."""

    def getall (self, name):
        """return a list of all values matching name"""
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
                val += "\n "+line.strip()
            else:
                if hit:
                    vals.append(val)
                val = ""
                hit = False
        return vals


    def __contains__(self, name):
        """Determine whether a message contains the named header."""
        return name.lower() in self.dict


def str_headers (headers):
    if hasattr(headers, "headers"):
        return "\n".join([ repr(s) for s in headers.headers ])
    return "\n".join([ repr("%s: %s\r"%(key, item)) for key, item in headers.items() ])


def remove_headers (headers, to_remove):
    """remove entries from RFC822 headers"""
    for h in to_remove:
        if h in headers:
            # note: this removes all headers with that name
            del headers[h]


def has_header_value (headers, key, value):
    if hasattr(headers, "getallmatchingheaders"):
        # rfc822.Message() object
        for h in headers.getallmatchingheaders(key):
            if h.strip().lower() == value.lower():
                return True
        return False
    return headers.get(key, '').lower() == value.lower()


def get_header_values (headers, key):
    return [ h.split(':')[1].strip() \
             for h in headers.getallmatchingheaders(key) ]


def set_via_header (headers):
    """set via header"""
    # XXX does not work with multiple existing via headers
    via = headers.get('Via', "").strip()
    if via: via += ", "
    via += "1.1 unknown\r"
    headers['Via'] = via


def remove_warning_headers (headers):
    # XXX todo
    pass


def client_set_headers (headers):
    client_remove_hop_by_hop_headers(headers)
    remove_warning_headers(headers)
    set_via_header(headers)
    client_set_connection_headers(headers)
    return client_set_encoding_headers(headers)


def client_remove_hop_by_hop_headers (headers):
    """Remove hop-by-hop headers"""
    to_remove = ['Proxy-Connection', 'Connection', 'Upgrade', 'Trailer', 'TE']
    hs = headers.getall('Connection') + headers.getall('Proxy-Connection')
    for h in hs:
        for v in h.split(','):
            if v not in to_remove:
                to_remove.append(v)
    remove_headers(headers, to_remove)


def client_set_connection_headers (headers):
    """Set our own connection headers"""
    headers['Connection'] = 'Keep-Alive\r'
    headers['Keep-Alive'] = 'timeout=300\r'


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
    # remove encoding header
    to_remove = ["Transfer-Encoding"]
    if headers.has_key("Content-Length"):
        warn(PROXY, 'chunked encoding should not have Content-Length')
        to_remove.append("Content-Length")
    remove_headers(headers, to_remove)
    # add warning
    headers['Warning'] = "214 Transformation applied\r"


def client_get_max_forwards (headers):
    """get Max-Forwards value as int and decrement it if its > 0"""
    try:
        mf = int(headers.get('Max-Forwards', -1))
    except ValueError:
        error(PROXY, "invalid Max-Forwards header value %s", headers.get('Max-Forwards', ''))
        mf = -1
    if mf>0:
        headers['Max-Forwards'] = "%d\r" % (mf-1)
    return mf


def server_set_headers (headers):
    server_remove_hop_by_hop_headers(headers)
    set_via_header(headers)
    server_set_date_header(headers)
    remove_warning_headers(headers)


def server_remove_hop_by_hop_headers (headers):
    """Remove hop-by-hop headers"""
    # note: do not remove Proxy-Authenticate, we still need it
    to_remove = ['Connection', 'Keep-Alive', 'Upgrade', 'Trailer',]
    remove_headers(headers, to_remove)


def server_set_date_header (headers):
    """add rfc2822 date if it was missing"""
    if not 'Date' in headers:
        from email import Utils
        headers['Date'] = "%s\r"%Utils.formatdate()


def server_set_content_headers (headers, document, mime, url):
    """add missing content-type headers"""
    # check content-type against our own guess
    i = document.find('?')
    if i>0:
        document = document[:i]
    gm = mimetypes.guess_type(document, None)
    ct = headers.get('Content-Type', None)
    if mime:
        if ct is None:
            warn(PROXY, i18n._("add Content-Type %s in %s"), `mime`, `url`)
            headers['Content-Type'] = "%s\r"%mime
        elif not ct.startswith(mime):
            i = ct.find(';')
            if i == -1:
                val = mime
            else:
                val = mime + ct[i:]
            warn(PROXY, i18n._("set Content-Type from %s to %s in %s"),
                 `str(ct)`, `val`, `url`)
            headers['Content-Type'] = "%s\r"%val
    elif gm[0]:
        # guessed an own content type
        if ct is None:
            warn(PROXY, i18n._("add Content-Type %s to %s"), `gm[0]`, `url`)
            headers['Content-Type'] = "%s\r"%gm[0]
    # hmm, fix application/x-httpd-php*
    if headers.get('Content-Type', '').lower().startswith('application/x-httpd-php'):
        warn(PROXY, i18n._("fix x-httpd-php Content-Type"))
        headers['Content-Type'] = 'text/html\r'


def server_set_encoding_headers (headers, rewrite, decoders, compress, bytes_remaining):
    """set encoding headers"""
    # add client accept-encoding value
    headers['Accept-Encoding'] = "%s\r"%compress
    if headers.has_key('Content-Length'):
        bytes_remaining = int(headers['Content-Length'])
        debug(PROXY, "Server: %d bytes remaining", bytes_remaining)
        if rewrite:
            remove_headers(headers, ['Content-Length'])
    else:
        bytes_remaining = None
    # add decoders
    if headers.has_key('Transfer-Encoding'):
        # chunked encoded
        tenc = headers['Transfer-Encoding']
        if tenc != 'chunked':
            error(PROXY, "Server: unknown transfer encoding %s, assuming chunked encoding", `tenc`)
        decoders.append(UnchunkStream())
        # remove encoding header
        to_remove = ["Transfer-Encoding"]
        if headers.has_key("Content-Length"):
            warn(PROXY, i18n._('chunked encoding should not have Content-Length'))
            to_remove.append("Content-Length")
            bytes_remaining = None
        remove_headers(headers, to_remove)
        # add warning
        headers['Warning'] = "214 Transformation applied\r"
    # only decompress on rewrite
    if not rewrite: return
    # Compressed content (uncompress only for rewriting modules)
    encoding = headers.get('Content-Encoding', '').lower()
    # XXX test for .gz files ???
    if encoding in ('gzip', 'x-gzip', 'deflate'):
        if encoding=='deflate':
            decoders.append(DeflateStream())
        else:
            decoders.append(GunzipStream())
        # remove encoding because we unzip the stream
        to_remove = ['Content-Encoding']
        # remove no-transform cache control
        if headers.get('Cache-Control', '').lower()=='no-transform':
            to_remove.append('Cache-Control')
        remove_headers(headers, to_remove)
        # add warning
        headers['Warning'] = "214 Transformation applied\r"
    elif encoding and encoding!='identity':
        warn(PROXY, i18n._("unsupported encoding: %s"), `encoding`)
        # do not disable filtering for unknown content-encodings
        # this could result in a DoS attack (server sending garbage
        # as content-encoding)
    return bytes_remaining

