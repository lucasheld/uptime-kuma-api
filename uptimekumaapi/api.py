import json
import time

import socketio

from . import AuthMethod
from . import MonitorType
from . import NotificationType, notification_provider_options
from . import ProxyProtocol
from . import IncidentStyle
from . import convert_from_socket, convert_to_socket, params_map_monitor, params_map_notification, params_map_proxy, params_map_status_page


def int_to_bool(data: list[dict] | dict, keys):
    if type(data) == list:
        for d in data:
            int_to_bool(d, keys)
    else:
        for key in keys:
            if key in data:
                data[key] = True if data[key] == 1 else False


def _build_monitor_data(
        type_: MonitorType,
        name: str,
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
        "type": type_,
        "name": name,
        "interval": heartbeat_interval,
        "retryInterval": heartbeat_retry_interval,
        "maxretries": retries,
        "notificationIDList": notification_ids,
        "upsideDown": upside_down_mode,
    }

    if tags:
        data.update({
            "tags": tags
        })

    if type_ == MonitorType.KEYWORD:
        data.update({
            "keyword": keyword,
        })

    if type_ in [MonitorType.HTTP, MonitorType.KEYWORD]:
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

    if type_ in [MonitorType.DNS, MonitorType.PING, MonitorType.STEAM, MonitorType.MQTT]:
        data.update({
            "hostname": hostname,
        })

    if type_ in [MonitorType.DNS, MonitorType.STEAM, MonitorType.MQTT]:
        data.update({
            "port": port,
        })

    if type_ == MonitorType.DNS:
        data.update({
            "dns_resolve_server": dns_resolve_server,
            "dns_resolve_type": dns_resolve_type,
        })

    if type_ == MonitorType.MQTT:
        data.update({
            "mqttUsername": mqtt_username,
            "mqttPassword": mqtt_password,
            "mqttTopic": mqtt_topic,
            "mqttSuccessMessage": mqtt_success_message,
        })

    if type_ == MonitorType.SQLSERVER:
        data.update({
            "databaseConnectionString": sqlserver_connection_string,
            "sqlserverQuery": sqlserver_query,
        })

    return data


def _build_notification_data(name: str, type_: NotificationType, default: bool, **kwargs):
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


