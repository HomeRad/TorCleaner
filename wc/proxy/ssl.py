# -*- coding: iso-8859-1 -*-

import os
from wc import ConfigDir, AppName
from OpenSSL import SSL, crypto
from wc.log import *


def absfile (fname):
    """return absolute filename for certificate files"""
    return os.path.join(ConfigDir, fname)


def verify_server_cb (conn, cert, errnum, depth, ok):
    # This obviously has to be updated
    debug(PROXY, '%s (%s) got client certificate %s', conn, ok, cert.get_subject())
    return 1


serverctx = None
def get_server_ctx ():
    global serverctx
    if serverctx is None:
        # Initialize context
        serverctx = SSL.Context(SSL.SSLv23_METHOD)
        #serverctx.set_options(SSL.OP_NO_SSLv2)
        # Demand a certificate
        #ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
        serverctx.set_verify(SSL.VERIFY_NONE, verify_server_cb)
        serverctx.use_privatekey_file(absfile('server.pkey'))
        serverctx.use_certificate_file(absfile('server.cert'))
        serverctx.load_verify_locations(absfile('CA.cert'))
    return serverctx


def verify_client_cb (conn, cert, errnum, depth, ok):
    # XXX this obviously has to be updated
    debug(PROXY, '%s (%s) got server certificate %s', conn, ok, cert.get_subject())
    return 1


clientctx = None
def get_client_ctx ():
    global clientctx
    if clientctx is None:
        # construct client context
        clientctx = SSL.Context(SSL.SSLv23_METHOD)
        clientctx.set_verify(SSL.VERIFY_NONE, verify_client_cb)
        clientctx.use_privatekey_file(absfile('client.pkey'))
        clientctx.use_certificate_file(absfile('client.cert'))
        clientctx.load_verify_locations(absfile('CA.cert'))
    return clientctx


def create_certificates ():
    """Create certificates and private keys for webcleaner"""
    cakey = createKeyPair(TYPE_RSA, 1024)
    careq = createCertRequest(cakey, CN='Certificate Authority')
    cacert = createCertificate(careq, (careq, cakey), 0, (0, 60*60*24*365*5)) # five years
    file(absfile('CA.pkey'), 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey))
    file(absfile('CA.cert'), 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cacert))
    for (fname, cname) in [('client', '%s Client'%AppName), ('server', '%s Server'%AppName)]:
        pkey = createKeyPair(TYPE_RSA, 1024)
        req = createCertRequest(pkey, CN=cname)
        cert = createCertificate(req, (cacert, cakey), 1, (0, 60*60*24*365*5)) # five years
        file(absfile('%s.pkey'%fname), 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        file(absfile('%s.cert'%fname), 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))



#
# certgen.py
#
# Copyright (C) Martin Sjögren and AB Strakt 2001, All rights reserved
#
# $Id$
#

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

def createKeyPair (ktype, bits):
    """
    Create a public/private key pair.

    Arguments: ktype - Key type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key
    Returns:   The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(ktype, bits)
    return pkey

def createCertRequest (pkey, digest="md5", **name):
    """
    Create a certificate request.

    Arguments: pkey   - The key to associate with the request
               digest - Digestion method to use for signing, default is md5
               **name - The name of the subject of the request, possible
                        arguments are:
                          C     - Country name
                          SP    - State or province name
                          L     - Locality name
                          O     - Organization name
                          OU    - Organizational unit name
                          CN    - Common name
                          email - E-mail address
    Returns:   The certificate request in an X509Req object
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for (key,value) in name.items():
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req

def createCertificate (req, (issuerCert, issuerKey), serial, (notBefore, notAfter), digest="md5"):
    """
    Generate a certificate given a certificate request.

    Arguments: req        - Certificate reqeust to use
               issuerCert - The certificate of the issuer
               issuerKey  - The private key of the issuer
               serial     - Serial number for the certificate
               notBefore  - Timestamp (relative to now) when the certificate
                            starts being valid
               notAfter   - Timestamp (relative to now) when the certificate
                            stops being valid
               digest     - Digest method to use for signing, default is md5
    Returns:   The signed certificate in an X509 object
    """
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBefore)
    cert.gmtime_adj_notAfter(notAfter)
    cert.set_issuer(issuerCert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuerKey, digest)
    return cert

