import unittest

from uptime_kuma_api import UptimeKumaApi
from uptime_kuma_test_case import UptimeKumaTestCase


class TestLogin(UptimeKumaTestCase):
    def test_auto_login(self):
        # disable auth
        r = self.api.set_settings(self.password, disableAuth=True)
        self.assertEqual(r["msg"], "Saved")

        # login again without username and password
        self.api.logout()
        self.api.disconnect()
        self.api = UptimeKumaApi(self.url)
        self.api.login()

        r = self.api.get_settings()
        self.assertTrue(r["disableAuth"])

        # enable auth again
        r = self.api.set_settings(disableAuth=False)
        self.assertEqual(r["msg"], "Saved")

        r = self.api.get_settings()
        self.assertFalse(r["disableAuth"])


if __name__ == '__main__':
    unittest.main()
