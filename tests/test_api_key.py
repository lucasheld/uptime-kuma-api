import unittest

from uptime_kuma_api import UptimeKumaException
from uptime_kuma_test_case import UptimeKumaTestCase


class TestApiKey(UptimeKumaTestCase):
    def test_api_key(self):
        # get empty list to make sure that future accesses will also work
        self.api.get_api_keys()

        expected = {
            "name": "name 1",
            "expires": "2023-03-30 12:20:00",
            "active": True
        }

        # add api key
        r = self.api.add_api_key(**expected)
        self.assertEqual(r["msg"], "Added Successfully.")
        api_key_id = r["keyID"]

        # get api key
        api_key = self.api.get_api_key(api_key_id)
        self.compare(api_key, expected)

        # get api keys
        api_keys = self.api.get_api_keys()
        api_key = self.find_by_id(api_keys, api_key_id)
        self.assertIsNotNone(api_key)
        self.compare(api_key, expected)

        # disable api key
        r = self.api.disable_api_key(api_key_id)
        self.assertEqual(r["msg"], "Disabled Successfully.")
        api_key = self.api.get_api_key(api_key_id)
        expected["active"] = False
        self.compare(api_key, expected)

        # enable api key
        r = self.api.enable_api_key(api_key_id)
        self.assertEqual(r["msg"], "Enabled Successfully")
        api_key = self.api.get_api_key(api_key_id)
        expected["active"] = True
        self.compare(api_key, expected)

        # delete api key
        r = self.api.delete_api_key(api_key_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_api_key(api_key_id)


if __name__ == '__main__':
    unittest.main()