def _build_proxy_data(
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


def _build_status_page_data(
        slug: str,

        # config
        id_: int,
        title: str,
        description: str = None,
        dark_theme: bool = False,
        published: bool = True,
        show_tags: bool = False,
        domain_name_list: list[str] = None,
        custom_css: str = "",
        footer_text: str = None,
        show_powered_by: bool = True,

        img_data_url: str = "/icon.svg",
        monitors: list = None
):
    if not domain_name_list:
        domain_name_list = []
    public_group_list = []
    if monitors:
        public_group_list.append({
            "name": "Services",
            "monitorList": monitors
        })
    config = {
        "id": id_,
        "slug": slug,
        "title": title,
        "description": description,
        "icon": img_data_url,
        "theme": "dark" if dark_theme else "light",
        "published": published,
        "showTags": show_tags,
        "domainNameList": domain_name_list,
        "customCSS": custom_css,
        "footerText": footer_text,
        "showPoweredBy": show_powered_by
    }
    return slug, config, img_data_url, public_group_list


class UptimeKumaApi(object):
    def __init__(self, url):
        self.sio = socketio.Client()

        self._event_data: dict[str, any] = {
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

        self.sio.on("connect", self._event_connect)
        self.sio.on("disconnect", self._event_disconnect)
        self.sio.on("monitorList", self._event_monitor_list)
        self.sio.on("notificationList", self._event_notification_list)
        self.sio.on("proxyList", self._event_proxy_list)
        self.sio.on("statusPageList", self._event_status_page_list)
        self.sio.on("heartbeatList", self._event_heartbeat_list)
        self.sio.on("importantHeartbeatList", self._event_important_heartbeat_list)
        self.sio.on("avgPing", self._event_avg_ping)
        self.sio.on("uptime", self._event_uptime)
        self.sio.on("heartbeat", self._event_heartbeat)
        self.sio.on("info", self._event_info)

        self.connect(url)

    def _get_event_data(self, event):
        while self._event_data[event] is None:
            time.sleep(0.01)
        time.sleep(0.01)  # wait for multiple messages
        return self._event_data[event]

    # event handlers

    def _event_connect(self):
        pass

    def _event_disconnect(self):
        pass

    def _event_monitor_list(self, data):
        self._event_data["monitorList"] = data

    def _event_notification_list(self, data):
        self._event_data["notificationList"] = data

    def _event_proxy_list(self, data):
        self._event_data["proxyList"] = data

    def _event_status_page_list(self, data):
        self._event_data["statusPageList"] = data

    def _event_heartbeat_list(self, id_, data, bool_):
        if self._event_data["heartbeatList"] is None:
            self._event_data["heartbeatList"] = []
        self._event_data["heartbeatList"].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_important_heartbeat_list(self, id_, data, bool_):
        if self._event_data["importantHeartbeatList"] is None:
            self._event_data["importantHeartbeatList"] = []
        self._event_data["importantHeartbeatList"].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_avg_ping(self, id_, data):
        if self._event_data["avgPing"] is None:
            self._event_data["avgPing"] = []
        self._event_data["avgPing"].append({
            "id": id_,
            "data": data,
        })

    def _event_uptime(self, id_, hours_24, days_30):
        if self._event_data["uptime"] is None:
            self._event_data["uptime"] = []
        self._event_data["uptime"].append({
            "id": id_,
            "hours_24": hours_24,
            "days_30": days_30,
        })

    def _event_heartbeat(self, data):
        if self._event_data["heartbeat"] is None:
            self._event_data["heartbeat"] = []
        self._event_data["heartbeat"].append(data)

    def _event_info(self, data):
        self._event_data["info"] = data

    # connection

    def connect(self, url: str):
        url = url.rstrip("/")
        self.sio.connect(f'{url}/socket.io/')

    def disconnect(self):
        self.sio.disconnect()

    # monitors

    def get_monitors(self):
        monitors = list(self._get_event_data("monitorList").values())
        int_to_bool(monitors, ["active"])
        return monitors

    def get_monitor(self, id_: int):
        return self.sio.call('getMonitor', id_)

    def pause_monitor(self, id_: int):
        return self.sio.call('pauseMonitor', id_)

    def resume_monitor(self, id_: int):
        return self.sio.call('resumeMonitor', id_)

    def delete_monitor(self, id_: int):
        return self.sio.call('deleteMonitor', id_)

    def get_monitor_beats(self, id_: int, period):
        return self.sio.call('getMonitorBeats', (id_, period))

    def add_monitor(self, *args, **kwargs):
        data = _build_monitor_data(*args, **kwargs)
        return self.sio.call('add', data)

    def edit_monitor(self, id_: int, **kwargs):
        monitor = self.get_monitor(id_)["monitor"]
        kwargs_sock = convert_to_socket(params_map_monitor, kwargs)
        monitor.update(kwargs_sock)
        return self.sio.call('editMonitor', monitor)

    # monitor tags

    def add_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
        return self.sio.call('addMonitorTag', (tag_id, monitor_id, value))

    # TODO: check!
    # def edit_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
    #     return self.sio.call('editMonitorTag', (tag_id, monitor_id, value))

    def delete_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
        return self.sio.call('deleteMonitorTag', (tag_id, monitor_id, value))

    # notifications

    def get_notifications(self):
        notifications_raw = self._get_event_data("notificationList")
        notifications = []
        for notification_raw in notifications_raw:
            notification = notification_raw.copy()
            config = json.loads(notification["config"])
            del notification["config"]
            notification.update(config)
            notifications.append(notification)
        return notifications

    def get_notification(self, id_: int):
        notifications = self.get_notifications()
        for notification in notifications:
            if notification["id"] == id_:
                return notification

    def test_notification(self, *args, **kwargs):
        data = _build_notification_data(*args, **kwargs)
        return self.sio.call('testNotification', data)

    def add_notification(self, *args, **kwargs):
        data = _build_notification_data(*args, **kwargs)
        return self.sio.call('addNotification', (data, None))

    def edit_notification(self, id_: int, **kwargs):
        notification = self.get_notification(id_)
        kwargs_sock = convert_to_socket(params_map_notification, kwargs)
        notification.update(kwargs_sock)
        return self.sio.call('addNotification', (notification, id_))

    def delete_notification(self, id_: int):
        return self.sio.call('deleteNotification', id_)

    def check_apprise(self):
        return self.sio.call('checkApprise')

    # proxy

    def get_proxies(self):
        proxies = self._get_event_data("proxyList")
        proxies = convert_from_socket(params_map_proxy, proxies)
        int_to_bool(proxies, ["auth", "active", "default", "apply_existing"])
        proxies = convert_to_socket(params_map_proxy, proxies)
        return proxies

    def get_proxy(self, id_: int):
        proxies = self.get_proxies()
        for proxy in proxies:
            if proxy["id"] == id_:
                return proxy

    def add_proxy(self, *args, **kwargs):
        data = _build_proxy_data(*args, **kwargs)
        return self.sio.call('addProxy', (data, None))

    def edit_proxy(self, id_: int, **kwargs):
        proxy_sock = self.get_proxy(id_)
        proxy = convert_from_socket(params_map_proxy, proxy_sock)
        for key in ["auth", "active", "default", "apply_existing"]:
            if key in proxy:
                proxy[key] = True if proxy[key] == 1 else False
        kwargs_sock = convert_to_socket(params_map_proxy, kwargs)
        proxy_sock = convert_to_socket(params_map_proxy, proxy)
        proxy_sock.update(kwargs_sock)
        return self.sio.call('addProxy', (proxy_sock, id_))
        # return proxy_sock, id_

    def delete_proxy(self, id_: int):
        return self.sio.call('deleteProxy', id_)

    # status page

    def get_status_pages(self):
        return list(self._get_event_data("statusPageList").values())

    def get_status_page(self, slug: str):
        r = self.sio.call('getStatusPage', slug)
        if r["ok"]:
            config = r["config"]
            del r["config"]
            r.update(config)
        return r

    def add_status_page(self, slug: str, title: str):
        return self.sio.call('addStatusPage', (title, slug))

    def delete_status_page(self, slug: str):
        return self.sio.call('deleteStatusPage', slug)

    def save_status_page(self, slug: str, **kwargs):
        status_page = self.get_status_page(slug)
        status_page.pop("ok")
        kwargs_sock = convert_to_socket(params_map_status_page, kwargs)
        status_page.update(kwargs_sock)
        status_page = convert_from_socket(params_map_status_page, status_page)
        data = _build_status_page_data(**status_page)
        return self.sio.call('saveStatusPage', data)

    def post_incident(
            self,
            slug: str,
            title: str,
            content: str,
            style: IncidentStyle = IncidentStyle.PRIMARY
    ):
        incident = {
            "title": title,
            "content": content,
            "style": style
        }
        r = self.sio.call('postIncident', (slug, incident))
        self.save_status_page(slug)
        return r

    def unpin_incident(self, slug: str):
        r = self.sio.call('unpinIncident', slug)
        self.save_status_page(slug)
        return r

    # heartbeat

    def get_heartbeats(self):
        return self._get_event_data("heartbeatList")

    def get_important_heartbeats(self):
        return self._get_event_data("importantHeartbeatList")

    def get_heartbeat(self):
        return self._get_event_data("heartbeat")

    # avg ping

    def avg_ping(self):
        return self._get_event_data("avgPing")

    # uptime

    def uptime(self):
        return self._get_event_data("uptime")

    # info

    def info(self):
        return self._get_event_data("info")

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

    def get_tag(self, id_: int):
        tags = self.get_tags()
        for tag in tags:
            if tag["id"] == id_:
                return tag

    # TODO: not working, monitor id required?
    # def edit_tag(self, id_: int, name: str, color: str):
    #     return self.sio.call('editTag', {
    #         "id": id_,
    #         "name": name,
    #         "color": color
    #     })

    def delete_tag(self, id_: int):
        return self.sio.call('deleteTag', id_)

    def add_tag(self, name: str, color: str):
        return self.sio.call('addTag', {
            "name": name,
            "color": color,
            "new": True
        })

    # settings

    def get_settings(self):
        return self.sio.call('getSettings')

    def set_settings(self, data, password: str):
        return self.sio.call('setSettings', (data, password))

    def change_password(self, old_password: str, new_password: str):
        return self.sio.call('changePassword', {
            "currentPassword": old_password,
            "newPassword": new_password,
        })

    def upload_backup(self, json_data, import_handle: str):
        if import_handle not in ["overwrite", "skip", "keep"]:
            raise ValueError()
        return self.sio.call('uploadBackup', (json_data, import_handle))

    # 2FA

    def twofa_status(self):
        return self.sio.call('twoFAStatus')

    def prepare_2fa(self, password: str):
        return self.sio.call('prepare2FA', password)

    def save_2fa(self, password: str):
        return self.sio.call('save2FA', password)

    def disable_2fa(self, password: str):
        return self.sio.call('disable2FA', password)

    # login

    def login(self, username: str, password: str):
        return self.sio.call('login', {
            "username": username,
            "password": password,
            "token": ""
        })

    def login_by_token(self, token: str):
        return self.sio.call('loginByToken', token)

    def verify_token(self, token: str, password: str):
        return self.sio.call('verifyToken', (token, password))

    def logout(self):
        return self.sio.call('logout')

    # setup

    def need_setup(self):
        return self.sio.call('needSetup')

    def setup(self, username: str, password: str):
        return self.sio.call("setup", (username, password))

    # database

    def get_database_size(self):
        return self.sio.call('getDatabaseSize')

    def shrink_database(self):
        return self.sio.call('shrinkDatabase')
