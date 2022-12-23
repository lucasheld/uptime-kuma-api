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
from . import MonitorType
from . import NotificationType, notification_provider_options, notification_provider_conditions
from . import ProxyProtocol
from . import UptimeKumaException
from .docstrings import append_docstring, monitor_docstring, notification_docstring, proxy_docstring, \
    docker_host_docstring


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
            Event.AUTO_LOGIN: None
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
        return deepcopy(self._event_data[event])

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

    def _event_heartbeat_list(self, id_, data, bool_) -> None:
        if self._event_data[Event.HEARTBEAT_LIST] is None:
            self._event_data[Event.HEARTBEAT_LIST] = []
        self._event_data[Event.HEARTBEAT_LIST].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_important_heartbeat_list(self, id_, data, bool_) -> None:
        if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = []
        self._event_data[Event.IMPORTANT_HEARTBEAT_LIST].append({
            "id": id_,
            "data": data,
            "bool": bool_,
        })

    def _event_avg_ping(self, id_, data) -> None:
        if self._event_data[Event.AVG_PING] is None:
            self._event_data[Event.AVG_PING] = []
        self._event_data[Event.AVG_PING].append({
            "id": id_,
            "data": data,
        })

    def _event_uptime(self, monitor_id, duration, uptime) -> None:
        if self._event_data[Event.UPTIME] is None:
            self._event_data[Event.UPTIME] = []
        self._event_data[Event.UPTIME].append({
            "id": monitor_id,
            "duration": duration,
            "uptime": uptime,
        })

    def _event_heartbeat(self, data) -> None:
        if self._event_data[Event.HEARTBEAT] is None:
            self._event_data[Event.HEARTBEAT] = []
        self._event_data[Event.HEARTBEAT].append(data)

    def _event_info(self, data) -> None:
        self._event_data[Event.INFO] = data

    def _event_cert_info(self, id_, data) -> None:
        if self._event_data[Event.CERT_INFO] is None:
            self._event_data[Event.CERT_INFO] = []
        self._event_data[Event.CERT_INFO].append({
            "id": id_,
            "data": data,
        })

    def _event_docker_host_list(self, data) -> None:
        self._event_data[Event.DOCKER_HOST_LIST] = data

    def _event_auto_login(self) -> None:
        self._event_data[Event.AUTO_LOGIN] = True

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

        # PORT, PING, DNS, STEAM, MQTT
        data.update({
            "hostname": hostname,
        })

        # PORT, DNS, STEAM, MQTT
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
                    'id': 1,
                    'name': 'Google',
                    'url': 'https://google.com',
                    'method': 'GET',
                    'hostname': None,
                    'port': 53,
                    'maxretries': 0,
                    'weight': 2000,
                    'active': True,
                    'type': 'http',
                    'interval': 60,
                    'retryInterval': 60,
                    'resendInterval': 0,
                    'keyword': None,
                    'expiryNotification': False,
                    'ignoreTls': False,
                    'upsideDown': False,
                    'maxredirects': 10,
                    'accepted_statuscodes': [
                        '200-299'
                    ],
                    'dns_resolve_type': 'A',
                    'dns_resolve_server': '1.1.1.1',
                    'dns_last_result': None,
                    'pushToken': None,
                    'docker_container': None,
                    'docker_host': None,
                    'proxyId': None,
                    'notificationIDList': [],
                    'tags': [],
                    'mqttUsername': None,
                    'mqttPassword': None,
                    'mqttTopic': None,
                    'mqttSuccessMessage': None,
                    'databaseConnectionString': None,
                    'databaseQuery': None,
                    'authMethod': '',
                    'authWorkstation': None,
                    'authDomain': None,
                    'radiusUsername': None,
                    'radiusPassword': None,
                    'radiusCalledStationId': None,
                    'radiusCallingStationId': None,
                    'radiusSecret': None,
                    'headers': None,
                    'body': None,
                    'basic_auth_user': None,
                    'basic_auth_pass': None
                }
            ]
        """
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
                'id': 1,
                'name': 'Google',
                'url': 'https://google.com',
                'method': 'GET',
                'hostname': None,
                'port': 53,
                'maxretries': 0,
                'weight': 2000,
                'active': True,
                'type': 'http',
                'interval': 60,
                'retryInterval': 60,
                'resendInterval': 0,
                'keyword': None,
                'expiryNotification': False,
                'ignoreTls': False,
                'upsideDown': False,
                'maxredirects': 10,
                'accepted_statuscodes': [
                    '200-299'
                ],
                'dns_resolve_type': 'A',
                'dns_resolve_server': '1.1.1.1',
                'dns_last_result': None,
                'pushToken': None,
                'docker_container': None,
                'docker_host': None,
                'proxyId': None,
                'notificationIDList': [],
                'tags': [],
                'mqttUsername': None,
                'mqttPassword': None,
                'mqttTopic': None,
                'mqttSuccessMessage': None,
                'databaseConnectionString': None,
                'databaseQuery': None,
                'authMethod': '',
                'authWorkstation': None,
                'authDomain': None,
                'radiusUsername': None,
                'radiusPassword': None,
                'radiusCalledStationId': None,
                'radiusCallingStationId': None,
                'radiusSecret': None,
                'headers': None,
                'body': None,
                'basic_auth_user': None,
                'basic_auth_pass': None
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

            >>> api.edit_monitor(1, interval=20)
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

        :param id tag_id: Id of the tag to remove.
        :param id monitor_id: Id of monitor to remove the tag from.
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

            >>> api.edit_notification(
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
                'publicGroupList': [
                    {
                        'id': 1,
                        'monitorList': [
                            {
                                'id': 1,
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
        return {
            **config,
            "incident": r2["incident"],
            "publicGroupList": r2["publicGroupList"]
        }

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
            ...     theme="light",
            ...     published=True,
            ...     showTags=False,
            ...     domainNameList=[],
            ...     customCSS="",
            ...     footerText=None,
            ...     showPoweredBy=False,
            ...     icon="/icon.svg",
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

    def get_heartbeats(self) -> list:
        """
        Get heartbeats.

        :return: The heartbeats.
        :rtype: list

        Example::

            >>> api.get_heartbeats()
            [
                {
                    'bool': False,
                    'data': [
                        {
                            'down_count': 0,
                            'duration': 0,
                            'id': 1,
                            'important': True,
                            'monitor_id': 1,
                            'msg': 'connect ECONNREFUSED 127.0.0.1:80',
                            'ping': None,
                            'status': False,
                            'time': '2022-12-15 16:51:41.782'
                        },
                        {
                            'down_count': 0,
                            'duration': 60,
                            'id': 2,
                            'important': False,
                            'monitor_id': 1,
                            'msg': 'connect ECONNREFUSED 127.0.0.1:80',
                            'ping': None,
                            'status': False,
                            'time': '2022-12-15 16:52:41.799'
                        },
                        ...
                    ],
                    'id': '1'
                }
            ]
        """
        r = self._get_event_data(Event.HEARTBEAT_LIST)
        for i in r:
            int_to_bool(i["data"], ["important", "status"])
        return r

    def get_important_heartbeats(self) -> list:
        """
        Get important heartbeats.

        :return: The important heartbeats.
        :rtype: list

        Example::

            >>> api.get_important_heartbeats()
            [
                {
                    'bool': False,
                    'data': [
                        {
                            'duration': 0,
                            'important': True,
                            'monitorID': 1,
                            'msg': 'connect ECONNREFUSED 127.0.0.1:80',
                            'ping': None,
                            'status': False,
                            'time': '2022-12-15 16:51:41.782'
                        }
                    ],
                    'id': '1'
                }
            ]
        """
        r = self._get_event_data(Event.IMPORTANT_HEARTBEAT_LIST)
        for i in r:
            int_to_bool(i["data"], ["important", "status"])
        return r

    def get_heartbeat(self) -> list:
        """
        Get heartbeat.

        :return: The heartbeat.
        :rtype: list

        Example::

            >>> api.get_heartbeat()
            [
                {
                    'duration': 60,
                    'important': False,
                    'monitorID': 1,
                    'msg': 'connect ECONNREFUSED 127.0.0.1:80',
                    'status': False,
                    'time': '2022-12-15 17:17:42.099'
                }
            ]
        """
        r = self._get_event_data(Event.HEARTBEAT)
        int_to_bool(r, ["important", "status"])
        return r

    # avg ping

    def avg_ping(self) -> list:
        """
        Get average ping.

        :return: The average ping.
        :rtype: list

        Example::

            >>> api.avg_ping()
            [
                {
                    'id': '1',
                    'data': 67
                }
            ]
        """
        return self._get_event_data(Event.AVG_PING)

    # cert info

    def cert_info(self) -> list:
        """
        Get certificate info.

        :return: Certificate info.
        :rtype: list

        Example::

            >>> api.cert_info()
            [
                {
                    'id': '2',
                    'data': '{"valid":true,"certInfo":{"subject":{"C":"US","ST":"California","L":"San Francisco","O":"Cloudflare, Inc.","CN":"cloudflare-dns.com"},"issuer":{"C":"US","O":"DigiCert Inc","CN":"DigiCert TLS Hybrid ECC SHA384 2020 CA1"},"subjectaltname":"DNS:cloudflare-dns.com, DNS:*.cloudflare-dns.com, DNS:one.one.one.one, IP Address:1.0.0.1, IP Address:1.1.1.1, IP Address:162.159.36.1, IP Address:162.159.46.1, IP Address:2606:4700:4700:0:0:0:0:1001, IP Address:2606:4700:4700:0:0:0:0:1111, IP Address:2606:4700:4700:0:0:0:0:64, IP Address:2606:4700:4700:0:0:0:0:6400","infoAccess":{"OCSP - URI":["http://ocsp.digicert.com"],"CA Issuers - URI":["http://cacerts.digicert.com/DigiCertTLSHybridECCSHA3842020CA1-1.crt"]},"bits":256,"pubkey":{"type":"Buffer","data":[4,252,62,81,239,116,29,198,218,120,186,174,165,138,74,221,217,11,230,226,91,87,49,87,222,211,191,182,217,138,59,79,210,84,84,136,207,189,46,101,231,102,235,197,223,208,49,84,82,167,44,238,18,134,163,154,102,193,234,6,121,3,186,27,240]},"asn1Curve":"prime256v1","nistCurve":"P-256","valid_from":"Sep 13 00:00:00 2022 GMT","valid_to":"Sep 13 23:59:59 2023 GMT","fingerprint":"D1:D4:67:E7:BC:0E:AC:CD:C8:87:A6:12:B8:B2:BC:15:C1:69:04:6B","fingerprint256":"66:67:73:19:84:78:03:0C:56:FB:23:76:8E:48:19:C2:B7:5C:32:2C:D3:BE:A4:A8:34:6B:B0:3C:22:8D:4F:18","fingerprint512":"C2:76:3A:C5:AC:64:76:BB:BF:9F:AB:3A:B9:04:55:06:A4:8D:13:67:08:26:10:A0:FE:22:B5:E2:26:E0:67:1F:EC:17:B7:C2:59:18:1E:7B:46:99:7C:54:A4:9E:4B:C6:58:B4:16:B4:88:6F:0C:5B:60:D1:78:AD:E9:CE:28:1C","ext_key_usage":["1.3.6.1.5.5.7.3.1","1.3.6.1.5.5.7.3.2"],"serialNumber":"0D1C7AF28E5F2717DBB27F410820BDF7","raw":{"type":"Buffer","data":[48,130,5,247,48,130,5,125,160,3,2,1,2,2,16,13,28,122,242,142,95,39,23,219,178,127,65,8,32,189,247,48,10,6,8,42,134,72,206,61,4,3,3,48,86,49,11,48,9,6,3,85,4,6,19,2,85,83,49,21,48,19,6,3,85,4,10,19,12,68,105,103,105,67,101,114,116,32,73,110,99,49,48,48,46,6,3,85,4,3,19,39,68,105,103,105,67,101,114,116,32,84,76,83,32,72,121,98,114,105,100,32,69,67,67,32,83,72,65,51,56,52,32,50,48,50,48,32,67,65,49,48,30,23,13,50,50,48,57,49,51,48,48,48,48,48,48,90,23,13,50,51,48,57,49,51,50,51,53,57,53,57,90,48,114,49,11,48,9,6,3,85,4,6,19,2,85,83,49,19,48,17,6,3,85,4,8,19,10,67,97,108,105,102,111,114,110,105,97,49,22,48,20,6,3,85,4,7,19,13,83,97,110,32,70,114,97,110,99,105,115,99,111,49,25,48,23,6,3,85,4,10,19,16,67,108,111,117,100,102,108,97,114,101,44,32,73,110,99,46,49,27,48,25,6,3,85,4,3,19,18,99,108,111,117,100,102,108,97,114,101,45,100,110,115,46,99,111,109,48,89,48,19,6,7,42,134,72,206,61,2,1,6,8,42,134,72,206,61,3,1,7,3,66,0,4,252,62,81,239,116,29,198,218,120,186,174,165,138,74,221,217,11,230,226,91,87,49,87,222,211,191,182,217,138,59,79,210,84,84,136,207,189,46,101,231,102,235,197,223,208,49,84,82,167,44,238,18,134,163,154,102,193,234,6,121,3,186,27,240,163,130,4,15,48,130,4,11,48,31,6,3,85,29,35,4,24,48,22,128,20,10,188,8,41,23,140,165,57,109,122,14,206,51,199,46,179,237,251,195,122,48,29,6,3,85,29,14,4,22,4,20,210,99,186,148,214,84,127,76,133,20,8,58,28,133,86,41,239,89,143,204,48,129,166,6,3,85,29,17,4,129,158,48,129,155,130,18,99,108,111,117,100,102,108,97,114,101,45,100,110,115,46,99,111,109,130,20,42,46,99,108,111,117,100,102,108,97,114,101,45,100,110,115,46,99,111,109,130,15,111,110,101,46,111,110,101,46,111,110,101,46,111,110,101,135,4,1,0,0,1,135,4,1,1,1,1,135,4,162,159,36,1,135,4,162,159,46,1,135,16,38,6,71,0,71,0,0,0,0,0,0,0,0,0,16,1,135,16,38,6,71,0,71,0,0,0,0,0,0,0,0,0,17,17,135,16,38,6,71,0,71,0,0,0,0,0,0,0,0,0,0,100,135,16,38,6,71,0,71,0,0,0,0,0,0,0,0,0,100,0,48,14,6,3,85,29,15,1,1,255,4,4,3,2,7,128,48,29,6,3,85,29,37,4,22,48,20,6,8,43,6,1,5,5,7,3,1,6,8,43,6,1,5,5,7,3,2,48,129,155,6,3,85,29,31,4,129,147,48,129,144,48,70,160,68,160,66,134,64,104,116,116,112,58,47,47,99,114,108,51,46,100,105,103,105,99,101,114,116,46,99,111,109,47,68,105,103,105,67,101,114,116,84,76,83,72,121,98,114,105,100,69,67,67,83,72,65,51,56,52,50,48,50,48,67,65,49,45,49,46,99,114,108,48,70,160,68,160,66,134,64,104,116,116,112,58,47,47,99,114,108,52,46,100,105,103,105,99,101,114,116,46,99,111,109,47,68,105,103,105,67,101,114,116,84,76,83,72,121,98,114,105,100,69,67,67,83,72,65,51,56,52,50,48,50,48,67,65,49,45,49,46,99,114,108,48,62,6,3,85,29,32,4,55,48,53,48,51,6,6,103,129,12,1,2,2,48,41,48,39,6,8,43,6,1,5,5,7,2,1,22,27,104,116,116,112,58,47,47,119,119,119,46,100,105,103,105,99,101,114,116,46,99,111,109,47,67,80,83,48,129,133,6,8,43,6,1,5,5,7,1,1,4,121,48,119,48,36,6,8,43,6,1,5,5,7,48,1,134,24,104,116,116,112,58,47,47,111,99,115,112,46,100,105,103,105,99,101,114,116,46,99,111,109,48,79,6,8,43,6,1,5,5,7,48,2,134,67,104,116,116,112,58,47,47,99,97,99,101,114,116,115,46,100,105,103,105,99,101,114,116,46,99,111,109,47,68,105,103,105,67,101,114,116,84,76,83,72,121,98,114,105,100,69,67,67,83,72,65,51,56,52,50,48,50,48,67,65,49,45,49,46,99,114,116,48,9,6,3,85,29,19,4,2,48,0,48,130,1,126,6,10,43,6,1,4,1,214,121,2,4,2,4,130,1,110,4,130,1,106,1,104,0,117,0,232,62,208,218,62,245,6,53,50,231,87,40,188,137,107,201,3,211,203,209,17,107,236,235,105,225,119,125,109,6,189,110,0,0,1,131,57,10,85,95,0,0,4,3,0,70,48,68,2,32,19,225,125,163,221,153,90,255,11,159,65,167,55,234,243,77,130,35,3,9,67,221,172,45,200,156,200,78,60,52,50,247,2,32,53,26,206,34,249,6,72,61,141,13,201,235,157,108,146,194,3,186,89,214,148,238,143,113,56,232,38,0,18,118,72,15,0,119,0,53,207,25,27,191,177,108,87,191,15,173,76,109,66,203,187,182,39,32,38,81,234,63,225,42,239,168,3,195,59,214,76,0,0,1,131,57,10,85,167,0,0,4,3,0,72,48,70,2,33,0,162,182,69,93,222,50,248,3,60,156,189,95,73,27,139,121,27,251,57,104,115,83,67,131,78,119,138,55,210,86,118,226,2,33,0,132,146,242,202,94,171,22,244,80,236,141,149,240,132,54,176,168,153,184,117,5,158,160,74,247,194,22,246,142,35,28,79,0,118,0,179,115,119,7,225,132,80,248,99,134,214,5,169,220,17,9,74,121,45,177,103,12,11,135,220,240,3,14,121,54,165,154,0,0,1,131,57,10,85,247,0,0,4,3,0,71,48,69,2,33,0,154,1,140,175,47,65,114,139,87,11,28,28,7,144,34,177,195,215,254,128,187,251,210,181,170,206,96,95,15,98,14,223,2,32,10,140,75,206,219,38,223,184,94,103,214,158,104,124,206,196,212,21,154,83,59,128,31,7,246,107,128,107,7,24,134,160,48,10,6,8,42,134,72,206,61,4,3,3,3,104,0,48,101,2,48,25,215,154,121,110,105,204,25,111,221,195,208,54,200,84,208,78,244,111,29,70,192,202,47,251,34,25,149,248,112,117,11,89,217,173,22,49,110,26,38,27,22,223,113,13,85,205,74,2,49,0,234,220,46,9,152,254,177,251,7,245,49,95,182,124,26,190,56,217,197,57,154,106,11,157,143,84,103,19,75,193,18,134,38,42,17,109,152,211,145,29,2,235,225,119,118,113,55,142]},"issuerCertificate":{"subject":{"C":"US","O":"DigiCert Inc","CN":"DigiCert TLS Hybrid ECC SHA384 2020 CA1"},"issuer":{"C":"US","O":"DigiCert Inc","OU":"www.digicert.com","CN":"DigiCert Global Root CA"},"infoAccess":{"OCSP - URI":["http://ocsp.digicert.com"],"CA Issuers - URI":["http://cacerts.digicert.com/DigiCertGlobalRootCA.crt"]},"bits":384,"pubkey":{"type":"Buffer","data":[4,193,27,198,154,91,152,217,164,41,160,233,212,4,181,219,235,166,178,108,85,192,255,237,152,198,73,47,6,39,81,203,191,112,193,5,122,195,177,157,135,137,186,173,180,19,23,201,168,180,131,200,184,144,209,204,116,53,54,60,131,114,176,181,208,247,34,105,200,241,128,196,123,64,143,207,104,135,38,92,57,137,241,77,145,77,218,137,139,228,3,195,67,229,191,47,115]},"asn1Curve":"secp384r1","nistCurve":"P-384","valid_from":"Apr 14 00:00:00 2021 GMT","valid_to":"Apr 13 23:59:59 2031 GMT","fingerprint":"AE:C1:3C:DD:5E:A6:A3:99:8A:EC:14:AC:33:1A:D9:6B:ED:BB:77:0F","fingerprint256":"F7:A9:A1:B2:FD:96:4A:3F:26:70:BD:66:8D:56:1F:B7:C5:5D:3A:A9:AB:83:91:E7:E1:69:70:2D:B8:A3:DB:CF","fingerprint512":"A9:0D:FF:FB:4B:1C:A3:01:3F:B2:D2:78:3F:AB:A7:B8:03:1E:25:08:08:19:28:63:76:D4:12:EB:97:D3:A5:66:2D:C0:5D:4E:C4:0A:77:29:89:72:0D:F8:2A:7B:67:92:65:56:6D:13:75:F0:0C:85:50:C6:83:03:B8:6A:C0:35","ext_key_usage":["1.3.6.1.5.5.7.3.1","1.3.6.1.5.5.7.3.2"],"serialNumber":"07F2F35C87A877AF7AEFE947993525BD","raw":{"type":"Buffer","data":[48,130,4,23,48,130,2,255,160,3,2,1,2,2,16,7,242,243,92,135,168,119,175,122,239,233,71,153,53,37,189,48,13,6,9,42,134,72,134,247,13,1,1,12,5,0,48,97,49,11,48,9,6,3,85,4,6,19,2,85,83,49,21,48,19,6,3,85,4,10,19,12,68,105,103,105,67,101,114,116,32,73,110,99,49,25,48,23,6,3,85,4,11,19,16,119,119,119,46,100,105,103,105,99,101,114,116,46,99,111,109,49,32,48,30,6,3,85,4,3,19,23,68,105,103,105,67,101,114,116,32,71,108,111,98,97,108,32,82,111,111,116,32,67,65,48,30,23,13,50,49,48,52,49,52,48,48,48,48,48,48,90,23,13,51,49,48,52,49,51,50,51,53,57,53,57,90,48,86,49,11,48,9,6,3,85,4,6,19,2,85,83,49,21,48,19,6,3,85,4,10,19,12,68,105,103,105,67,101,114,116,32,73,110,99,49,48,48,46,6,3,85,4,3,19,39,68,105,103,105,67,101,114,116,32,84,76,83,32,72,121,98,114,105,100,32,69,67,67,32,83,72,65,51,56,52,32,50,48,50,48,32,67,65,49,48,118,48,16,6,7,42,134,72,206,61,2,1,6,5,43,129,4,0,34,3,98,0,4,193,27,198,154,91,152,217,164,41,160,233,212,4,181,219,235,166,178,108,85,192,255,237,152,198,73,47,6,39,81,203,191,112,193,5,122,195,177,157,135,137,186,173,180,19,23,201,168,180,131,200,184,144,209,204,116,53,54,60,131,114,176,181,208,247,34,105,200,241,128,196,123,64,143,207,104,135,38,92,57,137,241,77,145,77,218,137,139,228,3,195,67,229,191,47,115,163,130,1,130,48,130,1,126,48,18,6,3,85,29,19,1,1,255,4,8,48,6,1,1,255,2,1,0,48,29,6,3,85,29,14,4,22,4,20,10,188,8,41,23,140,165,57,109,122,14,206,51,199,46,179,237,251,195,122,48,31,6,3,85,29,35,4,24,48,22,128,20,3,222,80,53,86,209,76,187,102,240,163,226,27,27,195,151,178,61,209,85,48,14,6,3,85,29,15,1,1,255,4,4,3,2,1,134,48,29,6,3,85,29,37,4,22,48,20,6,8,43,6,1,5,5,7,3,1,6,8,43,6,1,5,5,7,3,2,48,118,6,8,43,6,1,5,5,7,1,1,4,106,48,104,48,36,6,8,43,6,1,5,5,7,48,1,134,24,104,116,116,112,58,47,47,111,99,115,112,46,100,105,103,105,99,101,114,116,46,99,111,109,48,64,6,8,43,6,1,5,5,7,48,2,134,52,104,116,116,112,58,47,47,99,97,99,101,114,116,115,46,100,105,103,105,99,101,114,116,46,99,111,109,47,68,105,103,105,67,101,114,116,71,108,111,98,97,108,82,111,111,116,67,65,46,99,114,116,48,66,6,3,85,29,31,4,59,48,57,48,55,160,53,160,51,134,49,104,116,116,112,58,47,47,99,114,108,51,46,100,105,103,105,99,101,114,116,46,99,111,109,47,68,105,103,105,67,101,114,116,71,108,111,98,97,108,82,111,111,116,67,65,46,99,114,108,48,61,6,3,85,29,32,4,54,48,52,48,11,6,9,96,134,72,1,134,253,108,2,1,48,7,6,5,103,129,12,1,1,48,8,6,6,103,129,12,1,2,1,48,8,6,6,103,129,12,1,2,2,48,8,6,6,103,129,12,1,2,3,48,13,6,9,42,134,72,134,247,13,1,1,12,5,0,3,130,1,1,0,71,89,129,127,212,27,31,176,113,246,152,93,24,186,152,71,152,176,126,118,43,234,255,26,139,172,38,179,66,141,49,230,74,232,25,208,239,218,20,231,215,20,146,161,146,242,167,46,45,175,251,29,246,251,83,176,138,63,252,216,22,10,233,176,46,182,165,11,24,144,53,38,162,218,246,168,183,50,252,149,35,75,198,69,185,196,207,228,124,238,230,201,248,144,189,114,227,153,195,29,11,5,124,106,151,109,178,171,2,54,216,194,188,44,1,146,63,4,163,139,117,17,199,185,41,188,17,208,134,186,146,188,38,249,101,200,55,205,38,246,134,19,12,4,170,137,229,120,177,193,78,121,188,118,163,11,81,228,197,208,158,106,254,26,44,86,174,6,54,39,163,115,28,8,125,147,50,208,194,68,25,218,141,244,14,123,29,40,3,43,9,138,118,202,119,220,135,122,172,123,82,38,85,167,114,15,157,210,136,79,254,177,33,197,26,161,170,57,245,86,219,194,132,196,53,31,112,218,187,70,240,134,191,100,0,196,62,247,159,70,27,157,35,5,185,125,179,79,15,169,69,58,227,116,48,152]},"issuerCertificate":{"subject":{"C":"US","O":"DigiCert Inc","OU":"www.digicert.com","CN":"DigiCert Global Root CA"},"issuer":{"C":"US","O":"DigiCert Inc","OU":"www.digicert.com","CN":"DigiCert Global Root CA"},"modulus":"E23BE11172DEA8A4D3A357AA50A28F0B7790C9A2A5EE12CE965B010920CC0193A74E30B753F743C46900579DE28D22DD870640008109CECE1B83BFDFCD3B7146E2D666C705B37627168F7B9E1E957DEEB748A308DAD6AF7A0C3906657F4A5D1FBC17F8ABBEEE28D7747F7A78995985686E5C23324BBF4EC0E85A6DE370BF7710BFFC01F685D9A844105832A97518D5D1A2BE47E2276AF49A33F84908608BD45FB43A84BFA1AA4A4C7D3ECF4F5F6C765EA04B37919EDC22E66DCE141A8E6ACBFECDB3146417C75B299E32BFF2EEFAD30B42D4ABB74132DA0CD4EFF881D5BB8D583FB51BE84928A270DA3104DDF7B216F24C0A4E07A8ED4A3D5EB57FA390C3AF27","bits":2048,"exponent":"0x10001","pubkey":{"type":"Buffer","data":[48,130,1,34,48,13,6,9,42,134,72,134,247,13,1,1,1,5,0,3,130,1,15,0,48,130,1,10,2,130,1,1,0,226,59,225,17,114,222,168,164,211,163,87,170,80,162,143,11,119,144,201,162,165,238,18,206,150,91,1,9,32,204,1,147,167,78,48,183,83,247,67,196,105,0,87,157,226,141,34,221,135,6,64,0,129,9,206,206,27,131,191,223,205,59,113,70,226,214,102,199,5,179,118,39,22,143,123,158,30,149,125,238,183,72,163,8,218,214,175,122,12,57,6,101,127,74,93,31,188,23,248,171,190,238,40,215,116,127,122,120,153,89,133,104,110,92,35,50,75,191,78,192,232,90,109,227,112,191,119,16,191,252,1,246,133,217,168,68,16,88,50,169,117,24,213,209,162,190,71,226,39,106,244,154,51,248,73,8,96,139,212,95,180,58,132,191,161,170,74,76,125,62,207,79,95,108,118,94,160,75,55,145,158,220,34,230,109,206,20,26,142,106,203,254,205,179,20,100,23,199,91,41,158,50,191,242,238,250,211,11,66,212,171,183,65,50,218,12,212,239,248,129,213,187,141,88,63,181,27,232,73,40,162,112,218,49,4,221,247,178,22,242,76,10,78,7,168,237,74,61,94,181,127,163,144,195,175,39,2,3,1,0,1]},"valid_from":"Nov 10 00:00:00 2006 GMT","valid_to":"Nov 10 00:00:00 2031 GMT","fingerprint":"A8:98:5D:3A:65:E5:E5:C4:B2:D7:D6:6D:40:C6:DD:2F:B1:9C:54:36","fingerprint256":"43:48:A0:E9:44:4C:78:CB:26:5E:05:8D:5E:89:44:B4:D8:4F:96:62:BD:26:DB:25:7F:89:34:A4:43:C7:01:61","fingerprint512":"53:B4:44:E5:65:18:32:01:A6:1E:EB:46:12:09:B2:DC:30:89:5E:EC:A4:87:23:8D:15:A0:26:73:5F:22:9A:81:9E:5B:19:CB:D7:E2:FA:27:68:AB:2A:64:F6:EB:CD:9D:1E:72:13:41:C9:ED:5D:D0:9F:C0:D5:E4:3D:68:BC:A7","serialNumber":"083BE056904246B1A1756AC95991C74A","raw":{"type":"Buffer","data":[48,130,3,175,48,130,2,151,160,3,2,1,2,2,16,8,59,224,86,144,66,70,177,161,117,106,201,89,145,199,74,48,13,6,9,42,134,72,134,247,13,1,1,5,5,0,48,97,49,11,48,9,6,3,85,4,6,19,2,85,83,49,21,48,19,6,3,85,4,10,19,12,68,105,103,105,67,101,114,116,32,73,110,99,49,25,48,23,6,3,85,4,11,19,16,119,119,119,46,100,105,103,105,99,101,114,116,46,99,111,109,49,32,48,30,6,3,85,4,3,19,23,68,105,103,105,67,101,114,116,32,71,108,111,98,97,108,32,82,111,111,116,32,67,65,48,30,23,13,48,54,49,49,49,48,48,48,48,48,48,48,90,23,13,51,49,49,49,49,48,48,48,48,48,48,48,90,48,97,49,11,48,9,6,3,85,4,6,19,2,85,83,49,21,48,19,6,3,85,4,10,19,12,68,105,103,105,67,101,114,116,32,73,110,99,49,25,48,23,6,3,85,4,11,19,16,119,119,119,46,100,105,103,105,99,101,114,116,46,99,111,109,49,32,48,30,6,3,85,4,3,19,23,68,105,103,105,67,101,114,116,32,71,108,111,98,97,108,32,82,111,111,116,32,67,65,48,130,1,34,48,13,6,9,42,134,72,134,247,13,1,1,1,5,0,3,130,1,15,0,48,130,1,10,2,130,1,1,0,226,59,225,17,114,222,168,164,211,163,87,170,80,162,143,11,119,144,201,162,165,238,18,206,150,91,1,9,32,204,1,147,167,78,48,183,83,247,67,196,105,0,87,157,226,141,34,221,135,6,64,0,129,9,206,206,27,131,191,223,205,59,113,70,226,214,102,199,5,179,118,39,22,143,123,158,30,149,125,238,183,72,163,8,218,214,175,122,12,57,6,101,127,74,93,31,188,23,248,171,190,238,40,215,116,127,122,120,153,89,133,104,110,92,35,50,75,191,78,192,232,90,109,227,112,191,119,16,191,252,1,246,133,217,168,68,16,88,50,169,117,24,213,209,162,190,71,226,39,106,244,154,51,248,73,8,96,139,212,95,180,58,132,191,161,170,74,76,125,62,207,79,95,108,118,94,160,75,55,145,158,220,34,230,109,206,20,26,142,106,203,254,205,179,20,100,23,199,91,41,158,50,191,242,238,250,211,11,66,212,171,183,65,50,218,12,212,239,248,129,213,187,141,88,63,181,27,232,73,40,162,112,218,49,4,221,247,178,22,242,76,10,78,7,168,237,74,61,94,181,127,163,144,195,175,39,2,3,1,0,1,163,99,48,97,48,14,6,3,85,29,15,1,1,255,4,4,3,2,1,134,48,15,6,3,85,29,19,1,1,255,4,5,48,3,1,1,255,48,29,6,3,85,29,14,4,22,4,20,3,222,80,53,86,209,76,187,102,240,163,226,27,27,195,151,178,61,209,85,48,31,6,3,85,29,35,4,24,48,22,128,20,3,222,80,53,86,209,76,187,102,240,163,226,27,27,195,151,178,61,209,85,48,13,6,9,42,134,72,134,247,13,1,1,5,5,0,3,130,1,1,0,203,156,55,170,72,19,18,10,250,221,68,156,79,82,176,244,223,174,4,245,121,121,8,163,36,24,252,75,43,132,192,45,185,213,199,254,244,193,31,88,203,184,109,156,122,116,231,152,41,171,17,181,227,112,160,161,205,76,136,153,147,140,145,112,226,171,15,28,190,147,169,255,99,213,228,7,96,211,163,191,157,91,9,241,213,142,227,83,244,142,99,250,63,167,219,180,102,223,98,102,214,209,110,65,141,242,45,181,234,119,74,159,157,88,226,43,89,192,64,35,237,45,40,130,69,62,121,84,146,38,152,224,128,72,168,55,239,240,214,121,96,22,222,172,232,14,205,110,172,68,23,56,47,73,218,225,69,62,42,185,54,83,207,58,80,6,247,46,232,196,87,73,108,97,33,24,213,4,173,120,60,44,58,128,107,167,235,175,21,20,233,216,137,193,185,56,108,226,145,108,138,255,100,185,119,37,87,48,192,27,36,163,225,220,233,223,71,124,181,180,36,8,5,48,236,45,189,11,191,69,191,80,185,169,243,235,152,1,18,173,200,136,198,152,52,95,141,10,60,198,233,213,149,149,109,222]},"issuerCertificate":null,"validTo":"2031-11-10T00:00:00.000Z","daysRemaining":3251},"validTo":"2031-04-13T23:59:59.000Z","daysRemaining":3041},"validTo":"2023-09-13T23:59:59.000Z","validFor":["cloudflare-dns.com","*.cloudflare-dns.com","one.one.one.one","1.0.0.1","1.1.1.1","162.159.36.1","162.159.46.1","2606:4700:4700:0:0:0:0:1001","2606:4700:4700:0:0:0:0:1111","2606:4700:4700:0:0:0:0:64","2606:4700:4700:0:0:0:0:6400"],"daysRemaining":272}}'
                }
            ]
        """
        return self._get_event_data(Event.CERT_INFO)

    # uptime

    def uptime(self) -> list:
        """
        Get monitor uptime.

        :return: Monitor uptime.
        :rtype: list

        Example::

            >>> api.uptime()
            [
                {
                    'id': '2',
                    'duration': 24,
                    'uptime': 1
                },
                {
                    'id': '2',
                    'duration': 720,
                    'uptime': 1
                }
            ]
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
                'version': '1.18.5',
                'latestVersion': '1.18.5',
                'primaryBaseURL': None
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

    # not working, monitor id required?
    # def edit_tag(self, id_: int, name: str, color: str):
    #     return self._call('editTag', {
    #         "id": id_,
    #         "name": name,
    #         "color": color
    #     })

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

    def add_tag(self, name: str, color: str) -> dict:
        """
        Add a tag.

        :param str name: Tag name
        :param str color: Tag color
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
        return self._call('addTag', {
            "name": name,
            "color": color,
            "new": True
        })["tag"]

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
                'checkUpdate': False,
                'checkBeta': False,
                'keepDataPeriodDays': 180,
                'entryPage': 'dashboard',
                'searchEngineIndex': False,
                'primaryBaseURL': '',
                'steamAPIKey': '',
                'tlsExpiryNotifyDays': [
                    7,
                    14,
                    21
                ],
                'disableAuth': False,
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
    ) -> dict:
        """
        Set settings.

        :param str, optional password: Password, defaults to None
        :param bool, optional checkUpdate: Show update if available, defaults to True
        :param bool, optional checkBeta: Also check beta release, defaults to False
        :param int, optional keepDataPeriodDays: Keep monitor history data for X days., defaults to 180
        :param str, optional entryPage: Entry Page, defaults to "dashboard"
        :param bool, optional searchEngineIndex: Search Engine Visibility, defaults to False
        :param str, optional primaryBaseURL: Primary Base URL, defaults to ""
        :param str, optional steamAPIKey: Steam API Key. For monitoring a Steam Game Server you need a Steam Web-API key., defaults to ""
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
            ...     entryPage="dashboard",
            ...     searchEngineIndex=False,
            ...     primaryBaseURL="",
            ...     steamAPIKey="",
            ...     tlsExpiryNotifyDays=[7, 14, 21],
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

            >>> api.edit_docker_host(1, name="name 2")
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
