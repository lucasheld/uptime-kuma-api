import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestClear(UptimeKumaTestCase):
    def test_clear_events(self):
        monitor_id = self.add_monitor()
        self.api.clear_events(monitor_id)

    def test_clear_heartbeats(self):
        monitor_id = self.add_monitor()
        self.api.clear_heartbeats(monitor_id)

    def test_clear_statistics(self):
        self.api.clear_statistics()


if __name__ == '__main__':
    unittest.main()
