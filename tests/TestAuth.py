# -*- coding: iso-8859-1 -*-
import unittest, base64
from wc.proxy import auth


class TestAuth (unittest.TestCase):
    """Test authentication routines"""


    def _testDigest (self):
        chal = 'Digest realm="This is my digest auth", nonce="i5tbP9h2RAiGbccW", qop="auth", stale=false'
        chals = auth.parse_challenges(chal)
        attrs = {"username": "calvin", "password_b64": "Y2Fsdmlu",
                 "uri": "/logo.gif", "method": "GET",
                 "requireExtraQuotes": False}
        # test credentials recorded from mozilla session
        mozcreds = {"username":"calvin",  "realm":"This is my digest auth",
                "nonce":"i5tbP9h2RAiGbccW", "uri":"/logo.gif",
                "response":"73b8f33cd4ef569ec05dca533209a647",
                "qop":"auth", "nc":"00000001", "cnonce":"5993211954416e83"}
        creds = auth.parse_credentials(auth.get_credentials(chals, **attrs))
        wccreds = creds['Digest'][0]
        for key, item in mozcreds.items():
            self.assert_(key in wccreds)
            self.assertEqual(item, wccreds[key], "key %s: %s != %s"%(key, item, wccreds[key]))


    def testNtlm (self):
        auth.config['auth_ntlm'] = 1
        # challenge type 0
        challenges = auth.get_challenges(type=auth.ntlm.NTLMSSP_INIT)
        challenges = auth.parse_challenges(", ".join(challenges))
        self.assertEqual(challenges['NTLM'][0]['type'], 0)

        # credentials type 1
        attrs = {"username": "calvin", "type": auth.ntlm.NTLMSSP_NEGOTIATE,}
        creds = auth.get_credentials(challenges, **attrs)
        creds = auth.parse_credentials(creds)
        self.assertEqual(creds['NTLM'][0]['type'], 1)

        # challenges type 2
        attrs['host'] = creds['NTLM'][0]['host']
        attrs['domain'] = creds['NTLM'][0]['domain']
        attrs['type'] = auth.ntlm.NTLMSSP_CHALLENGE
        challenges = auth.get_challenges(**attrs)
        challenges = auth.parse_challenges(", ".join(challenges))
        self.assertEqual(challenges['NTLM'][0]['type'], 2)

        # credentials type 3
        attrs['type'] = auth.ntlm.NTLMSSP_AUTH
        attrs['nonce'] = challenges['NTLM'][0]['nonce']
        attrs['password_b64'] = base64.encodestring("Beeblebrox")
        creds = auth.get_credentials(challenges, **attrs)
        creds = auth.parse_credentials(creds)
        self.assertEqual(creds['NTLM'][0]['type'], 3)
        self.assertEqual(creds['NTLM'][0]['username'], 'calvin')
        self.assert_(auth.check_credentials(creds, **attrs))
        auth.config['auth_ntlm'] = 0


    def testNtlm2 (self):
        password = "Beeblebrox"
        nonce = "SrvNonce"
        lm_hashed_pw = auth.ntlm.create_lm_hashed_password(password)
        nt_hashed_pw = auth.ntlm.create_nt_hashed_password(password)
        correct_lm_resp = "\xad\x87\xca\x6d\xef\xe3\x46\x85\xb9\xc4\x3c\x47\x7a\x8c\x42\xd6\x00\x66\x7d\x68\x92\xe7\xe8\x97"
        correct_nt_resp = "\xe0\xe0\x0d\xe3\x10\x4a\x1b\xf2\x05\x3f\x07\xc7\xdd\xa8\x2d\x3c\x48\x9a\xe9\x89\xe1\xb0\x00\xd3"
        lm_resp = auth.ntlm.calc_resp(lm_hashed_pw, nonce)
        nt_resp = auth.ntlm.calc_resp(nt_hashed_pw, nonce)
        self.assertEqual(correct_lm_resp, lm_resp)
        self.assertEqual(correct_nt_resp, nt_resp)

suite = unittest.makeSuite(TestAuth,'test')

if __name__ == '__main__':
    unittest.main()
