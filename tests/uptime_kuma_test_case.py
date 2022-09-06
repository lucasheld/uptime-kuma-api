import json
import unittest

from uptime_kuma_api import UptimeKumaApi, Event, MonitorType

token = None


def compare(subset, superset):
    for key, value in subset.items():
        value2 = superset.get(key)
        if type(value) == list:
            for i in range(len(value)):
                if not value2:
                    return False
                elif type(value[i]) == list or type(value[i]) == dict:
                    if not compare(value[i], value2[i]):
                        return False
                else:
                    if value[i] != value2[i]:
                        return False
        elif type(value) == dict:
            if not compare(value, value2):
                return False
        else:
            if value != value2:
                return False
    return True


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
        self.assertTrue(compare(subset, superset))

    def find_by_id(self, objects, value, key="id"):
        for obj in objects:
            if obj[key] == value:
                return obj

    def add_monitor(self):
        r = self.api.add_monitor(type=MonitorType.HTTP, name="monitor 1", url="http://127.0.0.1")
        monitor_id = r["monitorID"]
        return monitor_id

    def add_tag(self):
        r = self.api.add_tag(name="tag 1", color="#ffffff")
        tag_id = r["id"]
        return tag_id

    def add_notification(self):
        r = self.api.add_notification(name="notification 1", type="PushByTechulus", pushAPIKey="123456789")
        notification_id = r["id"]
        return notification_id
