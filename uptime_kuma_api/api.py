import datetime
import json
import random
import string
import time
from contextlib import contextmanager
from copy import deepcopy
from typing import Any

import requests
import socketio
from packaging.version import parse as parse_version

from . import AuthMethod
from . import DockerType
from . import Event
from . import IncidentStyle
from . import MaintenanceStrategy
from . import MonitorType
from . import NotificationType, notification_provider_options, notification_provider_conditions
from . import ProxyProtocol
from . import UptimeKumaException
from .docstrings import append_docstring, monitor_docstring, notification_docstring, proxy_docstring, \
    docker_host_docstring, maintenance_docstring, tag_docstring


def int_to_bool(data, keys) -> None:
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


def _convert_monitor_return(monitor) -> None:
    if type(monitor["notificationIDList"]) == dict:
        monitor["notificationIDList"] = [int(i) for i in monitor["notificationIDList"].keys()]


def _convert_monitor_input(kwargs) -> None:
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
        elif kwargs["type"] == MonitorType.MYSQL:
            kwargs["databaseConnectionString"] = "mysql://username:password@host:port/database"
        elif kwargs["type"] == MonitorType.MONGODB:
            kwargs["databaseConnectionString"] = "mongodb://username:password@host:port/database"
        elif kwargs["type"] == MonitorType.REDIS:
            kwargs["databaseConnectionString"] = "redis://user:password@host:port"

    if kwargs["type"] == MonitorType.PUSH and not kwargs.get("pushToken"):
        kwargs["pushToken"] = gen_secret(10)


def _build_notification_data(
    name: str,
    type: NotificationType,
    isDefault: bool = False,
    applyExisting: bool = False,
    **kwargs
) -> dict:
    allowed_kwargs = []
    for keys in notification_provider_options.values():
        allowed_kwargs.extend(keys)

    for key in kwargs.keys():
        if key not in allowed_kwargs:
            raise TypeError(f"unknown argument '{key}'")

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
) -> dict:
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
    googleAnalyticsId: str = None,
    customCSS: str = "",
    footerText: str = None,
    showPoweredBy: bool = True,

    icon: str = "/icon.svg",
    publicGroupList: list = None
) -> (str, dict, str, list):
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
        "googleAnalyticsId": googleAnalyticsId,
        "customCSS": customCSS,
        "footerText": footerText,
        "showPoweredBy": showPoweredBy
    }
    return slug, config, icon, publicGroupList


def _convert_docker_host_input(kwargs) -> None:
    if not kwargs["dockerDaemon"]:
        if kwargs["dockerType"] == DockerType.SOCKET:
            kwargs["dockerDaemon"] = "/var/run/docker.sock"
        elif kwargs["dockerType"] == DockerType.TCP:
            kwargs["dockerDaemon"] = "tcp://localhost:2375"


def _build_docker_host_data(
    name: str,
    dockerType: DockerType,
    dockerDaemon: str = None
) -> dict:
    data = {
        "name": name,
        "dockerType": dockerType,
        "dockerDaemon": dockerDaemon
    }
    return data


def _build_maintenance_data(
    title: str,
    strategy: MaintenanceStrategy,
    active: bool = True,
    description: str = "",
    dateRange: list = None,
    intervalDay: int = 1,
    weekdays: list = None,
    daysOfMonth: list = None,
    timeRange: list = None
) -> dict:
    if not dateRange:
        dateRange = [
            datetime.date.today().strftime("%Y-%m-%d 00:00:00")
        ]
    if not timeRange:
        timeRange = [
            {
                "hours": 2,
                "minutes": 0,
            }, {
                "hours": 3,
                "minutes": 0,
            }
        ]
    if not weekdays:
        weekdays = []
    if not daysOfMonth:
        daysOfMonth = []
    data = {
        "title": title,
        "active": active,
        "intervalDay": intervalDay,
        "dateRange": dateRange,
        "description": description,
        "strategy": strategy,
        "weekdays": weekdays,
        "daysOfMonth": daysOfMonth,
        "timeRange": timeRange
    }
    return data


def _build_tag_data(
    name: str,
    color: str
) -> dict:
    data = {
        "new": True,
        "name": name,
        "color": color
    }
    return data


def _check_missing_arguments(required_params, kwargs) -> None:
    missing_arguments = []
    for required_param in required_params:
        if kwargs.get(required_param) is None:
            missing_arguments.append(required_param)
    if missing_arguments:
        missing_arguments_str = ", ".join([f"'{i}'" for i in missing_arguments])
        raise TypeError(f"missing {len(missing_arguments)} required argument: {missing_arguments_str}")


def _check_argument_conditions(valid_params, kwargs) -> None:
    for valid_param in valid_params:
        if valid_param in kwargs:
            value = kwargs[valid_param]
            if value is None:
                continue
            conditions = valid_params[valid_param]
            min_ = conditions.get("min")
            max_ = conditions.get("max")
            if min_ is not None and value < min_:
                raise ValueError(f"the value of {valid_param} must not be less than {min_}")
            if max_ is not None and value > max_:
                raise ValueError(f"the value of {valid_param} must not be larger than {max_}")


def _check_arguments_monitor(kwargs) -> None:
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
        MonitorType.GRPC_KEYWORD: ["grpcUrl", "keyword", "grpcServiceName", "grpcMethod"],
        MonitorType.DNS: ["hostname", "dns_resolve_server", "port"],
        MonitorType.DOCKER: ["docker_container", "docker_host"],
        MonitorType.PUSH: [],
        MonitorType.STEAM: ["hostname", "port"],
        MonitorType.GAMEDIG: ["game", "hostname", "port"],
        MonitorType.MQTT: ["hostname", "port", "mqttTopic"],
        MonitorType.SQLSERVER: [],
        MonitorType.POSTGRES: [],
        MonitorType.MYSQL: [],
        MonitorType.MONGODB: [],
        MonitorType.RADIUS: ["radiusUsername", "radiusPassword", "radiusSecret", "radiusCalledStationId", "radiusCallingStationId"],
        MonitorType.REDIS: []
    }
    type_ = kwargs["type"]
    required_args = required_args_by_type[type_]
    _check_missing_arguments(required_args, kwargs)

    conditions = dict(
        interval=dict(
            min=20,
        ),
        maxretries=dict(
            min=0,
        ),
        retryInterval=dict(
            min=20,
        ),
        maxredirects=dict(
            min=0,
        ),
        port=dict(
            min=0,
            max=65535,
        ),
    )
    _check_argument_conditions(conditions, kwargs)


def _check_arguments_notification(kwargs) -> None:
    required_args = ["type", "name"]
    _check_missing_arguments(required_args, kwargs)

    # TODO: collect required notification args from /src/components/notifications/*
    # type_ = kwargs["type"]
    # required_args = notification_provider_options[type_]
    # _check_missing_arguments(required_args, kwargs)
    _check_argument_conditions(notification_provider_conditions, kwargs)


def _check_arguments_proxy(kwargs) -> None:
    required_args = ["protocol", "host", "port"]
    if kwargs.get("auth"):
        required_args.extend(["username", "password"])
    _check_missing_arguments(required_args, kwargs)

    conditions = dict(
        port=dict(
            min=0,
            max=65535,
        )
    )
    _check_argument_conditions(conditions, kwargs)


def _check_arguments_maintenance(kwargs) -> None:
    required_args = ["title", "strategy"]
    _check_missing_arguments(required_args, kwargs)

    strategy = kwargs["strategy"]
    if strategy in [MaintenanceStrategy.RECURRING_INTERVAL, MaintenanceStrategy.RECURRING_WEEKDAY, MaintenanceStrategy.RECURRING_DAY_OF_MONTH]:
        required_args = ["dateRange"]
        _check_missing_arguments(required_args, kwargs)

    conditions = dict(
        intervalDay=dict(
            min=1,
            max=3650,
        )
    )
    _check_argument_conditions(conditions, kwargs)


def _check_arguments_tag(kwargs) -> None:
    required_args = [
        "name",
        "color"
    ]
    _check_missing_arguments(required_args, kwargs)


