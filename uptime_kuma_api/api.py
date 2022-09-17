import json
import time
import string
import random

import requests
import socketio
from packaging.version import parse as parse_version

from . import AuthMethod
from . import MonitorType
from . import NotificationType, notification_provider_options, notification_provider_conditions
from . import ProxyProtocol
from . import IncidentStyle
from . import DockerType
from . import Event
from . import UptimeKumaException


def int_to_bool(data, keys):
    if type(data) == list:
        for d in data:
            int_to_bool(d, keys)
    else:
        for key in keys:
            if key in data:
                data[key] = True if data[key] == 1 else False


def gen_secret(length: int) -> str:
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def _convert_monitor_return(monitor):
    monitor["notificationIDList"] = [int(i) for i in monitor["notificationIDList"].keys()]


def _convert_monitor_input(kwargs):
    if not kwargs["accepted_statuscodes"]:
        kwargs["accepted_statuscodes"] = ["200-299"]

    dict_notification_ids = {}
    if kwargs["notificationIDList"]:
        for notification_id in kwargs["notificationIDList"]:
            dict_notification_ids[notification_id] = True
    kwargs["notificationIDList"] = dict_notification_ids

    if not kwargs["databaseConnectionString"]:
        if kwargs["type"] == MonitorType.SQLSERVER:
            kwargs["databaseConnectionString"] = "Server=<hostname>,<port>;Database=<your database>;User Id=<your user id>;Password=<your password>;Encrypt=<true/false>;TrustServerCertificate=<Yes/No>;Connection Timeout=<int>"
        elif kwargs["type"] == MonitorType.POSTGRES:
            kwargs["databaseConnectionString"] = "postgres://username:password@host:port/database"

    if kwargs["type"] == MonitorType.PUSH and not kwargs.get("pushToken"):
        kwargs["pushToken"] = gen_secret(10)


def _build_notification_data(
        name: str,
        type: NotificationType,
        isDefault: bool = False,
        applyExisting: bool = False,
        **kwargs
):
    data = {
        "name": name,
        "type": type,
        "isDefault": isDefault,
        "applyExisting": applyExisting,
        **kwargs
    }
    return data


def _build_proxy_data(
        protocol: ProxyProtocol,
        host: str,
        port: str,
        auth: bool = False,
        username: str = None,
        password: str = None,
        active: bool = True,
        default: bool = False,
        applyExisting: bool = False,
):
    data = {
        "protocol": protocol,
        "host": host,
        "port": port,
        "auth": auth,
        "username": username,
        "password": password,
        "active": active,
        "default": default,
        "applyExisting": applyExisting
    }
    return data


def _build_status_page_data(
        slug: str,

        # config
        id: int,
        title: str,
        description: str = None,
        theme: str = "light",
        published: bool = True,
        showTags: bool = False,
        domainNameList: list = None,
        customCSS: str = "",
        footerText: str = None,
        showPoweredBy: bool = True,

        icon: str = "/icon.svg",
        publicGroupList: list = None
):
    if theme not in ["light", "dark"]:
        raise ValueError
    if not domainNameList:
        domainNameList = []
    if not publicGroupList:
        publicGroupList = []
    config = {
        "id": id,
        "slug": slug,
        "title": title,
        "description": description,
        "icon": icon,
        "theme": theme,
        "published": published,
        "showTags": showTags,
        "domainNameList": domainNameList,
        "customCSS": customCSS,
        "footerText": footerText,
        "showPoweredBy": showPoweredBy
    }
    return slug, config, icon, publicGroupList


def _convert_docker_host_input(kwargs):
    if not kwargs["dockerDaemon"]:
        if kwargs["dockerType"] == DockerType.SOCKET:
            kwargs["dockerDaemon"] = "/var/run/docker.sock"
        elif kwargs["dockerType"] == DockerType.TCP:
            kwargs["dockerDaemon"] = "tcp://localhost:2375"


def _build_docker_host_data(
        name: str,
        dockerType: DockerType,
        dockerDaemon: str = None
):
    data = {
        "name": name,
        "dockerType": dockerType,
        "dockerDaemon": dockerDaemon
    }
    return data


def _check_missing_arguments(required_params, kwargs):
    missing_arguments = []
    for required_param in required_params:
        if kwargs.get(required_param) is None:
            missing_arguments.append(required_param)
    if missing_arguments:
        missing_arguments_str = ", ".join([f"'{i}'" for i in missing_arguments])
        raise TypeError(f"missing {len(missing_arguments)} required argument: {missing_arguments_str}")


