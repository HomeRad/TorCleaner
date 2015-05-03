# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2009 Bastian Kleineidam
import unittest
import wc.configuration.ratingstorage


class TestRating(unittest.TestCase):

    def test_split_url(self):
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
