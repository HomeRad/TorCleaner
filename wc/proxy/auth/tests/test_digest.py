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

import unittest
import tests
import wc.proxy.auth

class TestDigest (unittest.TestCase):
    """
    Test authentication routines.
    """

    def test_digest (self):
        """
        Construct and parse Digest authentication messages.
        """
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
