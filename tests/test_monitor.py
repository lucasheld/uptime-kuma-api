import unittest
from packaging.version import parse as parse_version

from uptime_kuma_api import UptimeKumaException, MonitorType, AuthMethod
from uptime_kuma_test_case import UptimeKumaTestCase


class TestMonitor(UptimeKumaTestCase):
    def test_monitor(self):
        notification_id_1 = self.add_notification()
        notification_id_2 = self.add_notification()

        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "interval": 60,
            "retryInterval": 60,
            "maxretries": 0,
            "notificationIDList": [notification_id_1, notification_id_2],
            "upsideDown": False,
            "url": "http://127.0.0.1"
        }
        if parse_version(self.api.version) >= parse_version("1.18"):
            expected_monitor.update({
                "resendInterval": 0
            })

        # add monitor
        r = self.api.add_monitor(**expected_monitor)
        self.assertEqual(r["msg"], "Added Successfully.")
        monitor_id = r["monitorID"]

        # get monitor
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # get monitors
        monitors = self.api.get_monitors()
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertIsNotNone(monitor)
        self.compare(monitor, expected_monitor)

        # edit monitor
        expected_monitor["type"] = "ping"
        expected_monitor["name"] = "monitor 1 new"
        expected_monitor["hostname"] = "127.0.0.10"
        del expected_monitor["url"]
        r = self.api.edit_monitor(monitor_id, **expected_monitor)
        self.assertEqual(r["msg"], "Saved.")
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # pause monitor
        r = self.api.pause_monitor(monitor_id)
        self.assertEqual(r["msg"], "Paused Successfully.")

        # resume monitor
        r = self.api.resume_monitor(monitor_id)
        self.assertEqual(r["msg"], "Resumed Successfully.")

        # get monitor beats
        self.api.get_monitor_beats(monitor_id, 6)

        # delete monitor
        r = self.api.delete_monitor(monitor_id)
        self.assertEqual(r["msg"], "Deleted Successfully.")
        with self.assertRaises(UptimeKumaException):
            self.api.get_monitor(monitor_id)

    def do_test_monitor_type(self, expected_monitor):
        r = self.api.add_monitor(**expected_monitor)
        self.assertEqual(r["msg"], "Added Successfully.")
        monitor_id = r["monitorID"]

        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        r = self.api.edit_monitor(monitor_id, **expected_monitor)
        self.assertEqual(r["msg"], "Saved.")
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)
        return monitor

    def test_monitor_type_http(self):
        proxy_id = self.add_proxy()

        json_data = '{"key": "value"}'
        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "expiryNotification": False,
            "ignoreTls": False,
            "maxredirects": 10,
            "accepted_statuscodes": ["200-299"],
            "proxyId": proxy_id,
            "method": "GET",
            "body": json_data,
            "headers": json_data,
            "authMethod": AuthMethod.NONE
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_auth_method(self):
        for auth_method in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
            expected_monitor = {
                "type": MonitorType.HTTP,
                "name": "monitor 1",
                "url": "http://127.0.0.1",
                "authMethod": auth_method,
                "basic_auth_user": "auth user",
                "basic_auth_pass": "auth pass",
            }
            self.do_test_monitor_type(expected_monitor)

        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "authMethod": AuthMethod.NTLM,
            "authDomain": "auth domain",
            "authWorkstation": "auth workstation",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_port(self):
        expected_monitor = {
            "type": MonitorType.PORT,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_ping(self):
        expected_monitor = {
            "type": MonitorType.PING,
            "name": "monitor 1",
            "hostname": "127.0.0.1"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_keyword(self):
        expected_monitor = {
            "type": MonitorType.KEYWORD,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "keyword": "healthy"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_dns(self):
        expected_monitor = {
            "type": MonitorType.DNS,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888,
            "dns_resolve_server": "1.1.1.1",
            "dns_resolve_type": "A"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_push(self):
        expected_monitor = {
            "type": MonitorType.PUSH,
            "name": "monitor 1"
        }
        monitor = self.do_test_monitor_type(expected_monitor)

        # https://github.com/lucasheld/ansible-uptime-kuma/issues/5
        self.assertIsNotNone(monitor["pushToken"])

    def test_monitor_type_steam(self):
        expected_monitor = {
            "type": MonitorType.STEAM,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_mqtt(self):
        expected_monitor = {
            "type": MonitorType.MQTT,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888,
            "mqttUsername": "mqtt username",
            "mqttPassword": "mqtt password",
            "mqttTopic": "mqtt topic",
            "mqttSuccessMessage": "mqtt success message"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_sqlserver(self):
        expected_monitor = {
            "type": MonitorType.SQLSERVER,
            "name": "monitor 1",
            "databaseConnectionString": "Server=127.0.0.1,8888;Database=test;User Id=1;Password=secret123;Encrypt=true;"
                                        "TrustServerCertificate=Yes;Connection Timeout=5",
            "databaseQuery": "select getdate()"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_postgres(self):
        if parse_version(self.api.version) < parse_version("1.18"):
            self.skipTest("Unsupported in this Uptime Kuma version")

        expected_monitor = {
            "type": MonitorType.POSTGRES,
            "name": "monitor 1",
            "databaseConnectionString": "postgres://username:password@host:port/database",
            "databaseQuery": "select getdate()"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_docker(self):
        if parse_version(self.api.version) < parse_version("1.18"):
            self.skipTest("Unsupported in this Uptime Kuma version")

        docker_host_id = self.add_docker_host()
        expected_monitor = {
            "type": MonitorType.DOCKER,
            "name": "monitor 1",
            "docker_container": "test",
            "docker_host": docker_host_id
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_radius(self):
        if parse_version(self.api.version) < parse_version("1.18"):
            self.skipTest("Unsupported in this Uptime Kuma version")

        expected_monitor = {
            "type": MonitorType.RADIUS,
            "name": "monitor 1",
            "radiusUsername": "123",
            "radiusPassword": "456",
            "radiusSecret": "789",
            "radiusCalledStationId": "1",
            "radiusCallingStationId": "2"
        }
        self.do_test_monitor_type(expected_monitor)


if __name__ == '__main__':
    unittest.main()
