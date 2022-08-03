import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestHeartbeat(UptimeKumaTestCase):
    def test_get_heartbeats(self):
        self.api.get_heartbeats()

    def test_get_important_heartbeats(self):
        self.api.get_important_heartbeats()


if __name__ == '__main__':
    unittest.main()
