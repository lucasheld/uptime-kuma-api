import unittest

from uptime_kuma_api import UptimeKumaApi


token = None


class UptimeKumaTestCase(unittest.TestCase):
    api = None
    url = "http://127.0.0.1:3001"
    username = "admin"
    password = "secret123"

    @classmethod
    def setUpClass(cls):
        cls.api = UptimeKumaApi(cls.url)

        global token
        if not token:
            if cls.api.need_setup():
                cls.api.setup(cls.username, cls.password)
            r = cls.api.login(cls.username, cls.password)
            token = r["token"]

        cls.api.login_by_token(token)

    @classmethod
    def tearDownClass(cls):
        cls.api.disconnect()

    def compare(self, superset, subset):
        self.assertTrue(subset.items() <= superset.items())

    def find_by_id(self, objects, value, key="id"):
        for obj in objects:
            if obj[key] == value:
                return obj

    def add_monitor(self):
        r = self.api.add_monitor(type="http", name="monitor 1", url="http://127.0.0.1")
        monitor_id = r["monitorID"]
        return monitor_id

    def add_tag(self):
        r = self.api.add_tag(name="tag 1", color="#ffffff")
        tag_id = r["id"]
        return tag_id
