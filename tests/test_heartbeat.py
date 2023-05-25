import unittest

from uptime_kuma_api import MonitorStatus
from uptime_kuma_test_case import UptimeKumaTestCase


class TestHeartbeat(UptimeKumaTestCase):
    def test_get_heartbeats(self):
        self.add_monitor()
        r = self.api.get_heartbeats()
        self.assertTrue(type(list(r.values())[0][0]["status"]) == MonitorStatus)

    def test_get_important_heartbeats(self):
        self.add_monitor()
        r = self.api.get_important_heartbeats()
        self.assertTrue(type(list(r.values())[0][0]["status"]) == MonitorStatus)


if __name__ == '__main__':
    unittest.main()
