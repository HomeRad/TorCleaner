# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006 Bastian Kleineidam
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
import unittest
import wc
import wc.configuration.ratingstorage

class TestRating (unittest.TestCase):

    def test_split_url (self):
        """Test url splitting."""
        urls = (
            ('', []),
            ('a', []),
            ('a/b', []),
            ('http://imadoofus.com', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com//', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/?q=a', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/?q=a#a', ['http://', 'imadoofus.com', '/']),
            ('http://imadoofus.com/a/b//c', ['http://', 'imadoofus.com', '/', 'a', '/', 'b', '/', 'c']),
            ('http://imadoofus.com/forum', ['http://', 'imadoofus.com', '/', 'forum']),
            ('http://imadoofus.com/forum/', ['http://', 'imadoofus.com', '/', 'forum']),
        )
        split_url = wc.configuration.ratingstorage.split_url
        for url, res in urls:
            self.assertEqual(split_url(url), res)

def test_suite ():
    return unittest.makeSuite(TestRating)


if __name__ == '__main__':
    unittest.main()
