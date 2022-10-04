import unittest

from uptime_kuma_api import UptimeKumaException, ProxyProtocol
from uptime_kuma_test_case import UptimeKumaTestCase


class TestProxy(UptimeKumaTestCase):
    def test_proxy(self):
        # get empty list to make sure that future accesses will also work
        self.api.get_proxies()

        expected_proxy = {
            "protocol": ProxyProtocol.HTTP,
            "host": "127.0.0.1",
            "port": 8080,
            "auth": True,
            "username": "username",
            "password": "password",
            "active": True,
            "default": False
        }

        # add proxy
        r = self.api.add_proxy(applyExisting=False, **expected_proxy)
        self.assertEqual(r["msg"], "Saved")
        proxy_id = r["id"]

        # get proxy
        proxy = self.api.get_proxy(proxy_id)
        self.compare(proxy, expected_proxy)

        # get proxies
        proxies = self.api.get_proxies()
        proxy = self.find_by_id(proxies, proxy_id)
        self.assertIsNotNone(proxy)
        self.compare(proxy, expected_proxy)

        # edit proxy
        expected_proxy["protocol"] = ProxyProtocol.HTTPS
        expected_proxy["host"] = "127.0.0.2"
        expected_proxy["port"] = 8888
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