def _check_argument_conditions(valid_params, kwargs):
    for valid_param in valid_params:
        if valid_param in kwargs:
            value = kwargs[valid_param]
            conditions = valid_params[valid_param]
            min_ = conditions.get("min")
            max_ = conditions.get("max")
            if min_ is not None and value < min_:
                raise ValueError(f"the value of {valid_param} must not be less than {min_}")
            if max_ is not None and value > max_:
                raise ValueError(f"the value of {valid_param} must not be larger than {max_}")


def _check_arguments_monitor(kwargs):
    required_args = [
        "type",
        "name",
        "interval",
        "maxretries",
        "retryInterval"
    ]
    _check_missing_arguments(required_args, kwargs)

    required_args_by_type = {
        MonitorType.HTTP: ["url", "maxredirects"],
        MonitorType.PORT: ["hostname", "port"],
        MonitorType.PING: ["hostname"],
        MonitorType.KEYWORD: ["url", "keyword", "maxredirects"],
        MonitorType.DNS: ["hostname", "dns_resolve_server", "port"],
        MonitorType.PUSH: [],
        MonitorType.STEAM: ["hostname", "port"],
        MonitorType.MQTT: ["hostname", "port", "mqttTopic"],
        MonitorType.SQLSERVER: [],
        MonitorType.POSTGRES: [],
        MonitorType.DOCKER: ["docker_container", "docker_host"],
        MonitorType.RADIUS: ["radiusUsername", "radiusPassword", "radiusSecret", "radiusCalledStationId", "radiusCallingStationId"]
    }
    type_ = kwargs["type"]
    required_args = required_args_by_type[type_]
    _check_missing_arguments(required_args, kwargs)

    conditions = {
        "interval": {
            "min": 20
        },
        "maxretries": {
            "min": 0
        },
        "retryInterval": {
            "min": 20
        },
        "maxredirects": {
            "min": 0
        },
        "port": {
            "min": 0,
            "max": 65535
        }
    }
    _check_argument_conditions(conditions, kwargs)


def _check_arguments_notification(kwargs):
    required_args = ["type", "name"]
    _check_missing_arguments(required_args, kwargs)

    type_ = kwargs["type"]
    required_args = notification_provider_options[type_]
    _check_missing_arguments(required_args, kwargs)
    _check_argument_conditions(notification_provider_conditions, kwargs)


def _check_arguments_proxy(kwargs):
    required_args = ["protocol", "host", "port"]
    if kwargs.get("auth"):
        required_args.extend(["username", "password"])
    _check_missing_arguments(required_args, kwargs)

    conditions = {
        "port": {
            "min": 0,
            "max": 65535
        }
    }
    _check_argument_conditions(conditions, kwargs)


