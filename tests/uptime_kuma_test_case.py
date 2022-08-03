import unittest

from uptime_kuma_api import UptimeKumaApi


class UptimeKumaTestCase(unittest.TestCase):
    api = None
    password = "zS7zhQSc"

    @classmethod
    def setUpClass(cls):
        cls.api = UptimeKumaApi("http://127.0.0.1:3001")
        username = "testuser"
        if cls.api.need_setup():
            cls.api.setup(username, cls.password)
        cls.api.login(username, cls.password)

    @classmethod
    def tearDownClass(cls):
        cls.api.logout()
        cls.api.disconnect()

    def compare(self, superset, subset):
        return subset.items() <= superset.items()

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
