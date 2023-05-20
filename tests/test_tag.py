import unittest

from uptime_kuma_api import UptimeKumaException
from uptime_kuma_test_case import UptimeKumaTestCase


class TestTag(UptimeKumaTestCase):
    def test_tag(self):
        expected_tag = {
            "name": "tag 1",
            "color": "#ffffff"
        }

        # add tag
        tag = self.api.add_tag(**expected_tag)
        self.compare(tag, expected_tag)
        tag_id = tag["id"]

        # get tag
        tag = self.api.get_tag(tag_id)
        self.compare(tag, expected_tag)

        # get tags
        tags = self.api.get_tags()
        tag = self.find_by_id(tags, tag_id)
        self.assertIsNotNone(tag)
        self.compare(tag, expected_tag)

        # edit tag
        expected_tag["name"] = "tag 1 new"
        expected_tag["color"] = "#000000"
        r = self.api.edit_tag(tag_id, **expected_tag)
        self.assertEqual(r["msg"], "Saved")
        tag = self.api.get_tag(tag_id)
        self.compare(tag, expected_tag)

        # delete tag
        r = self.api.delete_tag(tag_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_tag(tag_id)


if __name__ == '__main__':
    unittest.main()
