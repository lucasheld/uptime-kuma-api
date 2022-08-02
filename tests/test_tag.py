import unittest
from uptime_kuma_test_case import UptimeKumaTestCase
from uptime_kuma_api import UptimeKumaException


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

        # delete tag
        r = self.api.delete_tag(tag_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        print(r)
        with self.assertRaises(UptimeKumaException):
            self.api.get_proxy(tag_id)


if __name__ == '__main__':
    unittest.main()
