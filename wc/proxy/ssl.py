import os
from wc import ConfigDir
from OpenSSL import SSL
from wc.log import *


def verify_server_cb (conn, cert, errnum, depth, ok):
    # This obviously has to be updated
    debug(PROXY, 'Got client certificate: %s', cert.get_subject())
    return ok

# Initialize context
serverctx = SSL.Context(SSL.SSLv23_METHOD)
serverctx.set_options(SSL.OP_NO_SSLv2)
# Demand a certificate
#ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
serverctx.set_verify(SSL.VERIFY_PEER, verify_server_cb)
serverctx.use_privatekey_file (os.path.join(ConfigDir, 'server.pkey'))
serverctx.use_certificate_file(os.path.join(ConfigDir, 'server.cert'))
serverctx.load_verify_locations(os.path.join(ConfigDir, 'CA.cert'))


def verify_client_cb (conn, cert, errnum, depth, ok):
    # XXX this obviously has to be updated
    debug(PROXY, 'Got server certificate: %s' % cert.get_subject())
    return ok

# construct client context
clientctx = SSL.Context(SSL.SSLv23_METHOD)
clientctx.set_verify(SSL.VERIFY_PEER, verify_client_cb)
clientctx.use_privatekey_file (os.path.join(ConfigDir, 'client.pkey'))
clientctx.use_certificate_file(os.path.join(ConfigDir, 'client.cert'))
clientctx.load_verify_locations(os.path.join(ConfigDir, 'CA.cert'))


