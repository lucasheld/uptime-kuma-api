import unittest
from uptime_kuma_api import UptimeKumaApi


class UptimeKumaTestCase(unittest.TestCase):
    api = None

    @classmethod
    def setUpClass(cls):
        cls.api = UptimeKumaApi("http://127.0.0.1:3001")
        username = "testuser"
        password = "zS7zhQSc"
        if cls.api.need_setup():
            cls.api.setup(username, password)
        cls.api.login(username, password)

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
