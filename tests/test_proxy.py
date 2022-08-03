import unittest

from uptime_kuma_api import UptimeKumaException
from uptime_kuma_test_case import UptimeKumaTestCase


class TestProxy(UptimeKumaTestCase):
    def test_proxy(self):
        expected_proxy = {
            "protocol": "http",
            "host": "127.0.0.1",
            "port": 8080,
            "active": True
        }

        # add proxy
        r = self.api.add_proxy(**expected_proxy)
        self.assertEqual(r["msg"], "Saved")
        proxy_id = r["id"]

        # get proxy
        proxy = self.api.get_proxy(proxy_id)
        self.compare(proxy, expected_proxy)

        # edit proxy
        expected_proxy["protocol"] = "https"
        expected_proxy["host"] = "127.0.0.2"
        expected_proxy["port"] = 8888
        expected_proxy["active"] = False
        r = self.api.edit_proxy(proxy_id, **expected_proxy)
        self.assertEqual(r["msg"], "Saved")
        proxy = self.api.get_proxy(proxy_id)
        self.compare(proxy, expected_proxy)

        # delete proxy
        r = self.api.delete_proxy(proxy_id)
        self.assertEqual(r["msg"], "Deleted")
        with self.assertRaises(UptimeKumaException):
            self.api.get_proxy(proxy_id)


if __name__ == '__main__':
    unittest.main()
