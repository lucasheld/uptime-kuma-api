import unittest

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

        # delete monitor tag
        r = self.api.delete_monitor_tag(**expected_monitor_tag)
        self.assertEqual(r["msg"], "Deleted Successfully.")


if __name__ == '__main__':
    unittest.main()
