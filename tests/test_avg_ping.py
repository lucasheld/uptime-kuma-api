import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestAvgPing(UptimeKumaTestCase):
    def test_avg_ping(self):
        self.add_monitor()
        self.api.avg_ping()


if __name__ == '__main__':
    unittest.main()
