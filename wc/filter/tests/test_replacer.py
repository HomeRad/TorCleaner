# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2006 Bastian Kleineidam
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
import random
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, STAGE_RESPONSE_MODIFY


class TestReplacer (unittest.TestCase):

    def init (self):
        super(TestReplacer, self).init()
        wc.configuration.init()
        wc.configuration.config['filters'] = ['Replacer']
        wc.configuration.config.init_filter_modules()

    def testReplaceRandom (self):
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY])
        # filter random data, should not raise any exception
        data = []
        for dummy in xrange(1024):
            data.append(chr(random.randint(0, 255)))
        data = "".join(data)
        applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)

    def testReplaceNonAscii (self):
        attrs = get_filterattrs("", "localhost", [STAGE_RESPONSE_MODIFY])
        data = "äöü asdfö"
        applyfilter(STAGE_RESPONSE_MODIFY, data, 'finish', attrs)


def test_suite ():
    return unittest.makeSuite(TestReplacer)


if __name__ == '__main__':
    unittest.main()
