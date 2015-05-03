# -*- coding: iso-8859-1 -*-
# Copyright (C) 2006-2010 Bastian Kleineidam

import unittest
import wc.http.header


class TestHeader(unittest.TestCase):

    def test_add(self):
        d = wc.http.header.WcMessage()
        d['Via'] = 'foo\r'
        self.assertTrue('via' in d)
