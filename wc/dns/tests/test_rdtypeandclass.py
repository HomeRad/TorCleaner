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

import unittest

import wc.dns.rdataclass
import wc.dns.rdatatype

class TestRdTypeAndClass (unittest.TestCase):

    # Classes

    def test_class_meta1(self):
        self.assert_(wc.dns.rdataclass.is_metaclass(wc.dns.rdataclass.ANY))

    def test_class_meta2(self):
        self.assert_(not wc.dns.rdataclass.is_metaclass(wc.dns.rdataclass.IN))

    def test_class_bytext1(self):
        self.assertEqual(wc.dns.rdataclass.from_text('IN'),
                         wc.dns.rdataclass.IN)

    def test_class_bytext2(self):
        self.assertEqual(wc.dns.rdataclass.from_text('CLASS1'),
                         wc.dns.rdataclass.IN)

    def test_class_bytext_bounds1(self):
        self.assertEqual(wc.dns.rdataclass.from_text('CLASS0'), 0)
        self.assertEqual(wc.dns.rdataclass.from_text('CLASS65535'), 65535)

    def test_class_bytext_bounds2(self):
        def bad():
            junk = wc.dns.rdataclass.from_text('CLASS65536')
        self.assertRaises(ValueError, bad)

    def test_class_bytext_unknown(self):
        def bad():
            junk = wc.dns.rdataclass.from_text('XXX')
        self.assertRaises(wc.dns.rdataclass.UnknownRdataclass, bad)

    def test_class_totext1(self):
        self.assertEqual(wc.dns.rdataclass.to_text(wc.dns.rdataclass.IN),
                         'IN')

    def test_class_totext1(self):
        self.assertEqual(wc.dns.rdataclass.to_text(999), 'CLASS999')

    def test_class_totext_bounds1(self):
        def bad():
            junk = wc.dns.rdataclass.to_text(-1)
        self.assertRaises(ValueError, bad)

    def test_class_totext_bounds2(self):
        def bad():
            junk = wc.dns.rdataclass.to_text(65536)
        self.assertRaises(ValueError, bad)

    # Types

    def test_type_meta1(self):
        self.assert_(wc.dns.rdatatype.is_metatype(wc.dns.rdatatype.ANY))

    def test_type_meta2(self):
        self.assert_(wc.dns.rdatatype.is_metatype(wc.dns.rdatatype.OPT))

    def test_type_meta3(self):
        self.assert_(not wc.dns.rdatatype.is_metatype(wc.dns.rdatatype.A))

    def test_type_singleton1(self):
        self.assert_(wc.dns.rdatatype.is_singleton(wc.dns.rdatatype.SOA))

    def test_type_singleton2(self):
        self.assert_(not wc.dns.rdatatype.is_singleton(wc.dns.rdatatype.A))

    def test_type_bytext1(self):
        self.assertEqual(wc.dns.rdatatype.from_text('A'), wc.dns.rdatatype.A)

    def test_type_bytext2(self):
        self.assertEqual(wc.dns.rdatatype.from_text('TYPE1'),
                         wc.dns.rdatatype.A)

    def test_type_bytext_bounds1(self):
        self.assertEqual(wc.dns.rdatatype.from_text('TYPE0'), 0)
        self.assertEqual(wc.dns.rdatatype.from_text('TYPE65535'), 65535)

    def test_type_bytext_bounds2(self):
        def bad():
            junk = wc.dns.rdatatype.from_text('TYPE65536')
        self.assertRaises(ValueError, bad)

    def test_type_bytext_unknown(self):
        def bad():
            junk = wc.dns.rdatatype.from_text('XXX')
        self.assertRaises(wc.dns.rdatatype.UnknownRdatatype, bad)

    def test_type_totext1(self):
        self.assertEqual(wc.dns.rdatatype.to_text(wc.dns.rdatatype.A), 'A')

    def test_type_totext1(self):
        self.assertEqual(wc.dns.rdatatype.to_text(999), 'TYPE999')

    def test_type_totext_bounds1(self):
        def bad():
            junk = wc.dns.rdatatype.to_text(-1)
        self.assertRaises(ValueError, bad)

    def test_type_totext_bounds2(self):
        def bad():
            junk = wc.dns.rdatatype.to_text(65536)
        self.assertRaises(ValueError, bad)


def test_suite ():
    return unittest.makeSuite(TestRdTypeAndClass)


if __name__ == '__main__':
    unittest.main()
