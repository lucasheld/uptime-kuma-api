import unittest
import warnings
from packaging.version import parse as parse_version

from uptime_kuma_api import UptimeKumaApi, MonitorType, DockerType, UptimeKumaException

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
        warnings.simplefilter("ignore", ResourceWarning)

        self.api = UptimeKumaApi(self.url)

        global token
        if not token:
            if self.api.need_setup():
                self.api.setup(self.username, self.password)
            r = self.api.login(self.username, self.password)
            token = r["token"]

        self.api.login_by_token(token)

        # delete monitors
        monitors = self.api.get_monitors()
        for monitor in monitors:
            self.api.delete_monitor(monitor["id"])

        # delete notifications
        notifications = self.api.get_notifications()
        for notification in notifications:
            self.api.delete_notification(notification["id"])

        # delete proxies
        proxies = self.api.get_proxies()
        for proxy in proxies:
            self.api.delete_proxy(proxy["id"])

        # delete tags
        tags = self.api.get_tags()
        for tag in tags:
            self.api.delete_tag(tag["id"])

        # delete status pages
        status_pages = self.api.get_status_pages()
        for status_page in status_pages:
            self.api.delete_status_page(status_page["slug"])

        if parse_version(self.api.version) >= parse_version("1.18"):
            # delete docker hosts
            docker_hosts = self.api.get_docker_hosts()
            for docker_host in docker_hosts:
                self.api.delete_docker_host(docker_host["id"])

        if parse_version(self.api.version) >= parse_version("1.19"):
            # delete maintenances
            maintenances = self.api.get_maintenances()
            for maintenance in maintenances:
                self.api.delete_maintenance(maintenance["id"])

        if parse_version(self.api.version) >= parse_version("1.21"):
            # delete api keys
            api_keys = self.api.get_api_keys()
            for api_key in api_keys:
                self.api.delete_api_key(api_key["id"])

        # login again to receive initial messages
        self.api.disconnect()
        self.api = UptimeKumaApi(self.url)
        self.api.login_by_token(token)

    def tearDown(self):
        self.api.disconnect()

    def compare(self, superset, subset):
        self.assertTrue(compare(subset, superset))

    def find_by_id(self, objects, value, key="id"):
        for obj in objects:
            if obj[key] == value:
                return obj

    def add_monitor(self, name="monitor 1"):
        r = self.api.add_monitor(
            type=MonitorType.HTTP,
            name=name,
            url="http://127.0.0.1"
        )
        monitor_id = r["monitorID"]
        return monitor_id

    def add_tag(self):
        r = self.api.add_tag(
            name="tag 1",
            color="#ffffff"
        )
        tag_id = r["id"]
        return tag_id

    def add_notification(self):
        r = self.api.add_notification(
            name="notification 1",
            type="PushByTechulus",
            pushAPIKey="123456789"
        )
        notification_id = r["id"]
        return notification_id

    def add_proxy(self):
        r = self.api.add_proxy(
            protocol="http",
            host="127.0.0.1",
            port=8080,
            active=True
        )
        proxy_id = r["id"]
        return proxy_id

    def add_docker_host(self):
        r = self.api.add_docker_host(
            name="docker host 1",
            dockerType=DockerType.SOCKET
        )
        docker_host_id = r["id"]
        return docker_host_id

    def add_status_page(self, title="status page 1"):
        slug = "statuspage1"
        self.api.add_status_page(slug, title)
        r = self.api.get_status_page(slug)
        return r["id"]
