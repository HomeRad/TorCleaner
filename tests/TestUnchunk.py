# -*- coding: iso-8859-1 -*-
import unittest
from wc.proxy.UnchunkStream import UnchunkStream
from tests.StandardTest import StandardTest


class TestUnchunk (StandardTest):

    def testUnchunk (self):
        unchunker = UnchunkStream()
        data = "a"*0x30
        s = "000000000030\r\n%s\r\n0\r\n\r\n" % data
        self.assertEqual(data, unchunker.decode(s))


if __name__ == '__main__':
    unittest.main(defaultTest='TestUnchunk')
else:
    suite = unittest.makeSuite(TestUnchunk, 'test')
