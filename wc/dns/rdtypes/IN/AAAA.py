# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003, 2004 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import wc.dns.exception
import wc.dns.inet
import wc.dns.rdata
import wc.dns.tokenizer

class AAAA(wc.dns.rdata.Rdata):
    """AAAA record.

    @ivar address: an IPv6 address
    @type address: string (in the standard IPv6 format)"""

    __slots__ = ['address']

    def __init__(self, rdclass, rdtype, address):
        super(AAAA, self).__init__(rdclass, rdtype)
        # check that it's OK
        junk = wc.dns.inet.inet_pton(wc.dns.inet.AF_INET6, address)
        self.address = address

    def to_text(self, origin=None, relativize=True, **kw):
        return self.address

    def from_text(cls, rdclass, rdtype, tok, origin = None, relativize = True):
        (ttype, address) = tok.get()
        if ttype != wc.dns.tokenizer.IDENTIFIER:
            raise wc.dns.exception.SyntaxError
        t = tok.get_eol()
        return cls(rdclass, rdtype, address)

    from_text = classmethod(from_text)

    def to_wire(self, file, compress = None, origin = None):
        file.write(wc.dns.inet.inet_pton(wc.dns.inet.AF_INET6, self.address))

    def from_wire(cls, rdclass, rdtype, wire, current, rdlen, origin = None):
        address = wc.dns.inet.inet_ntop(wc.dns.inet.AF_INET6,
                                     wire[current : current + rdlen])
        return cls(rdclass, rdtype, address)

    from_wire = classmethod(from_wire)

    def _cmp(self, other):
        sa = wc.dns.inet.inet_pton(wc.dns.inet.AF_INET6, self.address)
        oa = wc.dns.inet.inet_pton(wc.dns.inet.AF_INET6, other.address)
        return cmp(sa, oa)