class UptimeKumaApi(object):
    def __init__(self, url):
        self.url = url
        self.sio = socketio.Client()

        self._event_data: dict = {
            Event.MONITOR_LIST: None,
            Event.NOTIFICATION_LIST: None,
            Event.PROXY_LIST: None,
            Event.STATUS_PAGE_LIST: None,
            Event.HEARTBEAT_LIST: None,
            Event.IMPORTANT_HEARTBEAT_LIST: None,
            Event.AVG_PING: None,
            Event.UPTIME: None,
            Event.HEARTBEAT: None,
            Event.INFO: None,
            Event.CERT_INFO: None,
            Event.DOCKER_HOST_LIST: None
        }

        self.sio.on(Event.CONNECT, self._event_connect)
        self.sio.on(Event.DISCONNECT, self._event_disconnect)
        self.sio.on(Event.MONITOR_LIST, self._event_monitor_list)
        self.sio.on(Event.NOTIFICATION_LIST, self._event_notification_list)
        self.sio.on(Event.PROXY_LIST, self._event_proxy_list)
        self.sio.on(Event.STATUS_PAGE_LIST, self._event_status_page_list)
        self.sio.on(Event.HEARTBEAT_LIST, self._event_heartbeat_list)
        self.sio.on(Event.IMPORTANT_HEARTBEAT_LIST, self._event_important_heartbeat_list)
        self.sio.on(Event.AVG_PING, self._event_avg_ping)
        self.sio.on(Event.UPTIME, self._event_uptime)
        self.sio.on(Event.HEARTBEAT, self._event_heartbeat)
        self.sio.on(Event.INFO, self._event_info)
        self.sio.on(Event.CERT_INFO, self._event_cert_info)
        self.sio.on(Event.DOCKER_HOST_LIST, self._event_docker_host_list)

        self.connect()

    def _get_event_data(self, event):
        monitor_events = [Event.AVG_PING, Event.UPTIME, Event.HEARTBEAT_LIST, Event.IMPORTANT_HEARTBEAT_LIST, Event.CERT_INFO, Event.HEARTBEAT]
        while self._event_data[event] is None:
            # do not wait for events that are not sent
            if self._event_data[Event.MONITOR_LIST] == {} and event in monitor_events:
                return []
            time.sleep(0.01)
        time.sleep(0.01)  # wait for multiple messages
        return self._event_data[event]

    def _call(self, event, data=None):
        r = self.sio.call(event, data)
        if type(r) == dict and "ok" in r:
            if not r["ok"]:
                raise UptimeKumaException(r["msg"])
            r.pop("ok")
        return r

    # event handlers

    def _event_connect(self):
        pass

    def _event_disconnect(self):
        pass

    def _event_monitor_list(self, data):
        self._event_data[Event.MONITOR_LIST] = data

    def _event_notification_list(self, data):
        self._event_data[Event.NOTIFICATION_LIST] = data

    def _event_proxy_list(self, data):
        self._event_data[Event.PROXY_LIST] = data

    def _event_status_page_list(self, data):
        self._event_data[Event.STATUS_PAGE_LIST] = data

    def _event_heartbeat_list(self, id_, data, bool_):
        if self._event_data[Event.HEARTBEAT_LIST] is None:
            self._event_data[Event.HEARTBEAT_LIST] = []
        self._event_data[Event.HEARTBEAT_LIST].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_important_heartbeat_list(self, id_, data, bool_):
        if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = []
        self._event_data[Event.IMPORTANT_HEARTBEAT_LIST].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_avg_ping(self, id_, data):
        if self._event_data[Event.AVG_PING] is None:
            self._event_data[Event.AVG_PING] = []
        self._event_data[Event.AVG_PING].append({
            "id": id_,
            "data": data,
        })

    def _event_uptime(self, id_, hours_24, days_30):
        if self._event_data[Event.UPTIME] is None:
            self._event_data[Event.UPTIME] = []
        self._event_data[Event.UPTIME].append({
            "id": id_,
            "hours_24": hours_24,
            "days_30": days_30,
        })

    def _event_heartbeat(self, data):
        if self._event_data[Event.HEARTBEAT] is None:
            self._event_data[Event.HEARTBEAT] = []
        self._event_data[Event.HEARTBEAT].append(data)

    def _event_info(self, data):
        self._event_data[Event.INFO] = data

    def _event_cert_info(self, id_, data):
        if self._event_data[Event.CERT_INFO] is None:
            self._event_data[Event.CERT_INFO] = []
        self._event_data[Event.CERT_INFO].append({
            "id": id_,
            "data": data,
        })

    def _event_docker_host_list(self, data):
        self._event_data[Event.DOCKER_HOST_LIST] = data

    # connection

    def connect(self):
        url = self.url.rstrip("/")
        try:
            self.sio.connect(f'{url}/socket.io/')
        except:
            print("")

    def disconnect(self):
        self.sio.disconnect()

    # builder

    @property
    def version(self):
        info = self.info()
        return info["version"]

    def _build_monitor_data(
            self,
            type: MonitorType,
            name: str,
            interval: int = 60,
            retryInterval: int = 60,
            resendInterval: int = 0,
            maxretries: int = 0,
            upsideDown: bool = False,
            notificationIDList: list = None,

            # HTTP, KEYWORD
            url: str = None,
            expiryNotification: bool = False,
            ignoreTls: bool = False,
            maxredirects: int = 10,
            accepted_statuscodes: list = None,
            proxyId: int = None,
            method: str = "GET",
            body: str = None,
            headers: str = None,
            authMethod: AuthMethod = AuthMethod.NONE,
            basic_auth_user: str = None,
            basic_auth_pass: str = None,
            authDomain: str = None,
            authWorkstation: str = None,

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
            mqttUsername: str = None,
            mqttPassword: str = None,
            mqttTopic: str = None,
            mqttSuccessMessage: str = None,

            # SQLSERVER, POSTGRES
            databaseConnectionString: str = None,
            databaseQuery: str = None,

            # DOCKER
            docker_container: str = "",
            docker_host: int = None,

            # RADIUS
            radiusUsername: str = None,
            radiusPassword: str = None,
            radiusSecret: str = None,
            radiusCalledStationId: str = None,
            radiusCallingStationId: str = None
    ):
        data = {
            "type": type,
            "name": name,
            "interval": interval,
            "retryInterval": retryInterval,
            "maxretries": maxretries,
            "notificationIDList": notificationIDList,
            "upsideDown": upsideDown,
        }

        if parse_version(self.version) >= parse_version("1.18"):
            data.update({
                "resendInterval": resendInterval
            })

        if type == MonitorType.KEYWORD:
            data.update({
                "keyword": keyword,
            })

        # HTTP, KEYWORD
        data.update({
            "url": url,
            "expiryNotification": expiryNotification,
            "ignoreTls": ignoreTls,
            "maxredirects": maxredirects,
            "accepted_statuscodes": accepted_statuscodes,
            "proxyId": proxyId,
            "method": method,
            "body": body,
            "headers": headers,
            "authMethod": authMethod,
        })

        if authMethod in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
            data.update({
                "basic_auth_user": basic_auth_user,
                "basic_auth_pass": basic_auth_pass,
            })

        if authMethod == AuthMethod.NTLM:
            data.update({
                "authDomain": authDomain,
                "authWorkstation": authWorkstation,
            })

        # DNS, PING, STEAM, MQTT
        data.update({
            "hostname": hostname,
        })

        # DNS, STEAM, MQTT
        data.update({
            "port": port,
        })

        # DNS
        data.update({
            "dns_resolve_server": dns_resolve_server,
            "dns_resolve_type": dns_resolve_type,
        })

        # MQTT
        data.update({
            "mqttUsername": mqttUsername,
            "mqttPassword": mqttPassword,
            "mqttTopic": mqttTopic,
            "mqttSuccessMessage": mqttSuccessMessage,
        })

        # SQLSERVER, POSTGRES
        data.update({
            "databaseConnectionString": databaseConnectionString
        })
        if type in [MonitorType.SQLSERVER, MonitorType.POSTGRES]:
            data.update({
                "databaseQuery": databaseQuery,
            })

        # DOCKER
        if type == MonitorType.DOCKER:
            data.update({
                "docker_container": docker_container,
                "docker_host": docker_host
            })

        # RADIUS
        if type == MonitorType.RADIUS:
            data.update({
                "radiusUsername": radiusUsername,
                "radiusPassword": radiusPassword,
                "radiusSecret": radiusSecret,
                "radiusCalledStationId": radiusCalledStationId,
                "radiusCallingStationId": radiusCallingStationId
            })

        return data

    # monitors

    def get_monitors(self):
        r = list(self._get_event_data(Event.MONITOR_LIST).values())
        for monitor in r:
            _convert_monitor_return(monitor)
        int_to_bool(r, ["active"])
        return r

    def get_monitor(self, id_: int):
        r = self._call('getMonitor', id_)["monitor"]
        _convert_monitor_return(r)
        int_to_bool(r, ["active"])
        return r

    def pause_monitor(self, id_: int):
        return self._call('pauseMonitor', id_)

    def resume_monitor(self, id_: int):
        return self._call('resumeMonitor', id_)

    def delete_monitor(self, id_: int):
        return self._call('deleteMonitor', id_)

    def get_monitor_beats(self, id_: int, hours: int):
        r = self._call('getMonitorBeats', (id_, hours))["data"]
        int_to_bool(r, ["important", "status"])
        return r

    def add_monitor(self, **kwargs):
        data = self._build_monitor_data(**kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        r = self._call('add', data)
        return r

    def edit_monitor(self, id_: int, **kwargs):
        data = self.get_monitor(id_)
        data.update(kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        r = self._call('editMonitor', data)
        return r

    # monitor tags

    def add_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
        return self._call('addMonitorTag', (tag_id, monitor_id, value))

    # editMonitorTag is unused in uptime-kuma
    # def edit_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
    #     return self._call('editMonitorTag', (tag_id, monitor_id, value))

    def delete_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
        return self._call('deleteMonitorTag', (tag_id, monitor_id, value))

    # notifications

    def get_notifications(self):
        notifications = self._get_event_data(Event.NOTIFICATION_LIST)
        r = []
        for notification_raw in notifications:
            notification = notification_raw.copy()
            config = json.loads(notification["config"])
            del notification["config"]
            notification.update(config)
            r.append(notification)
        return r

    def get_notification(self, id_: int):
        notifications = self.get_notifications()
        for notification in notifications:
            if notification["id"] == id_:
                return notification
        raise UptimeKumaException("notification does not exist")

    def test_notification(self, **kwargs):
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        return self._call('testNotification', data)

    def add_notification(self, **kwargs):
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        return self._call('addNotification', (data, None))

    def edit_notification(self, id_: int, **kwargs):
        notification = self.get_notification(id_)

        # remove old notification provider options from notification object
        if "type" in kwargs and kwargs["type"] != notification["type"]:
            for provider in notification_provider_options:
                provider_options = notification_provider_options[provider]
                if provider != kwargs["type"]:
                    for option in provider_options:
                        if option in notification:
                            del notification[option]

        notification.update(kwargs)
        _check_arguments_notification(notification)
        return self._call('addNotification', (notification, id_))

    def delete_notification(self, id_: int):
        return self._call('deleteNotification', id_)

    def check_apprise(self):
        return self._call('checkApprise')

    # proxy

    def get_proxies(self):
        r = self._get_event_data(Event.PROXY_LIST)
        int_to_bool(r, ["auth", "active", "default", "applyExisting"])
        return r

    def get_proxy(self, id_: int):
        proxies = self.get_proxies()
        for proxy in proxies:
            if proxy["id"] == id_:
                return proxy
        raise UptimeKumaException("proxy does not exist")

    def add_proxy(self, **kwargs):
        data = _build_proxy_data(**kwargs)

        _check_arguments_proxy(data)
        return self._call('addProxy', (data, None))

    def edit_proxy(self, id_: int, **kwargs):
        proxy = self.get_proxy(id_)
        proxy.update(kwargs)
        _check_arguments_proxy(proxy)
        return self._call('addProxy', (proxy, id_))

    def delete_proxy(self, id_: int):
        return self._call('deleteProxy', id_)

    # status page

    def get_status_pages(self):
        r = list(self._get_event_data(Event.STATUS_PAGE_LIST).values())
        return r

    def get_status_page(self, slug: str):
        r1 = self._call('getStatusPage', slug)
        r2 = requests.get(f"{self.url}/api/status-page/{slug}").json()

        config = r1["config"]
        config.update(r2["config"])
        return {
            **config,
            "incident": r2["incident"],
            "publicGroupList": r2["publicGroupList"]
        }

    def add_status_page(self, slug: str, title: str):
        return self._call('addStatusPage', (title, slug))

    def delete_status_page(self, slug: str):
        return self._call('deleteStatusPage', slug)

    def save_status_page(self, slug: str, **kwargs):
        status_page = self.get_status_page(slug)
        status_page.pop("incident")
        status_page.update(kwargs)
        data = _build_status_page_data(**status_page)
        return self._call('saveStatusPage', data)

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
        r = self._call('postIncident', (slug, incident))["incident"]
        self.save_status_page(slug)
        return r

    def unpin_incident(self, slug: str):
        r = self._call('unpinIncident', slug)
        self.save_status_page(slug)
        return r

    # heartbeat

    def get_heartbeats(self):
        r = self._get_event_data(Event.HEARTBEAT_LIST)
        for i in r:
            int_to_bool(i["data"], ["important", "status"])
        return r

    def get_important_heartbeats(self):
        r = self._get_event_data(Event.IMPORTANT_HEARTBEAT_LIST)
        for i in r:
            int_to_bool(i["data"], ["important", "status"])
        return r

    def get_heartbeat(self):
        r = self._get_event_data(Event.HEARTBEAT)
        int_to_bool(r, ["important", "status"])
        return r

    # avg ping

    def avg_ping(self):
        return self._get_event_data(Event.AVG_PING)

    # cert info

    def cert_info(self):
        return self._get_event_data(Event.CERT_INFO)

    # uptime

    def uptime(self):
        return self._get_event_data(Event.UPTIME)

    # info

    def info(self) -> dict:
        r = self._get_event_data(Event.INFO)
        return r

    # clear

    def clear_events(self, monitor_id: int):
        return self._call('clearEvents', monitor_id)

    def clear_heartbeats(self, monitor_id: int):
        return self._call('clearHeartbeats', monitor_id)

    def clear_statistics(self):
        return self._call('clearStatistics')

    # tags

    def get_tags(self):
        return self._call('getTags')["tags"]

    def get_tag(self, id_: int):
        tags = self.get_tags()
        for tag in tags:
            if tag["id"] == id_:
                return tag
        raise UptimeKumaException("tag does not exist")

    # not working, monitor id required?
    # def edit_tag(self, id_: int, name: str, color: str):
    #     return self._call('editTag', {
    #         "id": id_,
    #         "name": name,
    #         "color": color
    #     })

    def delete_tag(self, id_: int):
        return self._call('deleteTag', id_)

    def add_tag(self, name: str, color: str):
        return self._call('addTag', {
            "name": name,
            "color": color,
            "new": True
        })["tag"]

    # settings

    def get_settings(self):
        r = self._call('getSettings')["data"]
        return r

    def set_settings(
            self,
            password: str,

            # about
            checkUpdate: bool = True,
            checkBeta: bool = False,

            # monitor history
            keepDataPeriodDays: int = 180,

            # general
            entryPage: str = "dashboard",
            searchEngineIndex: bool = False,
            primaryBaseURL: str = "",
            steamAPIKey: str = "",

            # notifications
            tlsExpiryNotifyDays: list = None,

            # security
            disableAuth: bool = False,

            # reverse proxy
            trustProxy: bool = False
    ):
        if not tlsExpiryNotifyDays:
            tlsExpiryNotifyDays = [7, 14, 21]

        data = {
            "checkUpdate": checkUpdate,
            "checkBeta": checkBeta,
            "keepDataPeriodDays": keepDataPeriodDays,
            "entryPage": entryPage,
            "searchEngineIndex": searchEngineIndex,
            "primaryBaseURL": primaryBaseURL,
            "steamAPIKey": steamAPIKey,
            "tlsExpiryNotifyDays": tlsExpiryNotifyDays,
            "disableAuth": disableAuth
        }
        if parse_version(self.version) >= parse_version("1.18"):
            data.update({
                "trustProxy": trustProxy
            })
        return self._call('setSettings', (data, password))

    def change_password(self, old_password: str, new_password: str):
        return self._call('changePassword', {
            "currentPassword": old_password,
            "newPassword": new_password,
        })

    def upload_backup(self, json_data, import_handle: str = "skip"):
        if import_handle not in ["overwrite", "skip", "keep"]:
            raise ValueError()
        return self._call('uploadBackup', (json_data, import_handle))

    # 2FA

    def twofa_status(self):
        return self._call('twoFAStatus')

    def prepare_2fa(self, password: str):
        return self._call('prepare2FA', password)

    def verify_token(self, token: str, password: str):
        return self._call('verifyToken', (token, password))

    def save_2fa(self, password: str):
        return self._call('save2FA', password)

    def disable_2fa(self, password: str):
        return self._call('disable2FA', password)

    # login

    def login(self, username: str, password: str, token: str = ""):
        return self._call('login', {
            "username": username,
            "password": password,
            "token": token
        })

    def login_by_token(self, token: str):
        return self._call('loginByToken', token)

    def logout(self):
        return self._call('logout')

    # setup

    def need_setup(self):
        return self._call('needSetup')

    def setup(self, username: str, password: str):
        return self._call("setup", (username, password))

    # database

    def get_database_size(self):
        return self._call('getDatabaseSize')

    def shrink_database(self):
        return self._call('shrinkDatabase')

    # docker host

    def get_docker_hosts(self):
        r = self._get_event_data(Event.DOCKER_HOST_LIST)
        return r

    def get_docker_host(self, id_: int):
        docker_hosts = self.get_docker_hosts()
        for docker_host in docker_hosts:
            if docker_host["id"] == id_:
                return docker_host
        raise UptimeKumaException("docker host does not exist")

    def test_docker_host(self, **kwargs):
        data = _build_docker_host_data(**kwargs)
        return self._call('testDockerHost', data)

    def add_docker_host(self, **kwargs):
        data = _build_docker_host_data(**kwargs)
        _convert_docker_host_input(data)
        return self._call('addDockerHost', (data, None))

    def edit_docker_host(self, id_: int, **kwargs):
        data = self.get_docker_host(id_)
        data.update(kwargs)
        _convert_docker_host_input(data)
        return self._call('addDockerHost', (data, id_))

    def delete_docker_host(self, id_: int):
        return self._call('deleteDockerHost', id_)
