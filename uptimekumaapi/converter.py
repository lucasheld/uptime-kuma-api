# socket -> python
params_map_monitor = {
    "type": "type_",
    "interval": "heartbeat_interval",
    "retryInterval": "heartbeat_retry_interval",
    "maxretries": "retries",
    "notificationIDList": "notification_ids",
    "upsideDown": "upside_down_mode",
    "expiryNotification": "certificate_expiry_notification",
    "ignoreTls": "ignore_tls_error",
    "maxredirects": "max_redirects",
    "accepted_statuscodes": "accepted_status_codes",
    "proxyId": "proxy_id",
    "method": "http_method",
    "body": "http_body",
    "headers": "http_headers",
    "authMethod": "auth_method",
    "basicauth-user": "auth_user",
    "basicauth-pass": "auth_pass",
    "basicauth-domain": "auth_domain",
    "basicauth-workstation": "auth_workstation",
    "mqttUsername": "mqtt_username",
    "mqttPassword": "mqtt_password",
    "mqttTopic": "mqtt_topic",
    "mqttSuccessMessage": "mqtt_success_message",
    "databaseConnectionString": "sqlserver_connection_string",
    "sqlserverQuery": "sqlserver_query"
}

params_map_notification = {
    "type": "type_",
    "isDefault": "default"
}

params_map_proxy = {
    "applyExisting": "apply_existing"
}

params_map_status_page = {
    "id": "id_",
    "slug": "slug",
    "title": "title",
    "description": "description",
    "icon": "img_data_url",
    "theme": "dark_theme",
    "published": "published",
    "showTags": "show_tags",
    "domainNameList": "domain_name_list",
    "customCSS": "custom_css",
    "footerText": "footer_text",
    "showPoweredBy": "show_powered_by"
}


def _convert_to_from_socket(params_map: dict[str, str], params: list[dict] | dict, to_socket=False):
    if type(params) == list:
        out = []
        params_list = params
        for params in params_list:
            params_py = _convert_to_from_socket(params_map, params, to_socket)
            out.append(params_py)
    else:
        if to_socket:
            params_map = {v: k for k, v in params_map.items()}
        out = {}
        for key, value in params.items():
            key = params_map.get(key, key)
            out[key] = value
    return out


def convert_from_socket(params_map, params):
    return _convert_to_from_socket(params_map, params)


def convert_to_socket(params_map, params):
    return _convert_to_from_socket(params_map, params, to_socket=True)
