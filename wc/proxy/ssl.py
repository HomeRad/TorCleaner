# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
"""
SSL related utility functions.
"""

import os
from .. import log, LOG_PROXY, AppName
from OpenSSL import SSL, crypto


def exist_certificates(configdir):
    """
    Ensure that all certificates are present in given config directory.
    """
    for fname in "CA", "server", "client":
        if not (os.path.exists(os.path.join(configdir, '%s.cert'%fname)) and
                os.path.exists(os.path.join(configdir, '%s.pkey'%fname))):
            return False
    return True


def dump_certificate(cert, filetype=crypto.FILETYPE_PEM):
    """
    A helper to dump an incoming cert as a PEM.
    """
    return crypto.dump_certificate(filetype, cert)


def verify_server_cb(conn, cert, errnum, depth, ok):
    """
    The browser (or commandline client) has sent a SSL certificate to
    the WebCleaner server.
    """
    expired = cert.has_expired()
    if expired:
        log.info(LOG_PROXY, "%s expired certificate %s", conn,
                    cert.get_subject())
    return not expired


serverctx = None
def get_serverctx(configdir):
    """
    Get SSL context for server.
    """
    global serverctx
    if serverctx is None:
        # Initialize context
        serverctx = SSL.Context(SSL.SSLv23_METHOD)
        serverctx.set_options(SSL.OP_NO_SSLv2)
        # Demand a certificate
        #serverctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
        #                     verify_server_cb)
        serverctx.set_verify(SSL.VERIFY_NONE, verify_server_cb)
        serverctx.use_privatekey_file(os.path.join(configdir, 'server.pkey'))
        serverctx.use_certificate_file(os.path.join(configdir, 'server.cert'))
        serverctx.load_verify_locations(os.path.join(configdir, 'CA.cert'))
    return serverctx


def verify_client_cb(conn, cert, errnum, depth, ok):
    """
    Verify expiration of the given certificate.
    """
    expired = cert.has_expired()
    if expired:
        log.info(LOG_PROXY, "%s expired certificate %s", conn,
                    cert.get_subject())
    return not expired


clientctx = None
def get_clientctx(configdir):
    """
    Get SSL context for client.
    """
    global clientctx
    if clientctx is None:
        # construct client context
        clientctx = SSL.Context(SSL.SSLv23_METHOD)
        #clientctx = SSL.Context(SSL.TLSv1_METHOD)
        clientctx.set_verify(SSL.VERIFY_NONE, verify_client_cb)
        # activate all (safe) bug option workarounds; see also
        # http://www.openssl.org/docs/ssl/SSL_CTX_set_options.html
        clientctx.set_options(SSL.OP_ALL)
        clientctx.use_privatekey_file(os.path.join(configdir, 'client.pkey'))
        clientctx.use_certificate_file(os.path.join(configdir, 'client.cert'))
        clientctx.load_verify_locations(os.path.join(configdir, 'CA.cert'))
    return clientctx

def create_certificates(configdir):
    """
    Create certificates and private keys for WebCleaner.
    """
    cakey = create_key_pair(TYPE_RSA, 1024)
    careq = create_cert_request(cakey, CN='Certificate Authority')
    # five years
    cacert = create_certificate(careq, (careq, cakey), 0, (0, 60*60*24*365*5))
    # write files with appropriate umask
    oldmask = os.umask(0022)
    f = file(os.path.join(configdir, 'CA.pkey'), 'w')
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey))
    f.close()
    f = file(os.path.join(configdir, 'CA.cert'), 'w')
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cacert))
    f.close()
    for (fname, cname) in [('client', '%s Client' % AppName),
                           ('server', '%s Server' % AppName)]:
        pkey = create_key_pair(TYPE_RSA, 1024)
        req = create_cert_request(pkey, CN=cname)
        # five years
        cert = create_certificate(req, (cacert, cakey), 1, (0, 60*60*24*365*5))
        f = file(os.path.join(configdir, '%s.pkey' % fname), 'w')
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        f.close()
        f = file(os.path.join(configdir, '%s.cert' % fname), 'w')
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        f.close()
    # reset umask
    os.umask(oldmask)


#
# certgen.py
#
# Copyright (C) Martin Sj�gren and AB Strakt 2001, All rights reserved
#
# $Id$
#

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

def create_key_pair(ktype, bits):
    """
    Create a public/private key pair.

    @param ktype: Key type, must be one of TYPE_RSA and TYPE_DSA
    @param bits:  Number of bits to use in the key

    @return: The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(ktype, bits)
    return pkey


def create_cert_request(pkey, digest="md5", **name):
    """
    Create a certificate request.

    @param pkey: The key to associate with the request
    @param digest: Digestion method to use for signing, default is md5
    @param name: The name of the subject of the request

    @keyword C: Country name
    @keyword SP: State or province name
    @keyword L: Locality name
    @keyword O: Organization name
    @keyword OU: Organizational unit name
    @keyword CN: Common name
    @keyword email: E-mail address

    @return:   The certificate request in an X509Req object
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for key, value in name.iteritems():
        # Note: the CN name should be a multiple of 4 since the pyopenssl
        # wrapper has a bug treating some strings as UniversalString.
        # Workaround here is to fill the value up with spaces.
        if key == 'CN':
            tofill = 4 - (len(value) % 4)
            value += " "*tofill
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req


def create_certificate(req,(issuerCert, issuerKey), serial,
                       (notBefore, notAfter), digest="md5"):
    """
    Generate a certificate given a certificate request.

    @param req:        Certificate request to use
    @param issuerCert: The certificate of the issuer
    @param issuerKey:  The private key of the issuer
    @param serial:     Serial number for the certificate
    @param notBefore:  Timestamp (relative to now) when the certificate
                       starts being valid
    @param notAfter:   Timestamp (relative to now) when the certificate
                       stops being valid
    @param digest:     Digest method to use for signing, default is md5

    @return:  the signed certificate in an X509 object
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
