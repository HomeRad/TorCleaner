# -*- coding: iso-8859-1 -*-
import unittest
import base64
import wc
import wc.proxy.auth


class TestNtlm (unittest.TestCase):
    """Test ntlm authentication routines"""

    def test_ntlm (self):
        """construct and parse NTLM authentication messages"""
        wc.config['auth_ntlm'] = 1
        # challenge type 0
        challenges = wc.proxy.auth.get_challenges(type=wc.proxy.auth.ntlm.NTLMSSP_INIT)
        challenges = wc.proxy.auth.parse_challenges(", ".join(challenges))
        self.assertEqual(challenges['NTLM'][0]['type'], 0)
        # credentials type 1
        attrs = {"username": "calvin", "type": wc.proxy.auth.ntlm.NTLMSSP_NEGOTIATE,}
        creds = wc.proxy.auth.get_credentials(challenges, **attrs)
        creds = wc.proxy.auth.parse_credentials(creds)
        self.assertEqual(creds['NTLM'][0]['type'], 1)
        # challenges type 2
        attrs['host'] = creds['NTLM'][0]['host']
        attrs['domain'] = creds['NTLM'][0]['domain']
        attrs['type'] = wc.proxy.auth.ntlm.NTLMSSP_CHALLENGE
        challenges = wc.proxy.auth.get_challenges(**attrs)
        challenges = wc.proxy.auth.parse_challenges(", ".join(challenges))
        self.assertEqual(challenges['NTLM'][0]['type'], 2)
        # credentials type 3
        attrs['type'] = wc.proxy.auth.ntlm.NTLMSSP_AUTH
        attrs['nonce'] = challenges['NTLM'][0]['nonce']
        attrs['password_b64'] = base64.encodestring("Beeblebrox")
        creds = wc.proxy.auth.get_credentials(challenges, **attrs)
        creds = wc.proxy.auth.parse_credentials(creds)
        self.assertEqual(creds['NTLM'][0]['type'], 3)
        self.assertEqual(creds['NTLM'][0]['username'], 'calvin')
        self.assert_(wc.proxy.auth.check_credentials(creds, **attrs))
        wc.config['auth_ntlm'] = 0

    def test_ntlmpass (self):
        """construct NTLM hashed password responses"""
        password = "Beeblebrox"
        nonce = "SrvNonce"
        lm_hashed_pw = wc.proxy.auth.ntlm.create_lm_hashed_password(password)
        nt_hashed_pw = wc.proxy.auth.ntlm.create_nt_hashed_password(password)
        correct_lm_resp = "\xad\x87\xca\x6d\xef\xe3\x46\x85\xb9\xc4\x3c\x47\x7a\x8c\x42\xd6\x00\x66\x7d\x68\x92\xe7\xe8\x97"
        correct_nt_resp = "\xe0\xe0\x0d\xe3\x10\x4a\x1b\xf2\x05\x3f\x07\xc7\xdd\xa8\x2d\x3c\x48\x9a\xe9\x89\xe1\xb0\x00\xd3"
        lm_resp = wc.proxy.auth.ntlm.calc_resp(lm_hashed_pw, nonce)
        nt_resp = wc.proxy.auth.ntlm.calc_resp(nt_hashed_pw, nonce)
        self.assertEqual(correct_lm_resp, lm_resp)
        self.assertEqual(correct_nt_resp, nt_resp)


def test_suite ():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNtlm))
    return suite

if __name__ == '__main__':
    unittest.main()
