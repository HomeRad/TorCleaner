import os
from wc import ConfigDir, AppName
from OpenSSL import SSL, crypto
from certgen import createKeyPair, createCertRequest, createCertificate
from certgen import TYPE_RSA
from wc.log import *


def absfile (fname):
    """return absolute filename for certificate files"""
    return os.path.join(ConfigDir, fname)


def verify_server_cb (conn, cert, errnum, depth, ok):
    # This obviously has to be updated
    debug(PROXY, '%s (%s) got client certificate %s', conn, ok, cert.get_subject())
    return 1

# Initialize context
serverctx = SSL.Context(SSL.SSLv23_METHOD)
#serverctx.set_options(SSL.OP_NO_SSLv2)
# Demand a certificate
#ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
serverctx.set_verify(SSL.VERIFY_NONE, verify_server_cb)
serverctx.use_privatekey_file(absfile('server.pkey'))
serverctx.use_certificate_file(absfile('server.cert'))
serverctx.load_verify_locations(absfile('CA.cert'))


def verify_client_cb (conn, cert, errnum, depth, ok):
    # XXX this obviously has to be updated
    debug(PROXY, '%s (%s) got server certificate %s', conn, ok, cert.get_subject())
    return 1

# construct client context
clientctx = SSL.Context(SSL.SSLv23_METHOD)
clientctx.set_verify(SSL.VERIFY_NONE, verify_client_cb)
clientctx.use_privatekey_file(absfile('client.pkey'))
clientctx.use_certificate_file(absfile('client.cert'))
clientctx.load_verify_locations(absfile('CA.cert'))


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

