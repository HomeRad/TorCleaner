# -*- coding: iso-8859-1 -*-
# Copyright (C) 2003-2007 Nominum, Inc.
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

import unittest

import wc.dns.flags
import wc.dns.rcode
import wc.dns.opcode

class TestFlags (unittest.TestCase):

    def test_rcode1(self):
        self.assertEqual(wc.dns.rcode.from_text('FORMERR'),
                         wc.dns.rcode.FORMERR)

    def test_rcode2(self):
        self.assertEqual(wc.dns.rcode.to_text(wc.dns.rcode.FORMERR),
                         "FORMERR")

    def test_rcode3(self):
        self.assertEqual(wc.dns.rcode.to_flags(wc.dns.rcode.FORMERR), (1, 0))

    def test_rcode4(self):
        self.assertEqual(wc.dns.rcode.to_flags(wc.dns.rcode.BADVERS),
                         (0, 0x01000000))

    def test_rcode5(self):
        self.assertEqual(wc.dns.rcode.from_flags(0, 0x01000000),
                         wc.dns.rcode.BADVERS)

    def test_rcode6(self):
        self.assertEqual(wc.dns.rcode.from_flags(5, 0), wc.dns.rcode.REFUSED)

    def test_rcode7(self):
        def bad():
            wc.dns.rcode.to_flags(4096)
        self.assertRaises(ValueError, bad)

    def test_flags1(self):
        self.assertEqual(wc.dns.flags.from_text("RA RD AA QR"),
              wc.dns.flags.QR|wc.dns.flags.AA|wc.dns.flags.RD|wc.dns.flags.RA)

    def test_flags2(self):
        flgs = wc.dns.flags.QR|wc.dns.flags.AA|wc.dns.flags.RD|wc.dns.flags.RA
        self.assertEqual(wc.dns.flags.to_text(flgs), "QR AA RD RA")
