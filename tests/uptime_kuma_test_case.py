import json
import unittest

from uptime_kuma_api import UptimeKumaApi, Event, MonitorType

token = None


class UptimeKumaTestCase(unittest.TestCase):
    api = None
    url = "http://127.0.0.1:3001"
    username = "admin"
    password = "secret123"

    def setUp(self):
        self.api = UptimeKumaApi(self.url)

        global token
        if not token:
            if self.api.need_setup():
                self.api.setup(self.username, self.password)
            r = self.api.login(self.username, self.password)
            token = r["token"]

        self.api.login_by_token(token)

        data = {
            "version": "1.17.1",
            "notificationList": [],
            "monitorList": [],
            "proxyList": []
        }
        data_str = json.dumps(data)
        r = self.api.upload_backup(data_str, "overwrite")
        self.assertEqual(r["msg"], "Backup successfully restored.")

        self.api._event_data[Event.MONITOR_LIST] = {}

    def tearDown(self):
        self.api.disconnect()

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
