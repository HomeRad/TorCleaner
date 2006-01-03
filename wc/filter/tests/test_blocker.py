#!/usr/bin/python
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
# -*- coding: iso-8859-1 -*-
"""
Test script to test filtering.
"""

import unittest
import tests
import wc
import wc.configuration
from wc.filter import applyfilter, get_filterattrs, STAGE_REQUEST


class TestBlocker (tests.StandardTest):

    def setUp (self):
        self.url = "http://ads.realmedia.com/"
        wc.configuration.init()
        wc.configuration.config['filters'] = ['Blocker',]
        wc.configuration.config.init_filter_modules()

    def test_block (self):
        data = "GET %s HTTP/1.0" % self.url
        attrs = get_filterattrs(self.url, "localhost", [STAGE_REQUEST])
        filtered = applyfilter(STAGE_REQUEST, data, 'finish', attrs)
        self.assert_(filtered.find("blocked.html")!=-1)


def test_suite ():
    return unittest.makeSuite(TestBlocker)


if __name__ == '__main__':
    unittest.main()
