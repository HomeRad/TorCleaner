# -*- coding: iso-8859-1 -*-
import unittest
import wc.proxy.UnchunkStream


class TestUnchunk (unittest.TestCase):

    def testUnchunk (self):
        unchunker = wc.proxy.UnchunkStream.UnchunkStream()
        data = "a"*0x30
        s = "000000000030\r\n%s\r\n0\r\n\r\n" % data
        self.assertEqual(data, unchunker.decode(s))


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUnchunk))
    return suite

if __name__ == '__main__':
    unittest.main()
