import unittest
from urllib import parse

import pyotp

from uptime_kuma_test_case import UptimeKumaTestCase


def parse_secret(uri):
    query = parse.urlsplit(uri).query
    params = dict(parse.parse_qsl(query))
    return params["secret"]


def generate_token(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()


class Test2FA(UptimeKumaTestCase):
    def test_2fa(self):
        # check 2fa is disabled
        r = self.api.twofa_status()
        self.assertEqual(r["status"], False)

        # prepare 2fa
        r = self.api.prepare_2fa(self.password)
        uri = r["uri"]
        self.assertTrue(uri.startswith("otpauth://totp/"))
        secret = parse_secret(uri)

        # verify token
        token = generate_token(secret)
        r = self.api.verify_token(token, self.password)
        self.assertEqual(r["valid"], True)

        # save 2fa
        r = self.api.save_2fa(self.password)
        self.assertEqual(r["msg"], "2FA Enabled.")

        # check 2fa is enabled
        r = self.api.twofa_status()
        self.assertEqual(r["status"], True)

        # relogin using the totp token
        self.api.logout()
        token = generate_token(secret)
        self.api.login(self.username, self.password, token)

        # disable 2fa
        r = self.api.disable_2fa(self.password)
        self.assertEqual(r["msg"], "2FA Disabled.")


if __name__ == '__main__':
    unittest.main()