class UptimeKumaApi(object):
    """This class is used to communicate with Uptime Kuma.

    Example::

    Import UptimeKumaApi from the library and specify the Uptime Kuma server url (e.g. 'http://127.0.0.1:3001'), username and password to initialize the connection.

        >>> from uptime_kuma_api import UptimeKumaApi
        >>> api = UptimeKumaApi('INSERT_URL')
        >>> api.login('INSERT_USERNAME', 'INSERT_PASSWORD')

    Now you can call one of the existing methods of the instance. For example create a new monitor:

        >>> api.add_monitor(
        ...     type=MonitorType.HTTP,
        ...     name="Google",
        ...     url="https://google.com"
        ... )
        {
            'msg': 'Added Successfully.',
            'monitorId': 1
        }

    At the end, the connection to the API must be disconnected so that the program does not block.

        >>> api.disconnect()

    :param str url: The url to the Uptime Kuma instance. For example ``http://127.0.0.1:3001``
    :param float wait_timeout: How many seconds the client should wait for the connection., defaults to 1
    :raises UptimeKumaException: When connection to server failed.
    """
    def __init__(
            self,
            url: str,
            wait_timeout: float = 1
    ) -> None:
        self.url = url
        self.wait_timeout = wait_timeout
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
            Event.DOCKER_HOST_LIST: None,
            Event.AUTO_LOGIN: None,
            Event.MAINTENANCE_LIST: None,
            Event.API_KEY_LIST: None
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
        self.sio.on(Event.AUTO_LOGIN, self._event_auto_login)
        self.sio.on(Event.INIT_SERVER_TIMEZONE, self._event_init_server_timezone)
        self.sio.on(Event.MAINTENANCE_LIST, self._event_maintenance_list)
        self.sio.on(Event.API_KEY_LIST, self._event_api_key_list)

        self.connect()

    @contextmanager
    def wait_for_event(self, event: Event) -> None:
        retries = 200
        event_data_before = deepcopy(self._event_data)

        try:
            yield
        except:
            raise
        else:
            counter = 0
            while event_data_before[event] == self._event_data[event]:
                time.sleep(0.01)
                counter += 1
                if counter >= retries:
                    print("wait_for_event timeout")
                    break

    def _get_event_data(self, event) -> Any:
        monitor_events = [Event.AVG_PING, Event.UPTIME, Event.HEARTBEAT_LIST, Event.IMPORTANT_HEARTBEAT_LIST, Event.CERT_INFO, Event.HEARTBEAT]
        while self._event_data[event] is None:
            # do not wait for events that are not sent
            if self._event_data[Event.MONITOR_LIST] == {} and event in monitor_events:
                return []
            time.sleep(0.01)
        time.sleep(0.05)  # wait for multiple messages
        return deepcopy(self._event_data[event].copy())

    def _call(self, event, data=None) -> Any:
        r = self.sio.call(event, data)
        if type(r) == dict and "ok" in r:
            if not r["ok"]:
                raise UptimeKumaException(r["msg"])
            r.pop("ok")
        return r

    # event handlers

    def _event_connect(self) -> None:
        pass

    def _event_disconnect(self) -> None:
        pass

    def _event_monitor_list(self, data) -> None:
        self._event_data[Event.MONITOR_LIST] = data

    def _event_notification_list(self, data) -> None:
        self._event_data[Event.NOTIFICATION_LIST] = data

    def _event_proxy_list(self, data) -> None:
        self._event_data[Event.PROXY_LIST] = data

    def _event_status_page_list(self, data) -> None:
        self._event_data[Event.STATUS_PAGE_LIST] = data

    def _event_heartbeat_list(self, monitor_id, data, overwrite) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.HEARTBEAT_LIST] is None:
            self._event_data[Event.HEARTBEAT_LIST] = {}
        if monitor_id not in self._event_data[Event.HEARTBEAT_LIST] or overwrite:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id] = data
        else:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id].append(data)

    def _event_important_heartbeat_list(self, monitor_id, data, overwrite) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = {}
        if monitor_id not in self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] or overwrite:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = data
        else:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id].append(data)

    def _event_avg_ping(self, monitor_id, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.AVG_PING] is None:
            self._event_data[Event.AVG_PING] = {}
        self._event_data[Event.AVG_PING][monitor_id] = data

    def _event_uptime(self, monitor_id, type_, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.UPTIME] is None:
            self._event_data[Event.UPTIME] = {}
        if monitor_id not in self._event_data[Event.UPTIME]:
            self._event_data[Event.UPTIME][monitor_id] = {}
        self._event_data[Event.UPTIME][monitor_id][type_] = data

    def _event_heartbeat(self, data) -> None:
        if self._event_data[Event.HEARTBEAT] is None:
            self._event_data[Event.HEARTBEAT] = {}
        monitor_id = data["monitorID"]
        if monitor_id not in self._event_data[Event.HEARTBEAT]:
            self._event_data[Event.HEARTBEAT][monitor_id] = []
        self._event_data[Event.HEARTBEAT][monitor_id].append(data)
        if len(self._event_data[Event.HEARTBEAT][monitor_id]) >= 150:
            self._event_data[Event.HEARTBEAT][monitor_id].pop(0)

        # add heartbeat to important heartbeat list
        if data["important"]:
            if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
                self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = {}
            if monitor_id not in self._event_data[Event.IMPORTANT_HEARTBEAT_LIST]:
                self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = []
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = [data] + self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id]

    def _event_info(self, data) -> None:
        self._event_data[Event.INFO] = data

    def _event_cert_info(self, monitor_id, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.CERT_INFO] is None:
            self._event_data[Event.CERT_INFO] = {}
        self._event_data[Event.CERT_INFO][monitor_id] = json.loads(data)

    def _event_docker_host_list(self, data) -> None:
        self._event_data[Event.DOCKER_HOST_LIST] = data

    def _event_auto_login(self) -> None:
        self._event_data[Event.AUTO_LOGIN] = True

    def _event_init_server_timezone(self) -> None:
        pass

    def _event_maintenance_list(self, data) -> None:
        self._event_data[Event.MAINTENANCE_LIST] = data

    def _event_api_key_list(self, data) -> None:
        self._event_data[Event.API_KEY_LIST] = data

    # connection

    def connect(self) -> None:
        """
        Connects to Uptime Kuma.

        Called automatically when the UptimeKumaApi instance is created.

        :raises UptimeKumaException: When connection to server failed.
        """
        url = self.url.rstrip("/")
        try:
            self.sio.connect(f'{url}/socket.io/', wait_timeout=self.wait_timeout)
        except:
            raise UptimeKumaException("unable to connect")

    def disconnect(self) -> None:
        """
        Disconnects from Uptime Kuma.

        Needs to be called to prevent blocking the program.
        """
        self.sio.disconnect()

    # builder

    @property
    def version(self) -> str:
        info = self.info()
        return info["version"]

    def _build_monitor_data(
            self,
            type: MonitorType,
            name: str,
            description: str = None,
            interval: int = 60,
            retryInterval: int = 60,
            resendInterval: int = 0,
            maxretries: int = 0,
            upsideDown: bool = False,
            notificationIDList: list = None,
            httpBodyEncoding: str = "json",

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
            tlsCert: str = None,
            tlsKey: str = None,
            tlsCa: str = None,
            basic_auth_user: str = None,
            basic_auth_pass: str = None,
            authDomain: str = None,
            authWorkstation: str = None,

            # KEYWORD
            keyword: str = None,

            # GRPC_KEYWORD
            grpcUrl: str = None,
            grpcEnableTls: bool = False,
            grpcServiceName: str = None,
            grpcMethod: str = None,
            grpcProtobuf: str = None,
            grpcBody: str = None,
            grpcMetadata: str = None,

            # DNS, PING, STEAM, MQTT
            hostname: str = None,

            # PING
            packetSize: int = 56,

            # DNS, STEAM, MQTT, RADIUS
            port: int = None,

            # DNS
            dns_resolve_server: str = "1.1.1.1",
            dns_resolve_type: str = "A",

            # MQTT
            mqttUsername: str = None,
            mqttPassword: str = None,
            mqttTopic: str = None,
            mqttSuccessMessage: str = None,

            # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
            databaseConnectionString: str = None,

            # SQLSERVER, POSTGRES, MYSQL
            databaseQuery: str = None,

            # DOCKER
            docker_container: str = "",
            docker_host: int = None,

            # RADIUS
            radiusUsername: str = None,
            radiusPassword: str = None,
            radiusSecret: str = None,
            radiusCalledStationId: str = None,
            radiusCallingStationId: str = None,

            # GAMEDIG
            game: str = None
    ) -> dict:
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

        if parse_version(self.version) >= parse_version("1.21"):
            data.update({
                "description": description,
                "httpBodyEncoding": httpBodyEncoding
            })

        if type in [MonitorType.KEYWORD, MonitorType.GRPC_KEYWORD]:
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

        if authMethod == AuthMethod.MTLS:
            data.update({
                "tlsCert": tlsCert,
                "tlsKey": tlsKey,
                "tlsCa": tlsCa,
            })

        # GRPC_KEYWORD
        if type == MonitorType.GRPC_KEYWORD:
            data.update({
                "grpcUrl": grpcUrl,
                "grpcEnableTls": grpcEnableTls,
                "grpcServiceName": grpcServiceName,
                "grpcMethod": grpcMethod,
                "grpcProtobuf": grpcProtobuf,
                "grpcBody": grpcBody,
                "grpcMetadata": grpcMetadata,
            })

        # PORT, PING, DNS, STEAM, MQTT
        data.update({
            "hostname": hostname,
        })

        # PING
        if parse_version(self.version) >= parse_version("1.20"):
            data.update({
                "packetSize": packetSize,
            })

        # PORT, DNS, STEAM, MQTT, RADIUS
        if not port:
            if type == MonitorType.DNS:
                port = 53
            elif type == MonitorType.RADIUS:
                port = 1812
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

        # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
        data.update({
            "databaseConnectionString": databaseConnectionString
        })

        # SQLSERVER, POSTGRES, MYSQL
        if type in [MonitorType.SQLSERVER, MonitorType.POSTGRES, MonitorType.MYSQL]:
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

        # GAMEDIG
        if type == MonitorType.GAMEDIG:
            data.update({
                "game": game
            })

        return data

    # monitor

    def get_monitors(self) -> list:
        """
        Get all monitors.

        :return: A list of monitors.
        :rtype: list

        Example::

            >>> api.get_monitors()
            [
                {
                    'accepted_statuscodes': ['200-299'],
                    'active': True,
                    'authDomain': None,
                    'authMethod': '',
                    'authWorkstation': None,
                    'basic_auth_pass': None,
                    'basic_auth_user': None,
                    'body': None,
                    'databaseConnectionString': None,
                    'databaseQuery': None,
                    'dns_last_result': None,
                    'dns_resolve_server': '1.1.1.1',
                    'dns_resolve_type': 'A',
                    'docker_container': None,
                    'docker_host': None,
                    'expiryNotification': False,
                    'game': None,
                    'grpcBody': None,
                    'grpcEnableTls': False,
                    'grpcMetadata': None,
                    'grpcMethod': None,
                    'grpcProtobuf': None,
                    'grpcServiceName': None,
                    'grpcUrl': None,
                    'headers': None,
                    'hostname': None,
                    'id': 1,
                    'ignoreTls': False,
                    'includeSensitiveData': True,
                    'interval': 60,
                    'keyword': None,
                    'maintenance': False,
                    'maxredirects': 10,
                    'maxretries': 0,
                    'method': 'GET',
                    'mqttPassword': None,
                    'mqttSuccessMessage': None,
                    'mqttTopic': None,
                    'mqttUsername': None,
                    'name': 'monitor 1',
                    'notificationIDList': [1, 2],
                    'packetSize': 56,
                    'port': None,
                    'proxyId': None,
                    'pushToken': None,
                    'radiusCalledStationId': None,
                    'radiusCallingStationId': None,
                    'radiusPassword': None,
                    'radiusSecret': None,
                    'radiusUsername': None,
                    'resendInterval': 0,
                    'retryInterval': 60,
                    'tags': [],
                    'type': 'http',
                    'upsideDown': False,
                    'url': 'http://127.0.0.1',
                    'weight': 2000
                }
            ]
        """

        # TODO: replace with getMonitorList?

        r = list(self._get_event_data(Event.MONITOR_LIST).values())
        for monitor in r:
            _convert_monitor_return(monitor)
        int_to_bool(r, ["active"])
        return r

    def get_monitor(self, id_: int) -> dict:
        """
        Get a monitor.

        :param int id_: The monitor id.
        :return: The monitor.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor(1)
            {
                'accepted_statuscodes': ['200-299'],
                'active': True,
                'authDomain': None,
                'authMethod': '',
                'authWorkstation': None,
                'basic_auth_pass': None,
                'basic_auth_user': None,
                'body': None,
                'databaseConnectionString': None,
                'databaseQuery': None,
                'dns_last_result': None,
                'dns_resolve_server': '1.1.1.1',
                'dns_resolve_type': 'A',
                'docker_container': None,
                'docker_host': None,
                'expiryNotification': False,
                'game': None,
                'grpcBody': None,
                'grpcEnableTls': False,
                'grpcMetadata': None,
                'grpcMethod': None,
                'grpcProtobuf': None,
                'grpcServiceName': None,
                'grpcUrl': None,
                'headers': None,
                'hostname': None,
                'id': 1,
                'ignoreTls': False,
                'includeSensitiveData': True,
                'interval': 60,
                'keyword': None,
                'maintenance': False,
                'maxredirects': 10,
                'maxretries': 0,
                'method': 'GET',
                'mqttPassword': None,
                'mqttSuccessMessage': None,
                'mqttTopic': None,
                'mqttUsername': None,
                'name': 'monitor 1',
                'notificationIDList': [1, 2],
                'packetSize': 56,
                'port': None,
                'proxyId': None,
                'pushToken': None,
                'radiusCalledStationId': None,
                'radiusCallingStationId': None,
                'radiusPassword': None,
                'radiusSecret': None,
                'radiusUsername': None,
                'resendInterval': 0,
                'retryInterval': 60,
                'tags': [],
                'type': 'http',
                'upsideDown': False,
                'url': 'http://127.0.0.1',
                'weight': 2000
            }
        """
        r = self._call('getMonitor', id_)["monitor"]
        _convert_monitor_return(r)
        int_to_bool(r, ["active"])
        return r

    def pause_monitor(self, id_: int) -> dict:
        """
        Pauses a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.pause_monitor(1)
            {
                'msg': 'Paused Successfully.'
            }
        """
        return self._call('pauseMonitor', id_)

    def resume_monitor(self, id_: int) -> dict:
        """
        Resumes a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.resume_monitor(1)
            {
                'msg': 'Resumed Successfully.'
            }
        """
        return self._call('resumeMonitor', id_)

    def delete_monitor(self, id_: int) -> dict:
        """
        Deletes a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_monitor(1)
            {
                'msg': 'Deleted Successfully.'
            }
        """
        with self.wait_for_event(Event.MONITOR_LIST):
            return self._call('deleteMonitor', id_)

    def get_monitor_beats(self, id_: int, hours: int) -> list:
        """
        Get monitor beats for a specific monitor in a time range.

        :param int id_: The monitor id.
        :param int hours: Period time in hours from now.
        :return: The server response.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor_beats(1, 6)
            [
                {
                    'down_count': 0,
                    'duration': 0,
                    'id': 25,
                    'important': True,
                    'monitor_id': 1,
                    'msg': '200 - OK',
                    'ping': 201,
                    'status': True,
                    'time': '2022-12-15 12:38:42.661'
                },
                {
                    'down_count': 0,
                    'duration': 60,
                    'id': 26,
                    'important': False,
                    'monitor_id': 1,
                    'msg': '200 - OK',
                    'ping': 193,
                    'status': True,
                    'time': '2022-12-15 12:39:42.878'
                },
                ...
            ]
        """
        r = self._call('getMonitorBeats', (id_, hours))["data"]
        int_to_bool(r, ["important", "status"])
        return r

    def get_game_list(self) -> list:
        """
        Get a list of games that are supported by the GameDig monitor type.

        :return: The server response.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_game_list()
            [
                {
                    'extra': {},
                    'keys': ['7d2d'],
                    'options': {
                        'port': 26900,
                        'port_query_offset': 1,
                        'protocol': 'valve'
                    },
                    'pretty': '7 Days to Die (2013)'
                },
                {
                    'extra': {},
                    'keys': ['arma2'],
                    'options': {
                        'port': 2302,
                        'port_query_offset': 1,
                        'protocol': 'valve'
                    },
                    'pretty': 'ARMA 2 (2009)'
                },
                ...
            ]
        """
        r = self._call('getGameList')
        # Workaround, gamelist is not available on first call.
        # Fixed in https://github.com/louislam/uptime-kuma/commit/7b8ed01f272fc4c6b69ff6299185e936a5e63735
        # Exists in 1.20.0 - 1.21.0
        if not r:
            r = self._call('getGameList')
        return r["gameList"]

    @append_docstring(monitor_docstring("add"))
    def add_monitor(self, **kwargs) -> dict:
        """
        Adds a new monitor.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_monitor(
            ...     type=MonitorType.HTTP,
            ...     name="Google",
            ...     url="https://google.com"
            ... )
            {
                'msg': 'Added Successfully.',
                'monitorID': 1
            }
        """
        data = self._build_monitor_data(**kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        with self.wait_for_event(Event.MONITOR_LIST):
            return self._call('add', data)

    @append_docstring(monitor_docstring("edit"))
    def edit_monitor(self, id_: int, **kwargs) -> dict:
        """
        Edits an existing monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_monitor(1,
            ...     interval=20
            ... )
            {
                'monitorID': 1,
                'msg': 'Saved.'
            }
        """
        data = self.get_monitor(id_)
        data.update(kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        with self.wait_for_event(Event.MONITOR_LIST):
            return self._call('editMonitor', data)

    # monitor tags

    def add_monitor_tag(self, tag_id: int, monitor_id: int, value: str = "") -> dict:
        """
        Add a tag to a monitor.

        :param int tag_id: Id of the tag.
        :param int monitor_id: Id of the monitor to add the tag to.
        :param str, optional value: Value of the tag., defaults to ""
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_monitor_tag(
            ...     tag_id=1,
            ...     monitor_id=1,
            ...     value="test"
            ... )
            {
                'msg': 'Added Successfully.'
            }
        """
        r = self._call('addMonitorTag', (tag_id, monitor_id, value))
        # the monitor list event does not send the updated tags
        self._event_data[Event.MONITOR_LIST][str(monitor_id)] = self.get_monitor(monitor_id)
        return r

    # editMonitorTag is unused in uptime-kuma
    # def edit_monitor_tag(self, tag_id: int, monitor_id: int, value=""):
    #     return self._call('editMonitorTag', (tag_id, monitor_id, value))

    def delete_monitor_tag(self, tag_id: int, monitor_id: int, value: str = "") -> dict:
        """
        Delete a tag from a monitor.

        :param int tag_id: Id of the tag to remove.
        :param int monitor_id: Id of monitor to remove the tag from.
        :param str, optional value: Value of the tag., defaults to ""
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_monitor_tag(
            ...     tag_id=1,
            ...     monitor_id=1,
            ...     value="test"
            ... )
            {
                'msg': 'Deleted Successfully.'
            }
        """
        r = self._call('deleteMonitorTag', (tag_id, monitor_id, value))
        # the monitor list event does not send the updated tags
        self._event_data[Event.MONITOR_LIST][str(monitor_id)] = self.get_monitor(monitor_id)
        return r

    # notification

    def get_notifications(self) -> list:
        """
        Get all notifications.

        :return: All notifications.
        :rtype: list

        Example::

            >>> api.get_notifications()
            [
                {
                    'active': True,
                    'applyExisting': True,
                    'id': 1,
                    'isDefault': True,
                    'name': 'notification 1',
                    'pushAPIKey': '123456789',
                    'type': 'PushByTechulus',
                    'userId': 1
                }
            ]
        """
        notifications = self._get_event_data(Event.NOTIFICATION_LIST)
        r = []
        for notification_raw in notifications:
            notification = notification_raw.copy()
            config = json.loads(notification["config"])
            del notification["config"]
            notification.update(config)
            r.append(notification)
        return r

    def get_notification(self, id_: int) -> dict:
        """
        Get a notification.

        :param int id_: Id of the notification to get.
        :return: The notification.
        :rtype: dict
        :raises UptimeKumaException: If the notification does not exist.

        Example::

            >>> api.get_notification(1)
            {
                'active': True,
                'applyExisting': True,
                'id': 1,
                'isDefault': True,
                'name': 'notification 1',
                'pushAPIKey': '123456789',
                'type': 'PushByTechulus',
                'userId': 1
            }
        """
        notifications = self.get_notifications()
        for notification in notifications:
            if notification["id"] == id_:
                return notification
        raise UptimeKumaException("notification does not exist")

    @append_docstring(notification_docstring("test"))
    def test_notification(self, **kwargs) -> dict:
        """
        Test a notification.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.test_notification(
            ...     name="notification 1",
            ...     isDefault=True,
            ...     applyExisting=True,
            ...     type=NotificationType.PUSHBYTECHULUS,
            ...     pushAPIKey="INSERT_PUSH_API_KEY"
            ... )
            {
                'ok': True,
                'msg': 'Sent Successfully.'
            }
        """
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        return self._call('testNotification', data)

    @append_docstring(notification_docstring("add"))
    def add_notification(self, **kwargs) -> dict:
        """
        Add a notification.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_notification(
            ...     name="notification 1",
            ...     isDefault=True,
            ...     applyExisting=True,
            ...     type=NotificationType.PUSHBYTECHULUS,
            ...     pushAPIKey="123456789"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        with self.wait_for_event(Event.NOTIFICATION_LIST):
            return self._call('addNotification', (data, None))

    @append_docstring(notification_docstring("edit"))
    def edit_notification(self, id_: int, **kwargs) -> dict:
        """
        Edit a notification.

        :param int id_: Id of the notification to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_notification(1,
            ...     name="notification 1 edited",
            ...     isDefault=False,
            ...     applyExisting=False,
            ...     type=NotificationType.PUSHDEER,
            ...     pushdeerKey="987654321"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
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
        with self.wait_for_event(Event.NOTIFICATION_LIST):
            return self._call('addNotification', (notification, id_))

    def delete_notification(self, id_: int) -> dict:
        """
        Delete a notification.

        :param int id_: Id of the notification to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_notification(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.NOTIFICATION_LIST):
            return self._call('deleteNotification', id_)

    def check_apprise(self) -> bool:
        """
        Check if apprise exists.

        :return: The server response.
        :rtype: bool
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.check_apprise()
            True
        """
        return self._call('checkApprise')

    # proxy

    def get_proxies(self) -> list:
        """
        Get all proxies.

        :return: All proxies.
        :rtype: list

        Example::

            >>> api.get_proxies()
            [
                {
                    'active': True,
                    'auth': True,
                    'createdDate': '2022-12-15 16:24:24',
                    'default': False,
                    'host': '127.0.0.1',
                    'id': 1,
                    'password': 'password',
                    'port': 8080,
                    'protocol': 'http',
                    'userId': 1,
                    'username': 'username'
                }
            ]
        """
        r = self._get_event_data(Event.PROXY_LIST)
        int_to_bool(r, ["auth", "active", "default", "applyExisting"])
        return r

    def get_proxy(self, id_: int) -> dict:
        """
        Get a proxy.

        :param int id_: Id of the proxy to get.
        :return: The proxy.
        :rtype: dict
        :raises UptimeKumaException: If the proxy does not exist.

        Example::

            >>> api.get_proxy(1)
            {
                'active': True,
                'auth': True,
                'createdDate': '2022-12-15 16:24:24',
                'default': False,
                'host': '127.0.0.1',
                'id': 1,
                'password': 'password',
                'port': 8080,
                'protocol': 'http',
                'userId': 1,
                'username': 'username'
            }
        """
        proxies = self.get_proxies()
        for proxy in proxies:
            if proxy["id"] == id_:
                return proxy
        raise UptimeKumaException("proxy does not exist")

    @append_docstring(proxy_docstring("add"))
    def add_proxy(self, **kwargs) -> dict:
        """
        Add a proxy.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_proxy(
            ...     protocol=ProxyProtocol.HTTP,
            ...     host="127.0.0.1",
            ...     port=8080,
            ...     auth=True,
            ...     username="username",
            ...     password="password",
            ...     active=True,
            ...     default=False,
            ...     applyExisting=False
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_proxy_data(**kwargs)

        _check_arguments_proxy(data)
        with self.wait_for_event(Event.PROXY_LIST):
            return self._call('addProxy', (data, None))

    @append_docstring(proxy_docstring("edit"))
    def edit_proxy(self, id_: int, **kwargs) -> dict:
        """
        Edit a proxy.

        :param int id_: Id of the proxy to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_proxy(1,
            ...     protocol=ProxyProtocol.HTTPS,
            ...     host="127.0.0.2",
            ...     port=8888
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        proxy = self.get_proxy(id_)
        proxy.update(kwargs)
        _check_arguments_proxy(proxy)
        with self.wait_for_event(Event.PROXY_LIST):
            return self._call('addProxy', (proxy, id_))

    def delete_proxy(self, id_: int) -> dict:
        """
        Delete a proxy.

        :param int id_: Id of the proxy to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_proxy(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.PROXY_LIST):
            return self._call('deleteProxy', id_)

    # status page

    def get_status_pages(self) -> list:
        """
        Get all status pages.

        :return: All status pages.
        :rtype: list

        Example::

            >>> api.get_status_pages()
            [
                {
                    'customCSS': '',
                    'description': 'description 1',
                    'domainNameList': [],
                    'footerText': None,
                    'icon': '/icon.svg',
                    'googleAnalyticsId': '',
                    'id': 1,
                    'published': True,
                    'showPoweredBy': False,
                    'showTags': False,
                    'slug': 'slug1',
                    'theme': 'light',
                    'title': 'status page 1'
                }
            ]
        """
        return list(self._get_event_data(Event.STATUS_PAGE_LIST).values())

    def get_status_page(self, slug: str) -> dict:
        """
        Get a status page.

        :param str slug: Slug
        :return: The status page.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_status_page("slug1")
            {
                'customCSS': '',
                'description': 'description 1',
                'domainNameList': [],
                'footerText': None,
                'icon': '/icon.svg',
                'googleAnalyticsId': '',
                'id': 1,
                'incident': {
                    'content': 'content 1',
                    'createdDate': '2022-12-15 16:51:43',
                    'id': 1,
                    'lastUpdatedDate': None,
                    'pin': 1,
                    'style': 'danger',
                    'title': 'title 1'
                },
                'maintenanceList': [],
                'publicGroupList': [
                    {
                        'id': 1,
                        'monitorList': [
                            {
                                'id': 1,
                                'maintenance': False,
                                'name': 'monitor 1',
                                'sendUrl': 0
                            }
                        ],
                        'name': 'Services',
                        'weight': 1
                    }
                ],
                'published': True,
                'showPoweredBy': False,
                'showTags': False,
                'slug': 'slug1',
                'theme': 'light',
                'title': 'status page 1'
            }
        """
        r1 = self._call('getStatusPage', slug)
        r2 = requests.get(f"{self.url}/api/status-page/{slug}").json()

        config = r1["config"]
        config.update(r2["config"])

        data = {
            **config,
            "incident": r2["incident"],
            "publicGroupList": r2["publicGroupList"],
        }
        if parse_version(self.version) >= parse_version("1.19"):
            data.update({
                "maintenanceList": r2["maintenanceList"]
            })
        return data

    def add_status_page(self, slug: str, title: str) -> dict:
        """
        Add a status page.

        :param str slug: Slug
        :param str title: Title
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_status_page("slug1", "status page 1")
            {
                'msg': 'OK!'
            }
        """
        with self.wait_for_event(Event.STATUS_PAGE_LIST):
            return self._call('addStatusPage', (title, slug))

    def delete_status_page(self, slug: str) -> dict:
        """
        Delete a status page.

        :param str slug: Slug
        :return: The server response.
        :rtype: dict

        Example::

            >>> api.delete_status_page("slug1")
            {}
        """
        r = self._call('deleteStatusPage', slug)

        # uptime kuma does not send the status page list event when a status page is deleted
        for status_page in self._event_data[Event.STATUS_PAGE_LIST].values():
            if status_page["slug"] == slug:
                status_page_id = status_page["id"]
                del self._event_data[Event.STATUS_PAGE_LIST][str(status_page_id)]
                break

        return r

    def save_status_page(self, slug: str, **kwargs) -> dict:
        """
        Save a status page.

        :param str slug: Slug
        :param int id: Id of the status page to save
        :param str title: Title
        :param str, optional description: Description, defaults to None
        :param str, optional theme: Switch Theme, defaults to "light"
        :param bool, optional published: Published, defaults to True
        :param bool, optional showTags: Show Tags, defaults to False
        :param list, optional domainNameList: Domain Names, defaults to None
        :param str, optional googleAnalyticsId: Google Analytics ID, defaults to None
        :param str, optional customCSS: Custom CSS, defaults to ""
        :param str, optional footerText: Custom Footer, defaults to None
        :param bool, optional showPoweredBy: Show Powered By, defaults to True
        :param str, optional icon: Icon, defaults to "/icon.svg"
        :param list, optional publicGroupList: Public Group List, defaults to None
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> monitor_id = 1
            >>> api.save_status_page(
            ...     slug="slug1",
            ...     title="status page 1",
            ...     description="description 1",
            ...     publicGroupList=[
            ...         {
            ...             'name': 'Services',
            ...             'weight': 1,
            ...             'monitorList': [
            ...                 {
            ...                     "id": monitor_id
            ...                 }
            ...             ]
            ...         }
            ...     ]
            ... )
            {
                'publicGroupList': [
                    {
                        'id': 1,
                        'monitorList': [
                            {
                                'id': 1
                            }
                        ],
                        'name': 'Services',
                        'weight': 1
                    }
                ]
            }
        """
        status_page = self.get_status_page(slug)
        status_page.pop("incident")
        if parse_version(self.version) >= parse_version("1.19"):
            status_page.pop("maintenanceList")
        status_page.update(kwargs)
        data = _build_status_page_data(**status_page)
        r = self._call('saveStatusPage', data)

        # uptime kuma does not send the status page list event when a status page is saved
        status_page = self._call('getStatusPage', slug)["config"]
        status_page_id = status_page["id"]
        if self._event_data[Event.STATUS_PAGE_LIST] is None:
            self._event_data[Event.STATUS_PAGE_LIST] = {}
        self._event_data[Event.STATUS_PAGE_LIST][str(status_page_id)] = status_page

        return r

    def post_incident(
            self,
            slug: str,
            title: str,
            content: str,
            style: IncidentStyle = IncidentStyle.PRIMARY
    ) -> dict:
        """
        Post an incident to status page.

        :param str slug: Slug
        :param str title: Title
        :param str content: Content
        :param IncidentStyle, optional style: Style, defaults to :attr:`~.IncidentStyle.PRIMARY`
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.post_incident(
            ...     slug="slug1",
            ...     title="title 1",
            ...     content="content 1",
            ...     style=IncidentStyle.DANGER
            ... )
            {
                'content': 'content 1',
                'createdDate': '2022-12-15 16:51:43',
                'id': 1,
                'pin': True,
                'style': 'danger',
                'title': 'title 1'
            }
        """
        incident = {
            "title": title,
            "content": content,
            "style": style
        }
        r = self._call('postIncident', (slug, incident))["incident"]
        self.save_status_page(slug)
        return r

    def unpin_incident(self, slug: str) -> dict:
        """
        Unpin an incident from a status page.

        :param str slug: Slug
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.unpin_incident(slug="slug1")
            {}
        """
        r = self._call('unpinIncident', slug)
        self.save_status_page(slug)
        return r

    # heartbeat

    def get_heartbeats(self) -> dict:
        """
        Get heartbeats.

        :return: The heartbeats for each monitor id.
        :rtype: dict

        Example::

            >>> api.get_heartbeats()
            {
                1: [
                    {
                        'down_count': 0,
                        'duration': 0,
                        'id': 1,
                        'important': True,
                        'monitor_id': 1,
                        'msg': '',
                        'ping': 10.5,
                        'status': True,
                        'time': '2023-05-01 17:22:20.289'
                    },
                    {
                        'down_count': 0,
                        'duration': 60,
                        'id': 2,
                        'important': False,
                        'monitor_id': 1,
                        'msg': '',
                        'ping': 10.7,
                        'status': True,
                        'time': '2023-05-01 17:23:20.349'
                    }
                ]
            }
        """
        r = self._get_event_data(Event.HEARTBEAT_LIST)
        for i in r:
            int_to_bool(r[i], ["important", "status"])
        return r

    def get_important_heartbeats(self) -> dict:
        """
        Get important heartbeats.

        :return: The important heartbeats for each monitor id.
        :rtype: dict

        Example::

            >>> api.get_important_heartbeats()
            {
                1: [
                    {
                        'duration': 0,
                        'important': True,
                        'monitorID': 1,
                        'msg': '',
                        'ping': 10.5,
                        'status': True,
                        'time': '2023-05-01 17:22:20.289'
                    }
                ]
            }
        """
        r = self._get_event_data(Event.IMPORTANT_HEARTBEAT_LIST)
        for i in r:
            int_to_bool(r[i], ["important", "status"])
        return r

    def get_heartbeat(self) -> dict:
        """
        Get the next heartbeat.

        :return: The next heartbeat.
        :rtype: dict

        Example::

            >>> api.get_heartbeat()
            {
                1: [
                    {
                        'duration': 60,
                        'important': False,
                        'monitorID': 1,
                        'msg': '',
                        'ping': 10.6,
                        'status': 1,
                        'time': '2023-05-01 17:28:20.557'
                    }
                ]
            }
        """
        r = self._get_event_data(Event.HEARTBEAT)
        int_to_bool(r, ["important", "status"])
        return r

    # avg ping

    def avg_ping(self) -> dict:
        """
        Get average ping.

        :return: The average ping for each monitor id.
        :rtype: dict

        Example::

            >>> api.avg_ping()
            {
                1: 10
            }
        """
        return self._get_event_data(Event.AVG_PING)

    # cert info

    def cert_info(self) -> dict:
        """
        Get certificate info.

        :return: Certificate info for each monitor id for which a certificate can be extracted.
        :rtype: dict

        Example::

            >>> api.cert_info()
            {
                1: {
                    'valid': True,
                    'certInfo': {
                        'subject': {
                            'CN': 'www.google.de'
                        },
                        'issuer': {
                            'C': 'US',
                            'O': 'Google Trust Services LLC',
                            'CN': 'GTS CA 1C3'
                        },
                        'subjectaltname': 'DNS:www.google.de',
                        'infoAccess': {
                            'OCSP - URI': ['http://ocsp.pki.goog/gts1c3'],
                            'CA Issuers - URI': ['http://pki.goog/repo/certs/gts1c3.der']
                        },
                        'bits': 256,
                        'pubkey': {
                            'type': 'Buffer',
                            'data': [4, 190, 87, 79, 99, 19, 100, 17, 253, 234, 34, 246, 7, 67, 197, 31, 168, 108, 212, 254, 170, 117, 68, 29, 16, 77, 78, 77, 152, 134, 139, 31, 187, 247, 140, 225, 130, 116, 249, 151, 31, 253, 69, 170, 182, 76, 191, 163, 96, 92, 127, 202, 159, 216, 189, 117, 255, 80, 18, 210, 77, 234, 108, 50, 109]
                        },
                        'asn1Curve': 'prime256v1',
                        'nistCurve': 'P-256',
                        'valid_from': 'Apr  3 08:24:23 2023 GMT',
                        'valid_to': 'Jun 26 08:24:22 2023 GMT',
                        'fingerprint': '45:B2:16:8F:B0:00:25:31:17:D1:DA:F2:66:DE:F6:51:6D:4E:51:E2',
                        'fingerprint256': '5E:77:02:E0:DE:28:33:5E:FB:D4:70:62:D3:21:B1:EE:AB:80:99:E0:92:D5:87:44:ED:C8:D6:8C:E6:67:3D:A8',
                        'fingerprint512': '35:D5:F8:24:BD:20:06:B1:00:19:FA:82:73:53:5A:53:F8:1F:D6:51:29:DF:17:2E:E6:72:8E:42:10:68:1B:E4:58:EB:0E:3A:48:4C:5D:78:12:69:B8:29:AA:95:0C:DB:79:AC:04:84:D8:53:74:F4:BB:0E:B3:80:D1:36:70:51',
                        'ext_key_usage': ['1.3.6.1.5.5.7.3.1'],
                        'serialNumber': '8628F43381B42BA50A686F0ACB522E40',
                        'raw': {
                            'type': 'Buffer',
                            'data': [48, 130, 4, 136, 48, 130, 3, 112, 160, 3, 2, 1, 2, 2, 17, 0, 134, 40, 244, 51, 129, 180, 43, 165, 10, 104, 111, 10, 203, 82, 46, 64, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 48, 70, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 85, 83, 49, 34, 48, 32, 6, 3, 85, 4, 10, 19, 25, 71, 111, 111, 103, 108, 101, 32, 84, 114, 117, 115, 116, 32, 83, 101, 114, 118, 105, 99, 101, 115, 32, 76, 76, 67, 49, 19, 48, 17, 6, 3, 85, 4, 3, 19, 10, 71, 84, 83, 32, 67, 65, 32, 49, 67, 51, 48, 30, 23, 13, 50, 51, 48, 52, 48, 51, 48, 56, 50, 52, 50, 51, 90, 23, 13, 50, 51, 48, 54, 50, 54, 48, 56, 50, 52, 50, 50, 90, 48, 24, 49, 22, 48, 20, 6, 3, 85, 4, 3, 19, 13, 119, 119, 119, 46, 103, 111, 111, 103, 108, 101, 46, 100, 101, 48, 89, 48, 19, 6, 7, 42, 134, 72, 206, 61, 2, 1, 6, 8, 42, 134, 72, 206, 61, 3, 1, 7, 3, 66, 0, 4, 190, 87, 79, 99, 19, 100, 17, 253, 234, 34, 246, 7, 67, 197, 31, 168, 108, 212, 254, 170, 117, 68, 29, 16, 77, 78, 77, 152, 134, 139, 31, 187, 247, 140, 225, 130, 116, 249, 151, 31, 253, 69, 170, 182, 76, 191, 163, 96, 92, 127, 202, 159, 216, 189, 117, 255, 80, 18, 210, 77, 234, 108, 50, 109, 163, 130, 2, 104, 48, 130, 2, 100, 48, 14, 6, 3, 85, 29, 15, 1, 1, 255, 4, 4, 3, 2, 7, 128, 48, 19, 6, 3, 85, 29, 37, 4, 12, 48, 10, 6, 8, 43, 6, 1, 5, 5, 7, 3, 1, 48, 12, 6, 3, 85, 29, 19, 1, 1, 255, 4, 2, 48, 0, 48, 29, 6, 3, 85, 29, 14, 4, 22, 4, 20, 214, 103, 166, 83, 212, 251, 70, 19, 90, 81, 159, 90, 229, 252, 199, 112, 251, 21, 1, 223, 48, 31, 6, 3, 85, 29, 35, 4, 24, 48, 22, 128, 20, 138, 116, 127, 175, 133, 205, 238, 149, 205, 61, 156, 208, 226, 70, 20, 243, 113, 53, 29, 39, 48, 106, 6, 8, 43, 6, 1, 5, 5, 7, 1, 1, 4, 94, 48, 92, 48, 39, 6, 8, 43, 6, 1, 5, 5, 7, 48, 1, 134, 27, 104, 116, 116, 112, 58, 47, 47, 111, 99, 115, 112, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 116, 115, 49, 99, 51, 48, 49, 6, 8, 43, 6, 1, 5, 5, 7, 48, 2, 134, 37, 104, 116, 116, 112, 58, 47, 47, 112, 107, 105, 46, 103, 111, 111, 103, 47, 114, 101, 112, 111, 47, 99, 101, 114, 116, 115, 47, 103, 116, 115, 49, 99, 51, 46, 100, 101, 114, 48, 24, 6, 3, 85, 29, 17, 4, 17, 48, 15, 130, 13, 119, 119, 119, 46, 103, 111, 111, 103, 108, 101, 46, 100, 101, 48, 33, 6, 3, 85, 29, 32, 4, 26, 48, 24, 48, 8, 6, 6, 103, 129, 12, 1, 2, 1, 48, 12, 6, 10, 43, 6, 1, 4, 1, 214, 121, 2, 5, 3, 48, 60, 6, 3, 85, 29, 31, 4, 53, 48, 51, 48, 49, 160, 47, 160, 45, 134, 43, 104, 116, 116, 112, 58, 47, 47, 99, 114, 108, 115, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 116, 115, 49, 99, 51, 47, 81, 113, 70, 120, 98, 105, 57, 77, 52, 56, 99, 46, 99, 114, 108, 48, 130, 1, 6, 6, 10, 43, 6, 1, 4, 1, 214, 121, 2, 4, 2, 4, 129, 247, 4, 129, 244, 0, 242, 0, 119, 0, 183, 62, 251, 36, 223, 156, 77, 186, 117, 242, 57, 197, 186, 88, 244, 108, 93, 252, 66, 207, 122, 159, 53, 196, 158, 29, 9, 129, 37, 237, 180, 153, 0, 0, 1, 135, 70, 110, 147, 124, 0, 0, 4, 3, 0, 72, 48, 70, 2, 33, 0, 255, 123, 215, 190, 105, 140, 120, 76, 223, 12, 35, 73, 127, 147, 74, 41, 72, 133, 185, 179, 204, 135, 14, 167, 40, 142, 235, 33, 236, 185, 56, 187, 2, 33, 0, 249, 146, 138, 177, 22, 38, 138, 252, 172, 111, 49, 198, 58, 81, 23, 246, 101, 105, 50, 240, 231, 37, 253, 210, 19, 242, 80, 126, 208, 150, 61, 206, 0, 119, 0, 232, 62, 208, 218, 62, 245, 6, 53, 50, 231, 87, 40, 188, 137, 107, 201, 3, 211, 203, 209, 17, 107, 236, 235, 105, 225, 119, 125, 109, 6, 189, 110, 0, 0, 1, 135, 70, 110, 147, 109, 0, 0, 4, 3, 0, 72, 48, 70, 2, 33, 0, 213, 243, 231, 98, 145, 101, 31, 217, 200, 81, 250, 200, 231, 25, 186, 67, 217, 135, 113, 76, 96, 110, 44, 171, 171, 88, 41, 142, 87, 221, 191, 248, 2, 33, 0, 203, 90, 155, 98, 40, 70, 6, 130, 10, 216, 126, 34, 214, 172, 51, 32, 83, 136, 80, 162, 159, 87, 59, 228, 30, 16, 141, 188, 94, 119, 44, 195, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 3, 130, 1, 1, 0, 5, 200, 236, 42, 163, 67, 196, 232, 159, 112, 110, 9, 114, 131, 77, 76, 31, 166, 48, 62, 59, 228, 180, 65, 196, 80, 154, 36, 88, 0, 17, 104, 250, 191, 236, 213, 42, 127, 208, 198, 132, 14, 94, 24, 205, 80, 222, 203, 153, 75, 248, 75, 189, 182, 222, 133, 77, 16, 180, 101, 165, 4, 4, 8, 6, 75, 183, 239, 121, 203, 220, 126, 183, 186, 37, 2, 153, 203, 54, 56, 111, 58, 39, 163, 54, 91, 26, 244, 19, 154, 225, 108, 117, 14, 25, 127, 93, 64, 16, 250, 185, 159, 155, 25, 212, 78, 133, 147, 247, 246, 68, 228, 87, 162, 183, 246, 106, 245, 191, 194, 116, 35, 25, 169, 221, 237, 76, 155, 57, 24, 229, 163, 176, 73, 160, 105, 90, 32, 33, 141, 195, 61, 84, 118, 22, 43, 2, 199, 13, 113, 77, 202, 135, 68, 208, 2, 188, 119, 241, 231, 47, 78, 115, 133, 109, 200, 36, 92, 91, 7, 174, 175, 10, 169, 201, 33, 88, 71, 171, 206, 186, 199, 154, 95, 107, 252, 191, 245, 40, 122, 192, 231, 188, 38, 124, 34, 122, 182, 92, 125, 165, 38, 120, 37, 188, 15, 109, 152, 213, 139, 14, 248, 156, 178, 154, 17, 142, 167, 6, 234, 41, 77, 211, 96, 165, 206, 107, 206, 29, 125, 81, 55, 74, 37, 9, 195, 194, 108, 225, 104, 121, 68, 65, 58, 193, 150, 127, 246, 170, 255, 71, 92, 216, 233, 26, 223]
                        },
                        'issuerCertificate': {
                            'subject': {
                                'C': 'US',
                                'O': 'Google Trust Services LLC',
                                'CN': 'GTS CA 1C3'
                            },
                            'issuer': {
                                'C': 'US',
                                'O': 'Google Trust Services LLC',
                                'CN': 'GTS Root R1'
                            },
                            'infoAccess': {
                                'OCSP - URI': ['http://ocsp.pki.goog/gtsr1'],
                                'CA Issuers - URI': ['http://pki.goog/repo/certs/gtsr1.der']
                            },
                            'modulus': 'F588DFE7628C1E37F83742907F6C87D0FB658225FDE8CB6BA4FF6DE95A23E299F61CE9920399137C090A8AFA42D65E5624AA7A33841FD1E969BBB974EC574C66689377375553FE39104DB734BB5F2577373B1794EA3CE59DD5BCC3B443EB2EA747EFB0441163D8B44185DD413048931BBFB7F6E0450221E0964217CFD92B6556340726040DA8FD7DCA2EEFEA487C374D3F009F83DFEF75842E79575CFC576E1A96FFFC8C9AA699BE25D97F962C06F7112A028080EB63183C504987E58ACA5F192B59968100A0FB51DBCA770B0BC9964FEF7049C75C6D20FD99B4B4E2CA2E77FD2DDC0BB66B130C8C192B179698B9F08BF6A027BBB6E38D518FBDAEC79BB1899D',
                            'bits': 2048,
                            'exponent': '0x10001',
                            'pubkey': {
                                'type': 'Buffer',
                                'data': [48, 130, 1, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 1, 15, 0, 48, 130, 1, 10, 2, 130, 1, 1, 0, 245, 136, 223, 231, 98, 140, 30, 55, 248, 55, 66, 144, 127, 108, 135, 208, 251, 101, 130, 37, 253, 232, 203, 107, 164, 255, 109, 233, 90, 35, 226, 153, 246, 28, 233, 146, 3, 153, 19, 124, 9, 10, 138, 250, 66, 214, 94, 86, 36, 170, 122, 51, 132, 31, 209, 233, 105, 187, 185, 116, 236, 87, 76, 102, 104, 147, 119, 55, 85, 83, 254, 57, 16, 77, 183, 52, 187, 95, 37, 119, 55, 59, 23, 148, 234, 60, 229, 157, 213, 188, 195, 180, 67, 235, 46, 167, 71, 239, 176, 68, 17, 99, 216, 180, 65, 133, 221, 65, 48, 72, 147, 27, 191, 183, 246, 224, 69, 2, 33, 224, 150, 66, 23, 207, 217, 43, 101, 86, 52, 7, 38, 4, 13, 168, 253, 125, 202, 46, 239, 234, 72, 124, 55, 77, 63, 0, 159, 131, 223, 239, 117, 132, 46, 121, 87, 92, 252, 87, 110, 26, 150, 255, 252, 140, 154, 166, 153, 190, 37, 217, 127, 150, 44, 6, 247, 17, 42, 2, 128, 128, 235, 99, 24, 60, 80, 73, 135, 229, 138, 202, 95, 25, 43, 89, 150, 129, 0, 160, 251, 81, 219, 202, 119, 11, 11, 201, 150, 79, 239, 112, 73, 199, 92, 109, 32, 253, 153, 180, 180, 226, 202, 46, 119, 253, 45, 220, 11, 182, 107, 19, 12, 140, 25, 43, 23, 150, 152, 185, 240, 139, 246, 160, 39, 187, 182, 227, 141, 81, 143, 189, 174, 199, 155, 177, 137, 157, 2, 3, 1, 0, 1]
                            },
                            'valid_from': 'Aug 13 00:00:42 2020 GMT',
                            'valid_to': 'Sep 30 00:00:42 2027 GMT',
                            'fingerprint': '1E:7E:F6:47:CB:A1:50:28:1C:60:89:72:57:10:28:78:C4:BD:8C:DC',
                            'fingerprint256': '23:EC:B0:3E:EC:17:33:8C:4E:33:A6:B4:8A:41:DC:3C:DA:12:28:1B:BC:3F:F8:13:C0:58:9D:6C:C2:38:75:22',
                            'fingerprint512': '43:7B:9E:11:1E:EB:78:01:39:69:F0:BF:AB:EE:CF:67:95:56:D3:FC:3F:6E:F9:C3:21:4F:D0:7B:58:B0:5C:78:DC:1A:9B:E9:B9:9D:21:15:68:BD:B4:4A:4A:33:59:4D:8D:23:08:B4:2A:E9:BF:23:96:82:A0:11:17:8D:FA:10',
                            'ext_key_usage': ['1.3.6.1.5.5.7.3.1', '1.3.6.1.5.5.7.3.2'],
                            'serialNumber': '0203BC53596B34C718F5015066',
                            'raw': {
                                'type': 'Buffer',
                                'data': [48, 130, 5, 150, 48, 130, 3, 126, 160, 3, 2, 1, 2, 2, 13, 2, 3, 188, 83, 89, 107, 52, 199, 24, 245, 1, 80, 102, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 48, 71, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 85, 83, 49, 34, 48, 32, 6, 3, 85, 4, 10, 19, 25, 71, 111, 111, 103, 108, 101, 32, 84, 114, 117, 115, 116, 32, 83, 101, 114, 118, 105, 99, 101, 115, 32, 76, 76, 67, 49, 20, 48, 18, 6, 3, 85, 4, 3, 19, 11, 71, 84, 83, 32, 82, 111, 111, 116, 32, 82, 49, 48, 30, 23, 13, 50, 48, 48, 56, 49, 51, 48, 48, 48, 48, 52, 50, 90, 23, 13, 50, 55, 48, 57, 51, 48, 48, 48, 48, 48, 52, 50, 90, 48, 70, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 85, 83, 49, 34, 48, 32, 6, 3, 85, 4, 10, 19, 25, 71, 111, 111, 103, 108, 101, 32, 84, 114, 117, 115, 116, 32, 83, 101, 114, 118, 105, 99, 101, 115, 32, 76, 76, 67, 49, 19, 48, 17, 6, 3, 85, 4, 3, 19, 10, 71, 84, 83, 32, 67, 65, 32, 49, 67, 51, 48, 130, 1, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 1, 15, 0, 48, 130, 1, 10, 2, 130, 1, 1, 0, 245, 136, 223, 231, 98, 140, 30, 55, 248, 55, 66, 144, 127, 108, 135, 208, 251, 101, 130, 37, 253, 232, 203, 107, 164, 255, 109, 233, 90, 35, 226, 153, 246, 28, 233, 146, 3, 153, 19, 124, 9, 10, 138, 250, 66, 214, 94, 86, 36, 170, 122, 51, 132, 31, 209, 233, 105, 187, 185, 116, 236, 87, 76, 102, 104, 147, 119, 55, 85, 83, 254, 57, 16, 77, 183, 52, 187, 95, 37, 119, 55, 59, 23, 148, 234, 60, 229, 157, 213, 188, 195, 180, 67, 235, 46, 167, 71, 239, 176, 68, 17, 99, 216, 180, 65, 133, 221, 65, 48, 72, 147, 27, 191, 183, 246, 224, 69, 2, 33, 224, 150, 66, 23, 207, 217, 43, 101, 86, 52, 7, 38, 4, 13, 168, 253, 125, 202, 46, 239, 234, 72, 124, 55, 77, 63, 0, 159, 131, 223, 239, 117, 132, 46, 121, 87, 92, 252, 87, 110, 26, 150, 255, 252, 140, 154, 166, 153, 190, 37, 217, 127, 150, 44, 6, 247, 17, 42, 2, 128, 128, 235, 99, 24, 60, 80, 73, 135, 229, 138, 202, 95, 25, 43, 89, 150, 129, 0, 160, 251, 81, 219, 202, 119, 11, 11, 201, 150, 79, 239, 112, 73, 199, 92, 109, 32, 253, 153, 180, 180, 226, 202, 46, 119, 253, 45, 220, 11, 182, 107, 19, 12, 140, 25, 43, 23, 150, 152, 185, 240, 139, 246, 160, 39, 187, 182, 227, 141, 81, 143, 189, 174, 199, 155, 177, 137, 157, 2, 3, 1, 0, 1, 163, 130, 1, 128, 48, 130, 1, 124, 48, 14, 6, 3, 85, 29, 15, 1, 1, 255, 4, 4, 3, 2, 1, 134, 48, 29, 6, 3, 85, 29, 37, 4, 22, 48, 20, 6, 8, 43, 6, 1, 5, 5, 7, 3, 1, 6, 8, 43, 6, 1, 5, 5, 7, 3, 2, 48, 18, 6, 3, 85, 29, 19, 1, 1, 255, 4, 8, 48, 6, 1, 1, 255, 2, 1, 0, 48, 29, 6, 3, 85, 29, 14, 4, 22, 4, 20, 138, 116, 127, 175, 133, 205, 238, 149, 205, 61, 156, 208, 226, 70, 20, 243, 113, 53, 29, 39, 48, 31, 6, 3, 85, 29, 35, 4, 24, 48, 22, 128, 20, 228, 175, 43, 38, 113, 26, 43, 72, 39, 133, 47, 82, 102, 44, 239, 240, 137, 19, 113, 62, 48, 104, 6, 8, 43, 6, 1, 5, 5, 7, 1, 1, 4, 92, 48, 90, 48, 38, 6, 8, 43, 6, 1, 5, 5, 7, 48, 1, 134, 26, 104, 116, 116, 112, 58, 47, 47, 111, 99, 115, 112, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 116, 115, 114, 49, 48, 48, 6, 8, 43, 6, 1, 5, 5, 7, 48, 2, 134, 36, 104, 116, 116, 112, 58, 47, 47, 112, 107, 105, 46, 103, 111, 111, 103, 47, 114, 101, 112, 111, 47, 99, 101, 114, 116, 115, 47, 103, 116, 115, 114, 49, 46, 100, 101, 114, 48, 52, 6, 3, 85, 29, 31, 4, 45, 48, 43, 48, 41, 160, 39, 160, 37, 134, 35, 104, 116, 116, 112, 58, 47, 47, 99, 114, 108, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 116, 115, 114, 49, 47, 103, 116, 115, 114, 49, 46, 99, 114, 108, 48, 87, 6, 3, 85, 29, 32, 4, 80, 48, 78, 48, 56, 6, 10, 43, 6, 1, 4, 1, 214, 121, 2, 5, 3, 48, 42, 48, 40, 6, 8, 43, 6, 1, 5, 5, 7, 2, 1, 22, 28, 104, 116, 116, 112, 115, 58, 47, 47, 112, 107, 105, 46, 103, 111, 111, 103, 47, 114, 101, 112, 111, 115, 105, 116, 111, 114, 121, 47, 48, 8, 6, 6, 103, 129, 12, 1, 2, 1, 48, 8, 6, 6, 103, 129, 12, 1, 2, 2, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 3, 130, 2, 1, 0, 137, 125, 172, 32, 92, 12, 60, 190, 154, 168, 87, 149, 27, 180, 174, 250, 171, 165, 114, 113, 180, 54, 149, 253, 223, 64, 17, 3, 76, 194, 70, 20, 187, 20, 36, 171, 240, 80, 113, 34, 219, 173, 196, 110, 127, 207, 241, 106, 111, 200, 131, 27, 216, 206, 137, 95, 135, 108, 135, 184, 169, 12, 163, 155, 161, 98, 148, 147, 149, 223, 91, 174, 102, 25, 11, 2, 150, 158, 252, 181, 231, 16, 105, 62, 122, 203, 70, 73, 95, 70, 225, 65, 177, 215, 152, 77, 101, 52, 0, 128, 26, 63, 79, 159, 108, 127, 73, 0, 129, 83, 65, 164, 146, 33, 130, 130, 26, 241, 163, 68, 91, 42, 80, 18, 19, 77, 193, 83, 54, 243, 66, 8, 175, 84, 250, 142, 119, 83, 27, 100, 56, 39, 23, 9, 189, 88, 201, 27, 124, 57, 45, 91, 243, 206, 212, 237, 151, 219, 20, 3, 191, 9, 83, 36, 31, 194, 12, 4, 121, 152, 38, 242, 97, 241, 83, 82, 253, 66, 140, 27, 102, 43, 63, 21, 161, 187, 255, 246, 155, 227, 129, 154, 1, 6, 113, 137, 53, 40, 36, 221, 225, 189, 235, 25, 45, 225, 72, 203, 61, 89, 131, 81, 180, 116, 198, 157, 124, 198, 177, 134, 91, 175, 204, 52, 196, 211, 204, 212, 129, 17, 149, 0, 161, 244, 18, 34, 1, 250, 180, 131, 113, 175, 140, 183, 140, 115, 36, 172, 55, 83, 194, 0, 144, 63, 17, 254, 92, 237, 54, 148, 16, 59, 189, 41, 174, 226, 199, 58, 98, 59, 108, 99, 217, 128, 191, 89, 113, 172, 99, 39, 185, 76, 23, 160, 218, 246, 115, 21, 191, 42, 222, 143, 243, 165, 108, 50, 129, 51, 3, 208, 134, 81, 113, 153, 52, 186, 147, 141, 93, 181, 81, 88, 247, 178, 147, 232, 1, 246, 89, 190, 113, 155, 253, 77, 40, 206, 207, 109, 199, 22, 220, 247, 209, 214, 70, 155, 167, 202, 107, 233, 119, 15, 253, 160, 182, 27, 35, 131, 29, 16, 26, 217, 9, 0, 132, 224, 68, 211, 162, 117, 35, 179, 52, 134, 246, 32, 176, 164, 94, 16, 29, 224, 82, 70, 0, 157, 177, 15, 31, 33, 112, 81, 245, 154, 221, 6, 252, 85, 244, 43, 14, 51, 119, 195, 75, 66, 194, 241, 119, 19, 252, 115, 128, 148, 235, 31, 187, 55, 63, 206, 2, 42, 102, 176, 115, 29, 50, 165, 50, 108, 50, 176, 142, 224, 196, 35, 255, 91, 125, 77, 101, 112, 172, 43, 155, 61, 206, 219, 224, 109, 142, 50, 128, 190, 150, 159, 146, 99, 188, 151, 187, 93, 185, 244, 225, 113, 94, 42, 228, 239, 3, 34, 177, 138, 101, 58, 143, 192, 147, 101, 212, 133, 205, 15, 15, 91, 131, 89, 22, 71, 22, 45, 156, 36, 58, 200, 128, 166, 38, 20, 133, 155, 246, 55, 155, 172, 111, 249, 197, 195, 6, 81, 243, 226, 127, 197, 177, 16, 186, 81, 244, 221]
                            },
                            'issuerCertificate': {
                                'subject': {
                                    'C': 'US',
                                    'O': 'Google Trust Services LLC',
                                    'CN': 'GTS Root R1'
                                },
                                'issuer': {
                                    'C': 'BE',
                                    'O': 'GlobalSign nv-sa',
                                    'OU': 'Root CA',
                                    'CN': 'GlobalSign Root CA'
                                },
                                'infoAccess': {
                                    'OCSP - URI': ['http://ocsp.pki.goog/gsr1'],
                                    'CA Issuers - URI': ['http://pki.goog/gsr1/gsr1.crt']
                                },
                                'modulus': 'B611028B1EE3A1779B3BDCBF943EB795A7403CA1FD82F97D32068271F6F68C7FFBE8DBBC6A2E9797A38C4BF92BF6B1F9CE841DB1F9C597DEEFB9F2A3E9BC12895EA7AA52ABF82327CBA4B19C63DBD7997EF00A5EEB68A6F4C65A470D4D1033E34EB113A3C8186C4BECFC0990DF9D6429252307A1B4D23D2E60E0CFD20987BBCD48F04DC2C27A888ABBBACF5919D6AF8FB007B09E31F182C1C0DF2EA66D6C190EB5D87E261A45033DB079A49428AD0F7F26E5A808FE96E83C689453EE833A882B159609B2E07A8C2E75D69CEBA756648F964F68AE3D97C2848FC0BC40C00B5CBDF687B3356CAC18507F84E04CCD92D320E933BC5299AF32B529B3252AB448F972E1CA64F7E682108DE89DC28A88FA38668AFC63F901F978FD7B5C77FA7687FAECDFB10E799557B4BD26EFD601D1EB160ABB8E0BB5C5C58A55ABD3ACEA914B29CC19A432254E2AF16544D002CEAACE49B4EA9F7C83B0407BE743ABA76CA38F7D8981FA4CA5FFD58EC3CE4BE0B5D8B38E45CF76C0ED402BFD530FB0A7D53B0DB18AA203DE31ADCC77EA6F7B3ED6DF912212E6BEFAD832FC1063145172DE5DD61693BD296833EF3A66EC078A26DF13D757657827DE5E491400A2007F9AA821B6A9B195B0A5B90D1611DAC76C483C40E07E0D5ACD563CD19705B9CB4BED394B9CC43FD255136E24B0D671FAF4C1BACCED1BF5FE8141D800983D3AC8AE7A9837180595',
                                'bits': 4096,
                                'exponent': '0x10001',
                                'pubkey': {
                                    'type': 'Buffer',
                                    'data': [48, 130, 2, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 2, 15, 0, 48, 130, 2, 10, 2, 130, 2, 1, 0, 182, 17, 2, 139, 30, 227, 161, 119, 155, 59, 220, 191, 148, 62, 183, 149, 167, 64, 60, 161, 253, 130, 249, 125, 50, 6, 130, 113, 246, 246, 140, 127, 251, 232, 219, 188, 106, 46, 151, 151, 163, 140, 75, 249, 43, 246, 177, 249, 206, 132, 29, 177, 249, 197, 151, 222, 239, 185, 242, 163, 233, 188, 18, 137, 94, 167, 170, 82, 171, 248, 35, 39, 203, 164, 177, 156, 99, 219, 215, 153, 126, 240, 10, 94, 235, 104, 166, 244, 198, 90, 71, 13, 77, 16, 51, 227, 78, 177, 19, 163, 200, 24, 108, 75, 236, 252, 9, 144, 223, 157, 100, 41, 37, 35, 7, 161, 180, 210, 61, 46, 96, 224, 207, 210, 9, 135, 187, 205, 72, 240, 77, 194, 194, 122, 136, 138, 187, 186, 207, 89, 25, 214, 175, 143, 176, 7, 176, 158, 49, 241, 130, 193, 192, 223, 46, 166, 109, 108, 25, 14, 181, 216, 126, 38, 26, 69, 3, 61, 176, 121, 164, 148, 40, 173, 15, 127, 38, 229, 168, 8, 254, 150, 232, 60, 104, 148, 83, 238, 131, 58, 136, 43, 21, 150, 9, 178, 224, 122, 140, 46, 117, 214, 156, 235, 167, 86, 100, 143, 150, 79, 104, 174, 61, 151, 194, 132, 143, 192, 188, 64, 192, 11, 92, 189, 246, 135, 179, 53, 108, 172, 24, 80, 127, 132, 224, 76, 205, 146, 211, 32, 233, 51, 188, 82, 153, 175, 50, 181, 41, 179, 37, 42, 180, 72, 249, 114, 225, 202, 100, 247, 230, 130, 16, 141, 232, 157, 194, 138, 136, 250, 56, 102, 138, 252, 99, 249, 1, 249, 120, 253, 123, 92, 119, 250, 118, 135, 250, 236, 223, 177, 14, 121, 149, 87, 180, 189, 38, 239, 214, 1, 209, 235, 22, 10, 187, 142, 11, 181, 197, 197, 138, 85, 171, 211, 172, 234, 145, 75, 41, 204, 25, 164, 50, 37, 78, 42, 241, 101, 68, 208, 2, 206, 170, 206, 73, 180, 234, 159, 124, 131, 176, 64, 123, 231, 67, 171, 167, 108, 163, 143, 125, 137, 129, 250, 76, 165, 255, 213, 142, 195, 206, 75, 224, 181, 216, 179, 142, 69, 207, 118, 192, 237, 64, 43, 253, 83, 15, 176, 167, 213, 59, 13, 177, 138, 162, 3, 222, 49, 173, 204, 119, 234, 111, 123, 62, 214, 223, 145, 34, 18, 230, 190, 250, 216, 50, 252, 16, 99, 20, 81, 114, 222, 93, 214, 22, 147, 189, 41, 104, 51, 239, 58, 102, 236, 7, 138, 38, 223, 19, 215, 87, 101, 120, 39, 222, 94, 73, 20, 0, 162, 0, 127, 154, 168, 33, 182, 169, 177, 149, 176, 165, 185, 13, 22, 17, 218, 199, 108, 72, 60, 64, 224, 126, 13, 90, 205, 86, 60, 209, 151, 5, 185, 203, 75, 237, 57, 75, 156, 196, 63, 210, 85, 19, 110, 36, 176, 214, 113, 250, 244, 193, 186, 204, 237, 27, 245, 254, 129, 65, 216, 0, 152, 61, 58, 200, 174, 122, 152, 55, 24, 5, 149, 2, 3, 1, 0, 1]
                                },
                                'valid_from': 'Jun 19 00:00:42 2020 GMT',
                                'valid_to': 'Jan 28 00:00:42 2028 GMT',
                                'fingerprint': '08:74:54:87:E8:91:C1:9E:30:78:C1:F2:A0:7E:45:29:50:EF:36:F6',
                                'fingerprint256': '3E:E0:27:8D:F7:1F:A3:C1:25:C4:CD:48:7F:01:D7:74:69:4E:6F:C5:7E:0C:D9:4C:24:EF:D7:69:13:39:18:E5',
                                'fingerprint512': '7C:88:3C:25:8B:8D:E7:34:81:D6:61:21:DF:53:D0:99:7A:7C:3B:06:E0:E7:09:68:8F:FB:1E:FD:18:B3:6C:B5:43:5F:41:52:8C:7E:64:D6:D8:88:B2:27:28:17:AE:D1:0C:4A:44:22:0E:01:F3:84:50:2F:04:95:E7:85:13:05',
                                'serialNumber': '77BD0D6CDB36F91AEA210FC4F058D30D',
                                'raw': {
                                    'type': 'Buffer',
                                    'data': [48, 130, 5, 98, 48, 130, 4, 74, 160, 3, 2, 1, 2, 2, 16, 119, 189, 13, 108, 219, 54, 249, 26, 234, 33, 15, 196, 240, 88, 211, 13, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 48, 87, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 66, 69, 49, 25, 48, 23, 6, 3, 85, 4, 10, 19, 16, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 110, 118, 45, 115, 97, 49, 16, 48, 14, 6, 3, 85, 4, 11, 19, 7, 82, 111, 111, 116, 32, 67, 65, 49, 27, 48, 25, 6, 3, 85, 4, 3, 19, 18, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 82, 111, 111, 116, 32, 67, 65, 48, 30, 23, 13, 50, 48, 48, 54, 49, 57, 48, 48, 48, 48, 52, 50, 90, 23, 13, 50, 56, 48, 49, 50, 56, 48, 48, 48, 48, 52, 50, 90, 48, 71, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 85, 83, 49, 34, 48, 32, 6, 3, 85, 4, 10, 19, 25, 71, 111, 111, 103, 108, 101, 32, 84, 114, 117, 115, 116, 32, 83, 101, 114, 118, 105, 99, 101, 115, 32, 76, 76, 67, 49, 20, 48, 18, 6, 3, 85, 4, 3, 19, 11, 71, 84, 83, 32, 82, 111, 111, 116, 32, 82, 49, 48, 130, 2, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 2, 15, 0, 48, 130, 2, 10, 2, 130, 2, 1, 0, 182, 17, 2, 139, 30, 227, 161, 119, 155, 59, 220, 191, 148, 62, 183, 149, 167, 64, 60, 161, 253, 130, 249, 125, 50, 6, 130, 113, 246, 246, 140, 127, 251, 232, 219, 188, 106, 46, 151, 151, 163, 140, 75, 249, 43, 246, 177, 249, 206, 132, 29, 177, 249, 197, 151, 222, 239, 185, 242, 163, 233, 188, 18, 137, 94, 167, 170, 82, 171, 248, 35, 39, 203, 164, 177, 156, 99, 219, 215, 153, 126, 240, 10, 94, 235, 104, 166, 244, 198, 90, 71, 13, 77, 16, 51, 227, 78, 177, 19, 163, 200, 24, 108, 75, 236, 252, 9, 144, 223, 157, 100, 41, 37, 35, 7, 161, 180, 210, 61, 46, 96, 224, 207, 210, 9, 135, 187, 205, 72, 240, 77, 194, 194, 122, 136, 138, 187, 186, 207, 89, 25, 214, 175, 143, 176, 7, 176, 158, 49, 241, 130, 193, 192, 223, 46, 166, 109, 108, 25, 14, 181, 216, 126, 38, 26, 69, 3, 61, 176, 121, 164, 148, 40, 173, 15, 127, 38, 229, 168, 8, 254, 150, 232, 60, 104, 148, 83, 238, 131, 58, 136, 43, 21, 150, 9, 178, 224, 122, 140, 46, 117, 214, 156, 235, 167, 86, 100, 143, 150, 79, 104, 174, 61, 151, 194, 132, 143, 192, 188, 64, 192, 11, 92, 189, 246, 135, 179, 53, 108, 172, 24, 80, 127, 132, 224, 76, 205, 146, 211, 32, 233, 51, 188, 82, 153, 175, 50, 181, 41, 179, 37, 42, 180, 72, 249, 114, 225, 202, 100, 247, 230, 130, 16, 141, 232, 157, 194, 138, 136, 250, 56, 102, 138, 252, 99, 249, 1, 249, 120, 253, 123, 92, 119, 250, 118, 135, 250, 236, 223, 177, 14, 121, 149, 87, 180, 189, 38, 239, 214, 1, 209, 235, 22, 10, 187, 142, 11, 181, 197, 197, 138, 85, 171, 211, 172, 234, 145, 75, 41, 204, 25, 164, 50, 37, 78, 42, 241, 101, 68, 208, 2, 206, 170, 206, 73, 180, 234, 159, 124, 131, 176, 64, 123, 231, 67, 171, 167, 108, 163, 143, 125, 137, 129, 250, 76, 165, 255, 213, 142, 195, 206, 75, 224, 181, 216, 179, 142, 69, 207, 118, 192, 237, 64, 43, 253, 83, 15, 176, 167, 213, 59, 13, 177, 138, 162, 3, 222, 49, 173, 204, 119, 234, 111, 123, 62, 214, 223, 145, 34, 18, 230, 190, 250, 216, 50, 252, 16, 99, 20, 81, 114, 222, 93, 214, 22, 147, 189, 41, 104, 51, 239, 58, 102, 236, 7, 138, 38, 223, 19, 215, 87, 101, 120, 39, 222, 94, 73, 20, 0, 162, 0, 127, 154, 168, 33, 182, 169, 177, 149, 176, 165, 185, 13, 22, 17, 218, 199, 108, 72, 60, 64, 224, 126, 13, 90, 205, 86, 60, 209, 151, 5, 185, 203, 75, 237, 57, 75, 156, 196, 63, 210, 85, 19, 110, 36, 176, 214, 113, 250, 244, 193, 186, 204, 237, 27, 245, 254, 129, 65, 216, 0, 152, 61, 58, 200, 174, 122, 152, 55, 24, 5, 149, 2, 3, 1, 0, 1, 163, 130, 1, 56, 48, 130, 1, 52, 48, 14, 6, 3, 85, 29, 15, 1, 1, 255, 4, 4, 3, 2, 1, 134, 48, 15, 6, 3, 85, 29, 19, 1, 1, 255, 4, 5, 48, 3, 1, 1, 255, 48, 29, 6, 3, 85, 29, 14, 4, 22, 4, 20, 228, 175, 43, 38, 113, 26, 43, 72, 39, 133, 47, 82, 102, 44, 239, 240, 137, 19, 113, 62, 48, 31, 6, 3, 85, 29, 35, 4, 24, 48, 22, 128, 20, 96, 123, 102, 26, 69, 13, 151, 202, 137, 80, 47, 125, 4, 205, 52, 168, 255, 252, 253, 75, 48, 96, 6, 8, 43, 6, 1, 5, 5, 7, 1, 1, 4, 84, 48, 82, 48, 37, 6, 8, 43, 6, 1, 5, 5, 7, 48, 1, 134, 25, 104, 116, 116, 112, 58, 47, 47, 111, 99, 115, 112, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 115, 114, 49, 48, 41, 6, 8, 43, 6, 1, 5, 5, 7, 48, 2, 134, 29, 104, 116, 116, 112, 58, 47, 47, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 115, 114, 49, 47, 103, 115, 114, 49, 46, 99, 114, 116, 48, 50, 6, 3, 85, 29, 31, 4, 43, 48, 41, 48, 39, 160, 37, 160, 35, 134, 33, 104, 116, 116, 112, 58, 47, 47, 99, 114, 108, 46, 112, 107, 105, 46, 103, 111, 111, 103, 47, 103, 115, 114, 49, 47, 103, 115, 114, 49, 46, 99, 114, 108, 48, 59, 6, 3, 85, 29, 32, 4, 52, 48, 50, 48, 8, 6, 6, 103, 129, 12, 1, 2, 1, 48, 8, 6, 6, 103, 129, 12, 1, 2, 2, 48, 13, 6, 11, 43, 6, 1, 4, 1, 214, 121, 2, 5, 3, 2, 48, 13, 6, 11, 43, 6, 1, 4, 1, 214, 121, 2, 5, 3, 3, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 11, 5, 0, 3, 130, 1, 1, 0, 52, 164, 30, 177, 40, 163, 208, 180, 118, 23, 166, 49, 122, 33, 233, 209, 82, 62, 200, 219, 116, 22, 65, 136, 184, 61, 53, 29, 237, 228, 255, 147, 225, 92, 95, 171, 187, 234, 124, 207, 219, 228, 13, 209, 139, 87, 242, 38, 111, 91, 190, 23, 70, 104, 148, 55, 111, 107, 122, 200, 192, 24, 55, 250, 37, 81, 172, 236, 104, 191, 178, 200, 73, 253, 90, 154, 202, 1, 35, 172, 132, 128, 43, 2, 140, 153, 151, 235, 73, 106, 140, 117, 215, 199, 222, 178, 201, 151, 159, 88, 72, 87, 14, 53, 161, 228, 26, 214, 253, 111, 131, 129, 111, 239, 140, 207, 151, 175, 192, 133, 42, 240, 245, 78, 105, 9, 145, 45, 225, 104, 184, 193, 43, 115, 233, 212, 217, 252, 34, 192, 55, 31, 11, 102, 29, 73, 237, 2, 85, 143, 103, 225, 50, 215, 211, 38, 191, 112, 227, 61, 244, 103, 109, 61, 124, 229, 52, 136, 227, 50, 250, 167, 110, 6, 106, 111, 189, 139, 145, 238, 22, 75, 232, 59, 169, 179, 55, 231, 195, 68, 164, 126, 216, 108, 215, 199, 70, 245, 146, 155, 231, 213, 33, 190, 102, 146, 25, 148, 85, 108, 212, 41, 178, 13, 193, 102, 91, 226, 119, 73, 72, 40, 237, 157, 215, 26, 51, 114, 83, 179, 130, 53, 207, 98, 139, 201, 36, 139, 165, 183, 57, 12, 187, 126, 42, 65, 191, 82, 207, 252, 162, 150, 182, 194, 130, 63]
                                },
                                'issuerCertificate': {
                                    'subject': {
                                        'C': 'BE',
                                        'O': 'GlobalSign nv-sa',
                                        'OU': 'Root CA',
                                        'CN': 'GlobalSign Root CA'
                                    },
                                    'issuer': {
                                        'C': 'BE',
                                        'O': 'GlobalSign nv-sa',
                                        'OU': 'Root CA',
                                        'CN': 'GlobalSign Root CA'
                                    },
                                    'modulus': 'DA0EE6998DCEA3E34F8A7EFBF18B83256BEA481FF12AB0B9951104BDF063D1E26766CF1CDDCF1B482BEE8D898E9AAF298065ABE9C72D12CBAB1C4C7007A13D0A30CD158D4FF8DDD48C50151CEF50EEC42EF7FCE952F2917DE06DD535308E5E4373F241E9D56AE3B2893A5639386F063C88695B2A4DC5A754B86C89CC9BF93CCAE5FD89F5123C927896D6DC746E934461D18DC746B2750E86E8198AD56D6CD5781695A2E9C80A38EBF224134F73549313853A1BBC1E34B58B058CB9778BB1DB1F2091AB09536E90CE7B3774B97047912251631679AEB1AE412608C8192BD146AA48D6642AD78334FF2C2AC16C19434A0785E7D37CF62168EFEAF2529F7F9390CF',
                                    'bits': 2048,
                                    'exponent': '0x10001',
                                    'pubkey': {
                                        'type': 'Buffer',
                                        'data': [48, 130, 1, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 1, 15, 0, 48, 130, 1, 10, 2, 130, 1, 1, 0, 218, 14, 230, 153, 141, 206, 163, 227, 79, 138, 126, 251, 241, 139, 131, 37, 107, 234, 72, 31, 241, 42, 176, 185, 149, 17, 4, 189, 240, 99, 209, 226, 103, 102, 207, 28, 221, 207, 27, 72, 43, 238, 141, 137, 142, 154, 175, 41, 128, 101, 171, 233, 199, 45, 18, 203, 171, 28, 76, 112, 7, 161, 61, 10, 48, 205, 21, 141, 79, 248, 221, 212, 140, 80, 21, 28, 239, 80, 238, 196, 46, 247, 252, 233, 82, 242, 145, 125, 224, 109, 213, 53, 48, 142, 94, 67, 115, 242, 65, 233, 213, 106, 227, 178, 137, 58, 86, 57, 56, 111, 6, 60, 136, 105, 91, 42, 77, 197, 167, 84, 184, 108, 137, 204, 155, 249, 60, 202, 229, 253, 137, 245, 18, 60, 146, 120, 150, 214, 220, 116, 110, 147, 68, 97, 209, 141, 199, 70, 178, 117, 14, 134, 232, 25, 138, 213, 109, 108, 213, 120, 22, 149, 162, 233, 200, 10, 56, 235, 242, 36, 19, 79, 115, 84, 147, 19, 133, 58, 27, 188, 30, 52, 181, 139, 5, 140, 185, 119, 139, 177, 219, 31, 32, 145, 171, 9, 83, 110, 144, 206, 123, 55, 116, 185, 112, 71, 145, 34, 81, 99, 22, 121, 174, 177, 174, 65, 38, 8, 200, 25, 43, 209, 70, 170, 72, 214, 100, 42, 215, 131, 52, 255, 44, 42, 193, 108, 25, 67, 74, 7, 133, 231, 211, 124, 246, 33, 104, 239, 234, 242, 82, 159, 127, 147, 144, 207, 2, 3, 1, 0, 1]
                                    },
                                    'valid_from': 'Sep  1 12:00:00 1998 GMT',
                                    'valid_to': 'Jan 28 12:00:00 2028 GMT',
                                    'fingerprint': 'B1:BC:96:8B:D4:F4:9D:62:2A:A8:9A:81:F2:15:01:52:A4:1D:82:9C',
                                    'fingerprint256': 'EB:D4:10:40:E4:BB:3E:C7:42:C9:E3:81:D3:1E:F2:A4:1A:48:B6:68:5C:96:E7:CE:F3:C1:DF:6C:D4:33:1C:99',
                                    'fingerprint512': '54:BA:00:4D:54:35:E8:B1:05:31:43:1C:39:2E:D9:97:76:12:0D:36:38:08:13:7D:E7:EB:59:03:04:63:F8:63:CA:DD:02:BD:F9:18:F5:96:B6:D2:09:64:B3:17:25:C2:36:3C:D7:60:17:99:CA:A9:36:0A:1C:36:FE:81:9F:BD',
                                    'serialNumber': '040000000001154B5AC394',
                                    'raw': {
                                        'type': 'Buffer',
                                        'data': [48, 130, 3, 117, 48, 130, 2, 93, 160, 3, 2, 1, 2, 2, 11, 4, 0, 0, 0, 0, 1, 21, 75, 90, 195, 148, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 5, 5, 0, 48, 87, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 66, 69, 49, 25, 48, 23, 6, 3, 85, 4, 10, 19, 16, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 110, 118, 45, 115, 97, 49, 16, 48, 14, 6, 3, 85, 4, 11, 19, 7, 82, 111, 111, 116, 32, 67, 65, 49, 27, 48, 25, 6, 3, 85, 4, 3, 19, 18, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 82, 111, 111, 116, 32, 67, 65, 48, 30, 23, 13, 57, 56, 48, 57, 48, 49, 49, 50, 48, 48, 48, 48, 90, 23, 13, 50, 56, 48, 49, 50, 56, 49, 50, 48, 48, 48, 48, 90, 48, 87, 49, 11, 48, 9, 6, 3, 85, 4, 6, 19, 2, 66, 69, 49, 25, 48, 23, 6, 3, 85, 4, 10, 19, 16, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 110, 118, 45, 115, 97, 49, 16, 48, 14, 6, 3, 85, 4, 11, 19, 7, 82, 111, 111, 116, 32, 67, 65, 49, 27, 48, 25, 6, 3, 85, 4, 3, 19, 18, 71, 108, 111, 98, 97, 108, 83, 105, 103, 110, 32, 82, 111, 111, 116, 32, 67, 65, 48, 130, 1, 34, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 1, 5, 0, 3, 130, 1, 15, 0, 48, 130, 1, 10, 2, 130, 1, 1, 0, 218, 14, 230, 153, 141, 206, 163, 227, 79, 138, 126, 251, 241, 139, 131, 37, 107, 234, 72, 31, 241, 42, 176, 185, 149, 17, 4, 189, 240, 99, 209, 226, 103, 102, 207, 28, 221, 207, 27, 72, 43, 238, 141, 137, 142, 154, 175, 41, 128, 101, 171, 233, 199, 45, 18, 203, 171, 28, 76, 112, 7, 161, 61, 10, 48, 205, 21, 141, 79, 248, 221, 212, 140, 80, 21, 28, 239, 80, 238, 196, 46, 247, 252, 233, 82, 242, 145, 125, 224, 109, 213, 53, 48, 142, 94, 67, 115, 242, 65, 233, 213, 106, 227, 178, 137, 58, 86, 57, 56, 111, 6, 60, 136, 105, 91, 42, 77, 197, 167, 84, 184, 108, 137, 204, 155, 249, 60, 202, 229, 253, 137, 245, 18, 60, 146, 120, 150, 214, 220, 116, 110, 147, 68, 97, 209, 141, 199, 70, 178, 117, 14, 134, 232, 25, 138, 213, 109, 108, 213, 120, 22, 149, 162, 233, 200, 10, 56, 235, 242, 36, 19, 79, 115, 84, 147, 19, 133, 58, 27, 188, 30, 52, 181, 139, 5, 140, 185, 119, 139, 177, 219, 31, 32, 145, 171, 9, 83, 110, 144, 206, 123, 55, 116, 185, 112, 71, 145, 34, 81, 99, 22, 121, 174, 177, 174, 65, 38, 8, 200, 25, 43, 209, 70, 170, 72, 214, 100, 42, 215, 131, 52, 255, 44, 42, 193, 108, 25, 67, 74, 7, 133, 231, 211, 124, 246, 33, 104, 239, 234, 242, 82, 159, 127, 147, 144, 207, 2, 3, 1, 0, 1, 163, 66, 48, 64, 48, 14, 6, 3, 85, 29, 15, 1, 1, 255, 4, 4, 3, 2, 1, 6, 48, 15, 6, 3, 85, 29, 19, 1, 1, 255, 4, 5, 48, 3, 1, 1, 255, 48, 29, 6, 3, 85, 29, 14, 4, 22, 4, 20, 96, 123, 102, 26, 69, 13, 151, 202, 137, 80, 47, 125, 4, 205, 52, 168, 255, 252, 253, 75, 48, 13, 6, 9, 42, 134, 72, 134, 247, 13, 1, 1, 5, 5, 0, 3, 130, 1, 1, 0, 214, 115, 231, 124, 79, 118, 208, 141, 191, 236, 186, 162, 190, 52, 197, 40, 50, 181, 124, 252, 108, 156, 44, 43, 189, 9, 158, 83, 191, 107, 94, 170, 17, 72, 182, 229, 8, 163, 179, 202, 61, 97, 77, 211, 70, 9, 179, 62, 195, 160, 227, 99, 85, 27, 242, 186, 239, 173, 57, 225, 67, 185, 56, 163, 230, 47, 138, 38, 59, 239, 160, 80, 86, 249, 198, 10, 253, 56, 205, 196, 11, 112, 81, 148, 151, 152, 4, 223, 195, 95, 148, 213, 21, 201, 20, 65, 156, 196, 93, 117, 100, 21, 13, 255, 85, 48, 236, 134, 143, 255, 13, 239, 44, 185, 99, 70, 246, 170, 252, 223, 188, 105, 253, 46, 18, 72, 100, 154, 224, 149, 240, 166, 239, 41, 143, 1, 177, 21, 181, 12, 29, 165, 254, 105, 44, 105, 36, 120, 30, 179, 167, 28, 113, 98, 238, 202, 200, 151, 172, 23, 93, 138, 194, 248, 71, 134, 110, 42, 196, 86, 49, 149, 208, 103, 137, 133, 43, 249, 108, 166, 93, 70, 157, 12, 170, 130, 228, 153, 81, 221, 112, 183, 219, 86, 61, 97, 228, 106, 225, 92, 214, 246, 254, 61, 222, 65, 204, 7, 174, 99, 82, 191, 83, 83, 244, 43, 233, 199, 253, 182, 247, 130, 95, 133, 210, 65, 24, 219, 129, 179, 4, 28, 197, 31, 164, 128, 111, 21, 32, 201, 222, 12, 136, 10, 29, 214, 102, 85, 226, 252, 72, 201, 41, 38, 105, 224]
                                    },
                                    'issuerCertificate': None,
                                    'validTo': '2028-01-28T12:00:00.000Z',
                                    'daysRemaining': 1733
                                },
                                'validTo': '2028-01-28T00:00:42.000Z',
                                'daysRemaining': 1732
                            },
                            'validTo': '2027-09-30T00:00:42.000Z',
                            'daysRemaining': 1612
                        },
                        'validTo': '2023-06-26T08:24:22.000Z',
                        'validFor': ['www.google.de'],
                        'daysRemaining': 56
                    }
                }
            }
        """
        # TODO: endless call if only ping monitors used
        return self._get_event_data(Event.CERT_INFO)

    # uptime

    def uptime(self) -> dict:
        """
        Get monitor uptime.

        :return: Monitor uptime.
        :rtype: dict

        Example::

            >>> api.uptime()
            {
                1: {
                    24: 1,
                    720: 1
                }
            }
        """
        return self._get_event_data(Event.UPTIME)

    # info

    def info(self) -> dict:
        """
        Get server info.

        :return: Server info.
        :rtype: dict

        Example::

            >>> api.info()
            {
                'version': '1.19.2',
                'latestVersion': '1.19.2',
                'primaryBaseURL': None,
                'serverTimezone': 'Europe/Berlin',
                'serverTimezoneOffset': '+01:00'
            }
        """
        r = self._get_event_data(Event.INFO)
        return r

    # clear

    def clear_events(self, monitor_id: int) -> dict:
        """
        Clear monitor events.

        :param int monitor_id: Id of the monitor to clear events.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_events(1)
            {}
        """
        return self._call('clearEvents', monitor_id)

    def clear_heartbeats(self, monitor_id: int) -> dict:
        """
        Clear monitor heartbeats.

        :param int monitor_id: Id of the monitor to clear heartbeats.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_heartbeats(1)
            {}
        """
        return self._call('clearHeartbeats', monitor_id)

    def clear_statistics(self) -> dict:
        """
        Clear statistics.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_statistics()
            {}
        """
        return self._call('clearStatistics')

    # tags

    def get_tags(self) -> list:
        """
        Get all tags.

        :return: All tags.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_tags()
            [
                {
                    'color': '#ffffff',
                    'id': 1,
                    'name': 'tag 1'
                }
            ]
        """
        return self._call('getTags')["tags"]

    def get_tag(self, id_: int) -> dict:
        """
        Get a tag.

        :param int id_: Id of the monitor to get.
        :return: The tag.
        :rtype: dict
        :raises UptimeKumaException: If the tag does not exist.

        Example::

            >>> api.get_tag(1)
            {
                'color': '#ffffff',
                'id': 1,
                'name': 'tag 1'
            }
        """

        tags = self.get_tags()
        for tag in tags:
            if tag["id"] == id_:
                return tag
        raise UptimeKumaException("tag does not exist")

    @append_docstring(tag_docstring("add"))
    def add_tag(self, **kwargs) -> dict:
        """
        Add a tag.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_tag(
            ...     name="tag 1",
            ...     color="#ffffff"
            ... )
            {
                'color': '#ffffff',
                'id': 1,
                'name': 'tag 1'
            }
        """
        data = _build_tag_data(**kwargs)
        _check_arguments_tag(data)
        return self._call('addTag', data)["tag"]

    @append_docstring(tag_docstring("edit"))
    def edit_tag(self, id_: int, **kwargs) -> dict:
        """
        Edits an existing tag.

        :param int id_: Id of the tag to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_tag(1,
            ...     name="tag 1 new",
            ...     color="#000000"
            ... )
            {
                'msg': 'Saved',
                'tag': {
                    'id': 1,
                    'name': 'tag 1 new',
                    'color': '#000000'
                }
            }
        """
        data = self.get_tag(id_)
        data.update(kwargs)
        _check_arguments_tag(data)
        return self._call('editTag', data)

    def delete_tag(self, id_: int) -> dict:
        """
        Delete a tag.

        :param int id_: Id of the monitor to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_tag(1)
            {
                'msg': 'Deleted Successfully.'
            }
        """
        return self._call('deleteTag', id_)

    # settings

    def get_settings(self) -> dict:
        """
        Get settings.

        :return: Settings.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_settings()
            {
                'checkBeta': False,
                'checkUpdate': False,
                'disableAuth': False,
                'dnsCache': True,
                'entryPage': 'dashboard',
                'keepDataPeriodDays': 180,
                'primaryBaseURL': '',
                'searchEngineIndex': False,
                'serverTimezone': 'Europe/Berlin',
                'steamAPIKey': '',
                'tlsExpiryNotifyDays': [
                    7,
                    14,
                    21
                ],
                'trustProxy': False
            }
        """
        r = self._call('getSettings')["data"]
        return r

    def set_settings(
            self,
            password: str = None,  # only required if disableAuth is true

            # about
            checkUpdate: bool = True,
            checkBeta: bool = False,

            # monitor history
            keepDataPeriodDays: int = 180,

            # general
            serverTimezone: str = "",
            entryPage: str = "dashboard",
            searchEngineIndex: bool = False,
            primaryBaseURL: str = "",
            steamAPIKey: str = "",
            dnsCache: bool = False,

            # notifications
            tlsExpiryNotifyDays: list = None,

            # security
            disableAuth: bool = False,

            # reverse proxy
            trustProxy: bool = False
    ) -> dict:
        """
        Set settings.

        :param str, optional password: Password, defaults to None
        :param bool, optional checkUpdate: Show update if available, defaults to True
        :param bool, optional checkBeta: Also check beta release, defaults to False
        :param int, optional keepDataPeriodDays: Keep monitor history data for X days. Set to 0 for infinite retention., defaults to 180
        :param str, optional serverTimezone: Server Timezone, defaults to ""
        :param str, optional entryPage: Entry Page, defaults to "dashboard"
        :param bool, optional searchEngineIndex: Search Engine Visibility, defaults to False
        :param str, optional primaryBaseURL: Primary Base URL, defaults to ""
        :param str, optional steamAPIKey: Steam API Key. For monitoring a Steam Game Server you need a Steam Web-API key., defaults to ""
        :param bool, optional dnsCache: True to enable DNS Cache. It may be not working in some IPv6 environments, disable it if you encounter any issues., defaults to False
        :param list, optional tlsExpiryNotifyDays: TLS Certificate Expiry. HTTPS Monitors trigger notification when TLS certificate expires in., defaults to None
        :param bool, optional disableAuth: Disable Authentication, defaults to False
        :param bool, optional trustProxy: Trust Proxy. Trust 'X-Forwarded-\*' headers. If you want to get the correct client IP and your Uptime Kuma is behind such as Nginx or Apache, you should enable this., defaults to False
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.set_settings(
            ...     checkUpdate=False,
            ...     checkBeta=False,
            ...     keepDataPeriodDays=180,
            ...     serverTimezone="Europe/Berlin",
            ...     entryPage="dashboard",
            ...     searchEngineIndex=False,
            ...     primaryBaseURL="",
            ...     steamAPIKey="",
            ...     dnsCache=False,
            ...     tlsExpiryNotifyDays=[
            ...         7,
            ...         14,
            ...         21
            ...     ],
            ...     disableAuth=False,
            ...     trustProxy=False
            ... )
            {
                'msg': 'Saved'
            }
        """

        if not tlsExpiryNotifyDays:
            tlsExpiryNotifyDays = [7, 14, 21]

        data = {
            "checkUpdate": checkUpdate,
            "checkBeta": checkBeta,
            "keepDataPeriodDays": keepDataPeriodDays,
            "serverTimezone": serverTimezone,
            "entryPage": entryPage,
            "searchEngineIndex": searchEngineIndex,
            "primaryBaseURL": primaryBaseURL,
            "steamAPIKey": steamAPIKey,
            "dnsCache": dnsCache,
            "tlsExpiryNotifyDays": tlsExpiryNotifyDays,
            "disableAuth": disableAuth
        }
        if parse_version(self.version) >= parse_version("1.18"):
            data.update({
                "trustProxy": trustProxy
            })
        return self._call('setSettings', (data, password))

    def change_password(self, old_password: str, new_password: str) -> dict:
        """
        Change password.

        :param str old_password: Old password
        :param str new_password: New password
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.change_password(
            ...     old_password="secret123",
            ...     new_password="321terces"
            ... )
            {
                'msg': 'Password has been updated successfully.'
            }
        """
        return self._call('changePassword', {
            "currentPassword": old_password,
            "newPassword": new_password,
        })

    def upload_backup(self, json_data: str, import_handle: str = "skip") -> dict:
        """
        Import Backup.

        :param str json_data: Backup data as json string.
        :param str, optional import_handle: Choose "skip" if you want to skip every monitor or notification with the same name. "overwrite" will delete every existing monitor and notification. "keep" will keep both., defaults to "skip"
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> json_data = json.dumps({
            ...     "version": "1.17.1",
            ...     "notificationList": [],
            ...     "monitorList": [],
            ...     "proxyList": []
            ... })
            >>> api.upload_backup(
            ...     json_data=json_data,
            ...     import_handle="overwrite"
            ... )
            {
                'msg': 'Backup successfully restored.'
            }
        """
        if import_handle not in ["overwrite", "skip", "keep"]:
            raise ValueError()
        return self._call('uploadBackup', (json_data, import_handle))

    # 2FA

    def twofa_status(self) -> dict:
        """
        Get current 2FA status.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.twofa_status()
            {
                'status': False
            }
        """
        return self._call('twoFAStatus')

    def prepare_2fa(self, password: str) -> dict:
        """
        Prepare 2FA configuration.

        :param str password: Current password.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> password = "secret123"
            >>> r = api.prepare_2fa(password)
            >>> r
            {
                'uri': 'otpauth://totp/Uptime%20Kuma:admin?secret=NBGVQNSNNRXWQ3LJJN4DIWSWIIYW45CZJRXXORSNOY3USSKXO5RG4MDPI5ZUK5CWJFIFOVCBGZVG24TSJ5LDE2BTMRLXOZBSJF3TISA'
            }
            >>> uri = r["uri"]
            >>>
            >>> from urllib import parse
            >>> def parse_secret(uri):
            ...     query = parse.urlsplit(uri).query
            ...     params = dict(parse.parse_qsl(query))
            ...     return params["secret"]
            >>> secret = parse_secret(uri)
            >>> secret
            NBGVQNSNNRXWQ3LJJN4DIWSWIIYW45CZJRXXORSNOY3USSKXO5RG4MDPI5ZUK5CWJFIFOVCBGZVG24TSJ5LDE2BTMRLXOZBSJF3TISA
        """
        return self._call('prepare2FA', password)

    def verify_token(self, token: str, password: str) -> dict:
        """
        Verify the provided 2FA token.

        :param str token: 2FA token.
        :param str password: Current password.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> import pyotp
            >>> def generate_token(secret):
            ...     totp = pyotp.TOTP(secret)
            ...     return totp.now()
            >>> token = generate_token(secret)
            >>> token
            526564
            >>> api.verify_token(token, password)
            {
                'valid': True
            }
        """
        return self._call('verifyToken', (token, password))

    def save_2fa(self, password: str) -> dict:
        """
        Save the current 2FA configuration.

        :param str password: Current password.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.save_2fa(password)
            {
                'msg': '2FA Enabled.'
            }
        """
        return self._call('save2FA', password)

    def disable_2fa(self, password: str) -> dict:
        """
        Disable 2FA for this user.

        :param str password: Current password.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.disable_2fa(password)
            {
                'msg': '2FA Disabled.'
            }
        """
        return self._call('disable2FA', password)

    # login

    def login(self, username: str = None, password: str = None, token: str = "") -> dict:
        """
        Login.

        If username and password is not provided, auto login is performed if disableAuth is enabled.

        :param str, optional username: Username. Must be None if disableAuth is enabled., defaults to None
        :param str, optional password: Password. Must be None if disableAuth is enabled., defaults to None
        :param str, optional token: 2FA Token. Required if 2FA is enabled., defaults to ""
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> username = "admin"
            >>> password = "secret123"
            >>> api.login(username, password)
            {
                'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjcxMTk3MjkzfQ.lpho_LuKMnoltXOdA7-jZ98gXOU-UbEIuxMwMRm4Nz0'
            }
        """
        # autologin
        if username is None and password is None:
            with self.wait_for_event(Event.AUTO_LOGIN):
                return {}

        return self._call('login', {
            "username": username,
            "password": password,
            "token": token
        })

    def login_by_token(self, token: str) -> dict:
        """
        Login by token.

        :param str token: Login token generated by :meth:`~login`
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.login_by_token(token)
            {}
        """
        return self._call('loginByToken', token)

    def logout(self) -> None:
        """
        Logout.

        :return: The server response.
        :rtype: None
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.logout()
            None
        """
        return self._call('logout')

    # setup

    def need_setup(self) -> bool:
        """
        Check if the server has already been set up.

        :return: The server response.
        :rtype: bool
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.need_setup()
            True
        """
        return self._call('needSetup')

    def setup(self, username: str, password: str) -> dict:
        """
        Set up the server.

        :param str username: Username
        :param str password: Password
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.setup(username, password)
            {
                'msg': 'Added Successfully.'
            }
        """
        return self._call("setup", (username, password))

    # database

    def get_database_size(self) -> dict:
        """
        Get database size.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_database_size()
            {
                'size': 61440
            }
        """
        return self._call('getDatabaseSize')

    def shrink_database(self) -> dict:
        """
        Shrink database.

        Trigger database VACUUM for SQLite. If your database is created after 1.10.0, AUTO_VACUUM is already enabled and this action is not needed.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.shrink_database()
            {}
        """
        return self._call('shrinkDatabase')

    # docker host

    def get_docker_hosts(self) -> list:
        """
        Get all docker hosts.

        :return: All docker hosts.
        :rtype: list

        Example::

            >>> api.get_docker_hosts()
            [
                {
                    'dockerDaemon': '/var/run/docker.sock',
                    'dockerType': 'socket',
                    'id': 1,
                    'name': 'name 1',
                    'userID': 1
                }
            ]
        """
        r = self._get_event_data(Event.DOCKER_HOST_LIST)
        return r

    def get_docker_host(self, id_: int) -> dict:
        """
        Get a docker host.

        :param int id_: Id of the docker host to get.
        :return: The docker host.
        :rtype: dict
        :raises UptimeKumaException: If the docker host does not exist.

        Example::

            >>> api.get_docker_host(1)
            {
                'dockerDaemon': '/var/run/docker.sock',
                'dockerType': 'socket',
                'id': 1,
                'name': 'name 1',
                'userID': 1
            }
        """
        docker_hosts = self.get_docker_hosts()
        for docker_host in docker_hosts:
            if docker_host["id"] == id_:
                return docker_host
        raise UptimeKumaException("docker host does not exist")

    @append_docstring(docker_host_docstring("test"))
    def test_docker_host(self, **kwargs) -> dict:
        """
        Test a docker host.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.test_docker_host(
            ...     name="name 1",
            ...     dockerType=DockerType.SOCKET,
            ...     dockerDaemon="/var/run/docker.sock"
            ... )
            {
                'msg': 'Connected Successfully. Amount of containers: 10'
            }
        """
        data = _build_docker_host_data(**kwargs)
        return self._call('testDockerHost', data)

    @append_docstring(docker_host_docstring("add"))
    def add_docker_host(self, **kwargs) -> dict:
        """
        Add a docker host.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_docker_host(
            ...     name="name 1",
            ...     dockerType=DockerType.SOCKET,
            ...     dockerDaemon="/var/run/docker.sock"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_docker_host_data(**kwargs)
        _convert_docker_host_input(data)
        with self.wait_for_event(Event.DOCKER_HOST_LIST):
            return self._call('addDockerHost', (data, None))

    @append_docstring(docker_host_docstring("edit"))
    def edit_docker_host(self, id_: int, **kwargs) -> dict:
        """
        Edit a docker host.

        :param int id_: Id of the docker host to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_docker_host(1,
            ...     name="name 2"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = self.get_docker_host(id_)
        data.update(kwargs)
        _convert_docker_host_input(data)
        with self.wait_for_event(Event.DOCKER_HOST_LIST):
            return self._call('addDockerHost', (data, id_))

    def delete_docker_host(self, id_: int) -> dict:
        """
        Delete a docker host.

        :param int id_: Id of the docker host to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_docker_host(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.DOCKER_HOST_LIST):
            return self._call('deleteDockerHost', id_)

    # maintenance

    def get_maintenances(self) -> list:
        """
        Get all maintenances.

        :return: All maintenances.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_maintenances()
            [
                {
                    "id": 1,
                    "title": "title",
                    "description": "description",
                    "strategy": "single",
                    "intervalDay": 1,
                    "active": true,
                    "dateRange": [
                        "2022-12-27 15:39:00",
                        "2022-12-30 15:39:00"
                    ],
                    "timeRange": [
                        {
                            "hours": 2,
                            "minutes": 0,
                            "seconds": 0
                        },
                        {
                            "hours": 3,
                            "minutes": 0,
                            "seconds": 0
                        }
                    ],
                    "weekdays": [],
                    "daysOfMonth": [],
                    "timeslotList": [
                        {
                            "id": 1,
                            "startDate": "2022-12-27 14:39:00",
                            "endDate": "2022-12-30 14:39:00",
                            "startDateServerTimezone": "2022-12-27 15:39",
                            "endDateServerTimezone": "2022-12-30 15:39",
                            "serverTimezoneOffset": "+01:00"
                        }
                    ],
                    "status": "under-maintenance"
                }
            ]
        """
        return list(self._get_event_data(Event.MAINTENANCE_LIST).values())

    def get_maintenance(self, id_: int) -> dict:
        """
        Get a maintenance.

        :param int id_: Id of the maintenance to get.
        :return: The maintenance.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_maintenance(1)
            {
                "id": 1,
                "title": "title",
                "description": "description",
                "strategy": "single",
                "intervalDay": 1,
                "active": true,
                "dateRange": [
                    "2022-12-27 15:39:00",
                    "2022-12-30 15:39:00"
                ],
                "timeRange": [
                    {
                        "hours": 2,
                        "minutes": 0,
                        "seconds": 0
                    },
                    {
                        "hours": 3,
                        "minutes": 0,
                        "seconds": 0
                    }
                ],
                "weekdays": [],
                "daysOfMonth": [],
                "timeslotList": [
                    {
                        "id": 1,
                        "startDate": "2022-12-27 14:39:00",
                        "endDate": "2022-12-30 14:39:00",
                        "startDateServerTimezone": "2022-12-27 15:39",
                        "endDateServerTimezone": "2022-12-30 15:39",
                        "serverTimezoneOffset": "+01:00"
                    }
                ],
                "status": "under-maintenance"
            }
        """
        return self._call('getMaintenance', id_)["maintenance"]

    @append_docstring(maintenance_docstring("add"))
    def add_maintenance(self, **kwargs) -> dict:
        """
        Adds a maintenance.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example (strategy: :attr:`~.MaintenanceStrategy.MANUAL`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.MANUAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 00:00:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.SINGLE`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.SINGLE,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:36:00",
            ...         "2022-12-29 22:36:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.RECURRING_INTERVAL`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_INTERVAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:37:00",
            ...         "2022-12-31 22:37:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.RECURRING_WEEKDAY`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_WEEKDAY,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:38:00",
            ...         "2022-12-31 22:38:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[
            ...         1,
            ...         3,
            ...         5,
            ...         0
            ...     ],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.RECURRING_DAY_OF_MONTH`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_DAY_OF_MONTH,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:39:00",
            ...         "2022-12-31 22:39:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[
            ...         1,
            ...         10,
            ...         20,
            ...         30,
            ...         "lastDay2"
            ...     ]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }
        """
        data = _build_maintenance_data(**kwargs)
        _check_arguments_maintenance(data)
        return self._call('addMaintenance', data)

    @append_docstring(maintenance_docstring("edit"))
    def edit_maintenance(self, id_: int, **kwargs) -> dict:
        """
        Edits a maintenance.

        :param int id_: Id of the maintenance to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_maintenance(1,
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_INTERVAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:37:00",
            ...         "2022-12-31 22:37:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Saved.",
                "maintenanceID": 1
            }
        """
        maintenance = self.get_maintenance(id_)
        maintenance.update(kwargs)
        _check_arguments_maintenance(maintenance)
        return self._call('editMaintenance', maintenance)

    def delete_maintenance(self, id_: int) -> dict:
        """
        Deletes a maintenance.

        :param int id_: Id of the maintenance to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_maintenance(1)
            {
                "msg": "Deleted Successfully."
            }
        """
        return self._call('deleteMaintenance', id_)

    def pause_maintenance(self, id_: int) -> dict:
        """
        Pauses a maintenance.

        :param int id_: Id of the maintenance to pause.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.pause_maintenance(1)
            {
                "msg": "Paused Successfully."
            }
        """
        return self._call('pauseMaintenance', id_)

    def resume_maintenance(self, id_: int) -> dict:
        """
        Resumes a maintenance.

        :param int id_: Id of the maintenance to resume.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.resume_maintenance(1)
            {
                "msg": "Resume Successfully"
            }
        """
        return self._call('resumeMaintenance', id_)

    def get_monitor_maintenance(self, id_: int) -> list:
        """
        Gets all monitors of a maintenance.

        :param int id_: Id of the maintenance to get the monitors from.
        :return: All monitors of the maintenance.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor_maintenance(1)
            [
                {
                    "id": 1,
                    "name": "monitor 1"
                },
                {
                    "id": 2,
                    "name": "monitor 2"
                }
            ]
        """
        return self._call('getMonitorMaintenance', id_)["monitors"]

    def add_monitor_maintenance(
            self,
            id_: int,
            monitors: list,
    ) -> dict:
        """
        Adds monitors to a maintenance.

        :param int id_: Id of the maintenance to add the monitors to.
        :param list monitors: The list of monitors to add to the maintenance.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> monitors = [
            ...     {
            ...         "id": 1,
            ...         "name": "monitor 1"
            ...     },
            ...     {
            ...         "id": 2,
            ...         "name": "monitor 2"
            ...     }
            ... ]
            >>> api.add_monitor_maintenance(1, monitors)
            {
                "msg": "Added Successfully."
            }
        """
        return self._call('addMonitorMaintenance', (id_, monitors))

    def get_status_page_maintenance(self, id_: int) -> list:
        """
        Gets all status pages of a maintenance.

        :param int id_: Id of the maintenance to get the status pages from.
        :return: All status pages of the maintenance.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_status_page_maintenance(1)
            [
                {
                    "id": 1,
                    "title": "test"
                }
            ]
        """
        return self._call('getMaintenanceStatusPage', id_)["statusPages"]

    def add_status_page_maintenance(
            self,
            id_: int,
            status_pages: list,
    ) -> dict:
        """
        Adds status pages to a maintenance.

        :param int id_: Id of the maintenance to add the monitors to.
        :param list status_pages: The list of status pages to add to the maintenance.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> status_pages = [
            ...     {
            ...         "id": 1,
            ...         "name": "status page 1"
            ...     },
            ...     {
            ...         "id": 2,
            ...         "name": "status page 2"
            ...     }
            ... ]
            >>> api.add_status_page_maintenance(1, status_pages)
            {
                "msg": "Added Successfully."
            }
        """
        return self._call('addMaintenanceStatusPage', (id_, status_pages))

    # api key

    def get_api_keys(self) -> list:
        """
        Get all api keys.

        :return: All api keys.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_api_key_list()
            [
                {
                    "id": 1,
                    "name": "test",
                    "userID": 1,
                    "createdDate": "2023-03-20 11:15:05",
                    "active": False,
                    "expires": null,
                    "status": "inactive"
                },
                {
                    "id": 2,
                    "name": "test2",
                    "userID": 1,
                    "createdDate": "2023-03-20 11:20:29",
                    "active": True,
                    "expires": "2023-03-30 12:20:00",
                    "status": "active"
                }
            ]
        """

        # TODO: replace with getAPIKeyList?

        r = self._get_event_data(Event.API_KEY_LIST)
        int_to_bool(r, ["active"])
        return r

    def get_api_key(self, id_: int) -> dict:
        """
        Get an api key.

        :param int id_: Id of the api key to get.
        :return: The api key.
        :rtype: dict
        :raises UptimeKumaException: If the api key does not exist.

        Example::

            >>> api.get_api_key(1)
            {
                "id": 1,
                "name": "test",
                "userID": 1,
                "createdDate": "2023-03-20 11:15:05",
                "active": False,
                "expires": null,
                "status": "inactive"
            }
        """
        api_keys = self.get_api_keys()
        for api_key in api_keys:
            if api_key["id"] == id_:
                return api_key
        raise UptimeKumaException("notification does not exist")

    def add_api_key(self, name: str, expires: str, active: bool) -> dict:
        """
        Adds a new api key.

        :param str name: Name of the api key.
        :param str expires: Expiration date of the api key. Set to ``None`` to disable expiration.
        :param bool active: True to activate api key.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_api_key(
            ...     name="test",
            ...     expires="2023-03-30 12:20:00",
            ...     active=True
            ... )
            {
              "msg": "Added Successfully.",
              "key": "uk1_9XPRjV7ilGj9CvWRKYiBPq9GLtQs74UzTxKfCxWY",
              "keyID": 1
            }

            >>> api.add_api_key(
            ...     name="test2",
            ...     expires=None,
            ...     active=True
            ... )
            {
              "msg": "Added Successfully.",
              "key": "uk2_jsB9H1Zmt9eEjycNFMTKgse1B0Vfvb944H4_aRqW",
              "keyID": 2
            }
        """
        data = {
            "name": name,
            "expires": expires,
            "active": 1 if active else 0
        }
        with self.wait_for_event(Event.API_KEY_LIST):
            return self._call('addAPIKey', data)

    def enable_api_key(self, id_: int) -> dict:
        """
        Enable an api key.

        :param int id_: Id of the api key to enable.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.enable_api_key(1)
            {
              "msg": "Enabled Successfully"
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST):
            return self._call('enableAPIKey', id_)

    def disable_api_key(self, id_: int) -> dict:
        """
        Disable an api key.

        :param int id_: Id of the api key to disable.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.disable_api_key(1)
            {
              "msg": "Disabled Successfully."
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST):
            return self._call('disableAPIKey', id_)

    def delete_api_key(self, id_: int) -> dict:
        """
        Enable an api key.

        :param int id_: Id of the api key to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_api_key(1)
            {
              "msg": "Deleted Successfully."
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST):
            return self._call('deleteAPIKey', id_)
