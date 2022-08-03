import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestInfo(UptimeKumaTestCase):
    def test_info(self):
        info = self.api.info()
        self.assertIn("version", info)
        self.assertIn("latestVersion", info)


if __name__ == '__main__':
    unittest.main()
