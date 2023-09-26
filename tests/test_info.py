import unittest

from uptime_kuma_api import UptimeKumaApi
from uptime_kuma_test_case import UptimeKumaTestCase


class TestInfo(UptimeKumaTestCase):
    def test_info(self):
        info = self.api.info()
        self.assertIn("version", info)
        self.assertIn("latestVersion", info)

    def test_info_with_version(self):
        # If wait_events is set to 0, the first info event is normally used.
        # The info event handler needs to drop this first event without a version.
        self.api.logout()
        self.api.disconnect()
        self.api = UptimeKumaApi(self.url, wait_events=0)
        self.api.login(self.username, self.password)
        info = self.api.info()
        self.assertIn("version", info)


if __name__ == '__main__':
    unittest.main()
