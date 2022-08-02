import unittest
from uptime_kuma_test_case import UptimeKumaTestCase
from uptime_kuma_api import UptimeKumaException


class TestMonitor(UptimeKumaTestCase):
    def test_monitor(self):
        expected_monitor = {
            "type_": "http",
            "name": "monitor 1",
            "url": "http://192.168.20.135"
        }

        # add monitor
        r = self.api.add_monitor(
            type_=expected_monitor["type_"],
            name=expected_monitor["name"],
            url=expected_monitor["url"]
        )
        self.assertEqual(r["msg"], "Added Successfully.")
        monitor_id = r["monitor_id"]

        # get monitor
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # get monitors
        monitors = self.api.get_monitors()
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertIsNotNone(monitor)
        self.compare(monitor, expected_monitor)

        # edit monitor
        expected_monitor["type_"] = "ping"
        expected_monitor["name"] = "monitor 1 new"
        expected_monitor["hostname"] = "127.0.0.1"
        del expected_monitor["url"]
        r = self.api.edit_monitor(monitor_id, **expected_monitor)
        self.assertEqual(r["msg"], "Saved.")
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # pause monitor
        r = self.api.pause_monitor(monitor_id)
        self.assertEqual(r["msg"], "Paused Successfully.")

        # resume monitor
        r = self.api.resume_monitor(monitor_id)
        self.assertEqual(r["msg"], "Resumed Successfully.")

        # delete monitor
        r = self.api.delete_monitor(monitor_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_monitor(monitor_id)


if __name__ == '__main__':
    unittest.main()
