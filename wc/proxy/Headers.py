"""Header mangling"""
from wc import remove_headers
from wc.log import *

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
    to_remove = ['Connection', 'Keep-Alive', 'Upgrade', 'Trailer', 'TE']
    remove_headers(headers, to_remove)


def client_set_connection_headers (headers):
    """Rename Proxy-Connection to Connection"""
    # XXX handle Connection values
    if headers.has_key('Proxy-Connection'):
        val = headers['Proxy-Connection'].strip()
        headers['Connection'] = val+"\r"
        remove_headers(headers, ['Proxy-Connection'])


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
    if headers.get("Content-Length") is not None:
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
    to_remove = ['Connection', 'Keep-Alive', 'Upgrade', 'Trailer',
                 'Proxy-Authenticate']
    remove_headers(headers, to_remove)


def server_set_date_header (headers):
    """add rfc2822 date if it was missing"""
    if not headers.has_key('Date'):
        from email import Utils
        headers['Date'] = "%s\r"%Utils.formatdate()


