# -*- coding: iso-8859-1 -*-
import unittest
import wc.proxy.auth

class TestDigest (unittest.TestCase):
    """Test authentication routines"""

    def test_digest (self):
        """construct and parse Digest authentication messages"""
        chal = 'Digest realm="This is my digest auth", nonce="i5tbP9h2RAiGbccW", qop="auth", stale=false'
        chals = wc.proxy.auth.parse_challenges(chal)
        attrs = {"username": "calvin", "password_b64": "Y2Fsdmlu",
                 "uri": "/logo.gif", "method": "GET",
                 "requireExtraQuotes": False}
        creds = wc.proxy.auth.parse_credentials(wc.proxy.auth.get_credentials(chals, **attrs))
        #wccreds = creds['Digest'][0]
        # XXX test this data


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDigest))
    return suite


if __name__ == '__main__':
    unittest.main()
