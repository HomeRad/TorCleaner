# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Test script to test filtering.
"""

import unittest
import tests
import wc
import wc.configuration
import wc.proxy.Headers
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY


class TestBinaryCharFilter (tests.StandardTest):
    """
    All these tests work with a _default_ filter configuration.
    If you change any of the *.zap filter configs, tests can fail...
    """

    def setUp (self):
        wc.configuration.init()
        wc.configuration.config['filters'] = ['BinaryCharFilter']
        wc.configuration.config.init_filter_modules()

    def filt (self, data, result):
        headers = wc.http.header.WcMessage()
        headers['Content-Type'] = "text/html"
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY],
                                serverheaders=headers, headers=headers)
        filtered = applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)
        self.assertEqual(filtered, result)

    def test_quotes (self):
        self.filt("""These \x84Microsoft\x93 \x94chars\x94 are history.""",
                  """These "Microsoft" "chars" are history.""")
        self.filt("""\x91Retter\x92 Majak trifft in der Schlussminute.""",
                  """`Retter' Majak trifft in der Schlussminute.""")

    def test_null (self):
        self.filt("\x00", " ")


def test_suite ():
    return unittest.makeSuite(TestBinaryCharFilter)


if __name__ == '__main__':
    unittest.main()
