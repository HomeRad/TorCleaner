# -*- coding: iso-8859-1 -*-
import unittest
import wc.proxy.UnchunkStream
import StandardTest


class TestUnchunk (StandardTest.StandardTest):

    def testUnchunk (self):
        unchunker = wc.proxy.UnchunkStream.UnchunkStream()
        data = "a"*0x30
        s = "000000000030\r\n%s\r\n0\r\n\r\n" % data
        self.assertEqual(data, unchunker.decode(s))


if __name__ == '__main__':
    unittest.main(defaultTest='TestUnchunk')
else:
    suite = unittest.makeSuite(TestUnchunk, 'test')
