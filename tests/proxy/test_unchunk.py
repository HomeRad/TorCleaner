# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005-2009 Bastian Kleineidam
import unittest
import wc.proxy.decoder.UnchunkStream
import wc.dummy


class TestUnchunk(unittest.TestCase):

    def testUnchunk(self):
        dummy = wc.dummy.Dummy()
        unchunker = wc.proxy.decoder.UnchunkStream.UnchunkStream(dummy)
        data = "a"*0x30
        s = "000000000030\r\n%s\r\n0\r\n\r\n" % data
        self.assertEqual(data, unchunker.process(s))
