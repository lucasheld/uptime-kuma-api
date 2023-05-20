import unittest

from uptime_kuma_api import UptimeKumaException
from uptime_kuma_test_case import UptimeKumaTestCase


class TestMonitorTag(UptimeKumaTestCase):
    def test_monitor_tag(self):
        tag_id = self.add_tag()
        monitor_id = self.add_monitor()

        expected_monitor_tag = {
            "tag_id": tag_id,
            "monitor_id": monitor_id,
            "value": "value 1"
        }

        # add monitor tag
        r = self.api.add_monitor_tag(**expected_monitor_tag)
        self.assertEqual(r["msg"], "Added Successfully.")

        # check if tag is listed in monitor tags
        monitors = self.api.get_monitors()
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertEqual(monitor["tags"][0]["tag_id"], tag_id)

        # delete monitor tag
        r = self.api.delete_monitor_tag(**expected_monitor_tag)
        self.assertEqual(r["msg"], "Deleted Successfully.")

        # check if tag is not listed in monitor tags
        monitors = self.api.get_monitors()
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertEqual(monitor["tags"], [])

    def test_delete_not_existing_monitor_tag(self):
        with self.assertRaises(UptimeKumaException):
            self.api.delete_monitor_tag(42, 42, 42)


if __name__ == '__main__':
    unittest.main()
