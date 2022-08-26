import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestUptime(UptimeKumaTestCase):
    def test_uptime_without_monitor(self):
        self.api.uptime()

    def test_uptime_with_monitor(self):
        self.add_monitor()
        self.api.uptime()


if __name__ == '__main__':
    unittest.main()
