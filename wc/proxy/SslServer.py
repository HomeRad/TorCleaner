# -*- coding: iso-8859-1 -*-
"""connection handling WebCleaner SSL server <--> Remote SSL server"""

from wc.log import *
from HttpsServer import HttpsServer


class SslServer (HttpsServer):
    """XXX """
    def __repr__ (self):
        """object description"""
        if self.addr[1] != 80:
	    portstr = ':%d' % self.addr[1]
        else:
            portstr = ''
        extra = '%s%s' % (self.addr[0], portstr)
        if self.socket:
            extra += " (%s)"%self.socket.state_string()
        #if len(extra) > 46: extra = extra[:43] + '...'
        return '<%s:%-8s %s>' % ('sslserver', self.state, extra)

