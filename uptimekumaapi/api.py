import time

import socketio

from . import AuthMethod
from . import MonitorType
from . import NotificationType, notification_provider_options
from . import ProxyProtocol


class UptimeKumaApi(object):
    def __init__(self, url):
        self.sio = socketio.Client()

        self.event_data: dict[str, any] = {
            "monitorList": None,
            "notificationList": None,
            "proxyList": None,
            "statusPageList": None,
            "heartbeatList": None,
            "importantHeartbeatList": None,
            "avgPing": None,
            "uptime": None,
            "heartbeat": None,
            "info": None,
        }

        self.sio.on("connect", self.event_connect)
        self.sio.on("disconnect", self.event_disconnect)
        self.sio.on("monitorList", self.event_monitor_list)
        self.sio.on("notificationList", self.event_notification_list)
        self.sio.on("proxyList", self.event_proxy_list)
        self.sio.on("statusPageList", self.event_status_page_list)
        self.sio.on("heartbeatList", self.event_heartbeat_list)
        self.sio.on("importantHeartbeatList",
                    self.event_important_heartbeat_list)
        self.sio.on("avgPing", self.event_avg_ping)
        self.sio.on("uptime", self.event_uptime)
        self.sio.on("heartbeat", self.event_heartbeat)
        self.sio.on("info", self.event_info)

        self.connect(url)

    def get_event_data(self, event):
        while self.event_data[event] is None:
            time.sleep(0.01)
        time.sleep(0.01)  # wait for multiple messages
        return self.event_data[event]

    # event handlers

    def event_connect(self):
        pass

    def event_disconnect(self):
        pass

    def event_monitor_list(self, data):
        self.event_data["monitorList"] = data

    def event_notification_list(self, data):
        self.event_data["notificationList"] = data

    def event_proxy_list(self, data):
        self.event_data["proxyList"] = data

    def event_status_page_list(self, data):
        self.event_data["statusPageList"] = data

    def event_heartbeat_list(self, id_, data, bool_):
        if self.event_data["heartbeatList"] is None:
            self.event_data["heartbeatList"] = []
        self.event_data["heartbeatList"].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def event_important_heartbeat_list(self, id_, data, bool_):
        if self.event_data["importantHeartbeatList"] is None:
            self.event_data["importantHeartbeatList"] = []
        self.event_data["importantHeartbeatList"].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def event_avg_ping(self, id_, data):
        if self.event_data["avgPing"] is None:
            self.event_data["avgPing"] = []
        self.event_data["avgPing"].append({
            "id": id_,
            "data": data,
        })

    def event_uptime(self, id_, hours_24, days_30):
        if self.event_data["uptime"] is None:
            self.event_data["uptime"] = []
        self.event_data["uptime"].append({
            "id": id_,
            "hours_24": hours_24,
            "days_30": days_30,
        })

    def event_heartbeat(self, data):
        if self.event_data["heartbeat"] is None:
            self.event_data["heartbeat"] = []
        self.event_data["heartbeat"].append(data)

    def event_info(self, data):
        self.event_data["info"] = data

    # connection

    def connect(self, url):
        url = url.rstrip("/")
        self.sio.connect(f'{url}/socket.io/')

    def disconnect(self):
        self.sio.disconnect()

    # monitors

    def get_monitors(self):
        return self.get_event_data("monitorList")

    def get_monitor(self, id_):
        return self.sio.call('getMonitor', id_)

    def pause_monitor(self, id_):
        return self.sio.call('pauseMonitor', id_)

    def resume_monitor(self, id_):
        return self.sio.call('resumeMonitor', id_)

    def delete_monitor(self, id_):
        return self.sio.call('deleteMonitor', id_)

    def get_monitor_beats(self, id_, period):
        return self.sio.call('getMonitorBeats', (id_, period))

    def add_monitor(self, *args, **kwargs):
        data = self._build_monitor_data(*args, **kwargs)
        return self.sio.call('add', data)

    def edit_monitor(self, id_, *args, **kwargs):
        data = self._build_monitor_data(*args, **kwargs)
        data.update({
            "id": id_
        })
        return self.sio.call('editMonitor', data)

    def _build_monitor_data(
            self,
            monitor_type: MonitorType,
            friendly_name: str,
            heartbeat_interval: int = 60,
            heartbeat_retry_interval: int = 60,
            retries: int = 0,
            upside_down_mode: bool = False,
            tags: list = None,
            notification_ids: list[int] = None,
            # HTTP, KEYWORD
            url: str = None,
            certificate_expiry_notification: bool = False,
            ignore_tls_error: bool = False,
            max_redirects: int = 10,
            accepted_status_codes: list[str] = None,
            proxy_id: int = None,
            http_method: str = "GET",
            http_body: str = None,
            http_headers: str = None,
            auth_method: AuthMethod = AuthMethod.NONE,
            auth_user: str = None,
            auth_pass: str = None,
            auth_domain: str = None,
            auth_workstation: str = None,
            # KEYWORD
            keyword: str = None,
            # DNS, PING, STEAM, MQTT
            hostname: str = None,
            # DNS, STEAM, MQTT
            port: int = 53,
            # DNS
            dns_resolve_server: str = "1.1.1.1",
            dns_resolve_type: str = "A",
            # MQTT
            mqtt_username: str = None,
            mqtt_password: str = None,
            mqtt_topic: str = None,
            mqtt_success_message: str = None,
            # SQLSERVER
            sqlserver_connection_string: str = "Server=<hostname>,<port>;Database=<your database>;User Id=<your user id>;Password=<your password>;Encrypt=<true/false>;TrustServerCertificate=<Yes/No>;Connection Timeout=<int>",
            sqlserver_query: str = None,
    ):
        if not accepted_status_codes:
            accepted_status_codes = ["200-299"]

        dict_notification_ids = {}
        if notification_ids:
            for notification_id in notification_ids:
                dict_notification_ids[notification_id] = True
        notification_ids = dict_notification_ids

        data = {
            "type": monitor_type,
            "name": friendly_name,
            "interval": heartbeat_interval,
            "retryInterval": heartbeat_retry_interval,
            "maxretries": retries,
            "notificationIDList": notification_ids,
            "upsideDown": upside_down_mode,
        }

        if monitor_type == MonitorType.KEYWORD:
            data.update({
                "keyword": keyword,
            })

        if monitor_type in [MonitorType.HTTP, MonitorType.KEYWORD]:
            data.update({
                "url": url,
                "expiryNotification": certificate_expiry_notification,
                "ignoreTls": ignore_tls_error,
                "maxredirects": max_redirects,
                "accepted_statuscodes": accepted_status_codes,
                "proxyId": proxy_id,
                "method": http_method,
                "body": http_body,
                "headers": http_headers,
                "authMethod": auth_method,
            })

            if auth_method in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
                data.update({
                    "basicauth-user": auth_user,
                    "basicauth-pass": auth_pass,
                })

            if auth_method == AuthMethod.NTLM:
                data.update({
                    "basicauth-domain": auth_domain,
                    "basicauth-workstation": auth_workstation,
                })

        if monitor_type in [MonitorType.DNS, MonitorType.PING, MonitorType.STEAM, MonitorType.MQTT]:
            data.update({
                "hostname": hostname,
            })

        if monitor_type in [MonitorType.DNS, MonitorType.STEAM, MonitorType.MQTT]:
            data.update({
                "port": port,
            })

        if monitor_type == MonitorType.DNS:
            data.update({
                "dns_resolve_server": dns_resolve_server,
                "dns_resolve_type": dns_resolve_type,
            })

        if monitor_type == MonitorType.MQTT:
            data.update({
                "mqttUsername": mqtt_username,
                "mqttPassword": mqtt_password,
                "mqttTopic": mqtt_topic,
                "mqttSuccessMessage": mqtt_success_message,
            })

        if monitor_type == MonitorType.SQLSERVER:
            data.update({
                "databaseConnectionString": sqlserver_connection_string,
                "sqlserverQuery": sqlserver_query,
            })

        return data

    # monitor tags

    def add_monitor_tag(self, tag_id, monitor_id, value):
        return self.sio.call('addMonitorTag', (tag_id, monitor_id, value))

    def edit_monitor_tag(self, tag_id, monitor_id, value):
        return self.sio.call('editMonitorTag', (tag_id, monitor_id, value))

    def delete_monitor_tag(self, tag_id, monitor_id, value):
        return self.sio.call('deleteMonitorTag', (tag_id, monitor_id, value))

    # notifications

    def get_notifications(self):
        return self.get_event_data("notificationList")

    def test_notification(self, *args, **kwargs):
        data = self._build_notification_data(*args, **kwargs)
        return self.sio.call('testNotification', data)

    def add_notification(self, *args, **kwargs):
        data = self._build_notification_data(*args, **kwargs)
        return self.sio.call('addNotification', (data, None))

    def edit_notification(self, id_: int, *args, **kwargs):
        data = self._build_notification_data(*args, **kwargs)
        return self.sio.call('addNotification', (data, id_))

    def delete_notification(self, id_: int):
        return self.sio.call('deleteNotification', id_)

    def check_apprise(self):
        return self.sio.call('checkApprise')

    def _build_notification_data(self, name: str, type_: NotificationType, default: bool, **kwargs):
        allowed_options = notification_provider_options[type_]
        s1 = set(allowed_options)
        s2 = set(kwargs.keys())
        if len(s1 - s2) > 0 or len(s2 - s1) > 0:
            raise ValueError(f"Allowed options: {allowed_options}")

        return {
            "name": name,
            "type": type_,
            "isDefault": default,
            **kwargs
        }

    # proxy

    def get_proxies(self):
        return self.get_event_data("proxyList")

    def add_proxy(self, *args, **kwargs):
        data = self._build_proxy_data(*args, **kwargs)
        return self.sio.call('addProxy', (data, None))

    def edit_proxy(self, id_: int, *args, **kwargs):
        data = self._build_proxy_data(*args, **kwargs)
        return self.sio.call('addProxy', (data, id_))

    def delete_proxy(self, id_: int):
        return self.sio.call('deleteProxy', id_)

    def _build_proxy_data(
            self,
            protocol: ProxyProtocol,
            host: str,
            port: str,
            auth: bool = False,
            username: str = None,
            password: str = None,
            active: bool = True,
            default: bool = False,
            apply_existing: bool = False,
    ):
        return {
            "protocol": protocol,
            "host": host,
            "port": port,
            "auth": auth,
            "username": username,
            "password": password,
            "active": active,
            "default": default,
            "applyExisting": apply_existing
        }

    # status page

    def get_statuspages(self):
        return self.get_event_data("statusPageList")

    # heartbeat

    def get_heartbeats(self):
        return self.get_event_data("heartbeatList")

    def get_important_heartbeats(self):
        return self.get_event_data("importantHeartbeatList")

    def get_heartbeat(self):
        return self.get_event_data("heartbeat")

    # avg ping

    def avg_ping(self):
        return self.get_event_data("avgPing")

    # uptime

    def uptime(self):
        return self.get_event_data("uptime")

    # info

    def info(self):
        return self.get_event_data("info")

    # clear

    def clear_events(self):
        return self.sio.call('clearEvents')

    def clear_heartbeats(self):
        return self.sio.call('clearHeartbeats')

    def clear_statistics(self):
        return self.sio.call('clearStatistics')

    # tags

    def get_tags(self):
        return self.sio.call('getTags')

    def edit_tag(self, tag):
        return self.sio.call('editTag', tag)

    def delete_tag(self, id_):
        return self.sio.call('deleteTag', id_)

    def add_tag(self, color, name):
        return self.sio.call('addTag', {
            "color": color,
            "name": name,
            "new": True
        })

    # settings

    def get_settings(self):
        return self.sio.call('getSettings')

    def set_settings(self, data, password):
        return self.sio.call('setSettings', (data, password))

    def change_password(self, old_password, new_password):
        return self.sio.call('changePassword', {
            "currentPassword": old_password,
            "newPassword": new_password,
        })

    def upload_backup(self, json_data, import_handle):
        if import_handle not in ["overwrite", "skip", "keep"]:
            raise ValueError()
        return self.sio.call('uploadBackup', (json_data, import_handle))

    # 2FA

    def twofa_status(self):
        return self.sio.call('twoFAStatus')

    def prepare_2fa(self, password):
        return self.sio.call('prepare2FA', password)

    def save_2fa(self, password):
        return self.sio.call('save2FA', password)

    def disable_2fa(self, password):
        return self.sio.call('disable2FA', password)

    # login

    def login(self, username, password):
        return self.sio.call('login', {
            "username": username,
            "password": password,
            "token": ""
        })

    def login_by_token(self, token):
        return self.sio.call('loginByToken', token)

    def verify_token(self, token, password):
        return self.sio.call('verifyToken', (token, password))

    def logout(self):
        return self.sio.call('logout')

    # setup

    def need_setup(self):
        return self.sio.call('needSetup')

    def setup(self, username, password):
        return self.sio.call("setup", (username, password))
