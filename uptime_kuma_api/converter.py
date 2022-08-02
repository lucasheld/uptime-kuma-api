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
    "sqlserverQuery": "sqlserver_query",
    "authDomain": "auth_domain",
    "authWorkstation": "auth_workstation",
    "databaseQuery": "database_query",
    "monitorID": "monitor_id"
}

params_map_notification = {
    "type": "type_",
    "isDefault": "default",
    "userId": "user_id",
    "applyExisting": "apply_existing",
}

params_map_notification_providers = {
    'alerta': 'alerta',
    'AliyunSMS': 'aliyun_sms',
    'apprise': 'apprise',
    'Bark': 'bark',
    'clicksendsms': 'clicksendsms',
    'DingDing': 'ding_ding',
    'discord': 'discord',
    'Feishu': 'feishu',
    'GoogleChat': 'google_chat',
    'gorush': 'gorush',
    'gotify': 'gotify',
    'line': 'line',
    'lunasea': 'lunasea',
    'matrix': 'matrix',
    'mattermost': 'mattermost',
    'ntfy': 'ntfy',
    'octopush': 'octopush',
    'OneBot': 'one_bot',
    'PagerDuty': 'pager_duty',
    'promosms': 'promosms',
    'pushbullet': 'pushbullet',
    'PushDeer': 'push_deer',
    'pushover': 'pushover',
    'pushy': 'pushy',
    'rocket.chat': 'rocket_chat',
    'serwersms': 'serwersms',
    'signal': 'signal',
    'slack': 'slack',
    'smtp': 'smtp',
    'stackfield': 'stackfield',
    'teams': 'teams',
    'PushByTechulus': 'push_by_techulus',
    'telegram': 'telegram',
    'webhook': 'webhook',
    'WeCom': 'we_com'
}

params_map_notification_provider_options = {
    'alerta': {
        'alertaApiEndpoint': 'alerta_api_endpoint',
        'alertaApiKey': 'alerta_api_key',
        'alertaEnvironment': 'alerta_environment',
        'alertaAlertState': 'alerta_alert_state',
        'alertaRecoverState': 'alerta_recover_state',
    },
    'aliyun_sms': {
        'phonenumber': 'aliyun_sms_phonenumber',
        'templateCode': 'aliyun_sms_template_code',
        'signName': 'aliyun_sms_sign_name',
        'accessKeyId': 'aliyun_sms_access_key_id',
        'secretAccessKey': 'aliyun_sms_secret_access_key',
    },
    'apprise': {
        'appriseURL': 'apprise_url',
        'title': 'apprise_title',
    },
    'bark': {
        'barkEndpoint': 'bark_endpoint',
    },
    'clicksendsms': {
        'clicksendsmsLogin': 'clicksendsms_login',
        'clicksendsmsPassword': 'clicksendsms_password',
        'clicksendsmsToNumber': 'clicksendsms_to_number',
        'clicksendsmsSenderName': 'clicksendsms_sender_name',
    },
    'ding_ding': {
        'webHookUrl': 'ding_ding_web_hook_url',
        'secretKey': 'ding_ding_secret_key',
    },
    'discord': {
        'discordUsername': 'discord_username',
        'discordWebhookUrl': 'discord_webhook_url',
        'discordPrefixMessage': 'discord_prefix_message',
    },
    'feishu': {
        'feishuWebHookUrl': 'feishu_web_hook_url',
    },
    'google_chat': {
        'googleChatWebhookURL': 'google_chat_chat_webhook_url',
    },
    'gorush': {
        'gorushDeviceToken': 'gorush_device_token',
        'gorushPlatform': 'gorush_platform',
        'gorushTitle': 'gorush_title',
        'gorushPriority': 'gorush_priority',
        'gorushRetry': 'gorush_retry',
        'gorushTopic': 'gorush_topic',
        'gorushServerURL': 'gorush_server_url',
    },
    'gotify': {
        'gotifyserverurl': 'gotify_serverurl',
        'gotifyapplicationToken': 'gotify_application_token',
        'gotifyPriority': 'gotify_priority',
    },
    'line': {
        'lineChannelAccessToken': 'line_channel_access_token',
        'lineUserID': 'line_user_id',
    },
    'lunasea': {
        'lunaseaDevice': 'lunasea_device',
    },
    'matrix': {
        'internalRoomId': 'matrix_internal_room_id',
        'accessToken': 'matrix_access_token',
        'homeserverUrl': 'matrix_homeserver_url',
    },
    'mattermost': {
        'mattermostusername': 'mattermost_username',
        'mattermostWebhookUrl': 'mattermost_webhook_url',
        'mattermostchannel': 'mattermost_channel',
        'mattermosticonemo': 'mattermost_iconemo',
        'mattermosticonurl': 'mattermost_iconurl',
    },
    'ntfy': {
        'ntfyserverurl': 'ntfy_serverurl',
        'ntfytopic': 'ntfy_topic',
        'ntfyPriority': 'ntfy_priority',
    },
    'octopush': {
        'octopushVersion': 'octopush_version',
        'octopushAPIKey': 'octopush_apikey',
        'octopushLogin': 'octopush_login',
        'octopushPhoneNumber': 'octopush_phone_number',
        'octopushSMSType': 'octopush_smstype',
        'octopushSenderName': 'octopush_sender_name',
        'octopushDMLogin': 'octopush_dmlogin',
        'octopushDMAPIKey': 'octopush_dmapikey',
        'octopushDMPhoneNumber': 'octopush_dmphone_number',
        'octopushDMSenderName': 'octopush_dmsender_name',
        'octopushDMSMSType': 'octopush_dmsmstype',
    },
    'one_bot': {
        'httpAddr': 'one_bot_http_addr',
        'accessToken': 'one_bot_access_token',
        'msgType': 'one_bot_msg_type',
        'recieverId': 'one_bot_reciever_id',
    },
    'pager_duty': {
        'pagerdutyAutoResolve': 'pager_duty_duty_auto_resolve',
        'pagerdutyIntegrationUrl': 'pager_duty_duty_integration_url',
        'pagerdutyPriority': 'pager_duty_duty_priority',
        'pagerdutyIntegrationKey': 'pager_duty_duty_integration_key',
    },
    'promosms': {
        'promosmsLogin': 'promosms_login',
        'promosmsPassword': 'promosms_password',
        'promosmsPhoneNumber': 'promosms_phone_number',
        'promosmsSMSType': 'promosms_smstype',
        'promosmsSenderName': 'promosms_sender_name',
    },
    'pushbullet': {
        'pushbulletAccessToken': 'pushbullet_access_token',
    },
    'push_deer': {
        'pushdeerKey': 'push_deer_deer_key',
    },
    'pushover': {
        'pushoveruserkey': 'pushover_userkey',
        'pushoverapptoken': 'pushover_apptoken',
        'pushoversounds': 'pushover_sounds',
        'pushoverpriority': 'pushover_priority',
        'pushovertitle': 'pushover_title',
        'pushoverdevice': 'pushover_device',
    },
    'pushy': {
        'pushyAPIKey': 'pushy_apikey',
        'pushyToken': 'pushy_token',
    },
    'rocket_chat': {
        'rocketchannel': 'rocket_chat_channel',
        'rocketusername': 'rocket_chat_username',
        'rocketiconemo': 'rocket_chat_iconemo',
        'rocketwebhookURL': 'rocket_chat_webhook_url',
        'rocketbutton': 'rocket_chat_button',
    },
    'serwersms': {
        'serwersmsUsername': 'serwersms_username',
        'serwersmsPassword': 'serwersms_password',
        'serwersmsPhoneNumber': 'serwersms_phone_number',
        'serwersmsSenderName': 'serwersms_sender_name',
    },
    'signal': {
        'signalNumber': 'signal_number',
        'signalRecipients': 'signal_recipients',
        'signalURL': 'signal_url',
    },
    'slack': {
        'slackbutton': 'slack_button',
        'slackchannel': 'slack_channel',
        'slackusername': 'slack_username',
        'slackiconemo': 'slack_iconemo',
        'slackwebhookURL': 'slack_webhook_url',
    },
    'smtp': {
        'smtpHost': 'smtp_host',
        'smtpPort': 'smtp_port',
        'smtpSecure': 'smtp_secure',
        'smtpIgnoreTLSError': 'smtp_ignore_tlserror',
        'smtpDkimDomain': 'smtp_dkim_domain',
        'smtpDkimKeySelector': 'smtp_dkim_key_selector',
        'smtpDkimPrivateKey': 'smtp_dkim_private_key',
        'smtpDkimHashAlgo': 'smtp_dkim_hash_algo',
        'smtpDkimheaderFieldNames': 'smtp_dkimheader_field_names',
        'smtpDkimskipFields': 'smtp_dkimskip_fields',
        'smtpUsername': 'smtp_username',
        'smtpPassword': 'smtp_password',
        'customSubject': 'smtp_custom_subject',
        'smtpFrom': 'smtp_from',
        'smtpCC': 'smtp_cc',
        'smtpBCC': 'smtp_bcc',
        'smtpTo': 'smtp_to',
    },
    'stackfield': {
        'stackfieldwebhookURL': 'stackfield_webhook_url',
    },
    'teams': {
        'webhookUrl': 'teams_webhook_url',
    },
    'push_by_techulus': {
        'pushAPIKey': 'push_by_techulus_apikey',
    },
    'telegram': {
        'telegramBotToken': 'telegram_bot_token',
        'telegramChatID': 'telegram_chat_id',
    },
    'webhook': {
        'webhookContentType': 'webhook_content_type',
        'webhookURL': 'webhook_url',
    },
    'we_com': {
        'weComBotKey': 'we_com_com_bot_key',
    },
}

params_map_proxy = {
    "applyExisting": "apply_existing",
    "createdDate": "created_date",
    "userId": "user_id"
}

params_map_status_page = {
    "id": "id_",
    "slug": "slug",
    "title": "title",
    "description": "description",
    "icon": "img_data_url",
    "published": "published",
    "showTags": "show_tags",
    "domainNameList": "domain_name_list",
    "customCSS": "custom_css",
    "footerText": "footer_text",
    "showPoweredBy": "show_powered_by",
    "createdDate": "created_date"
}

params_map_info = {
    "latestVersion": "latest_version",
    "primaryBaseURL": "primary_base_url"
}

params_map_settings = {
    # about
    "checkUpdate": "check_update",
    "checkBeta": "check_beta",
    # monitor history
    "keepDataPeriodDays": "keep_data_period_days",
    # general
    "entryPage": "entry_page",
    "searchEngineIndex": "search_engine_index",
    "primaryBaseURL": "primary_base_url",
    "steamAPIKey": "steam_api_key",
    # notifications
    "tlsExpiryNotifyDays": "tls_expiry_notify_days",
    # security
    "disableAuth": "disable_auth"
}


def _convert_to_from_socket(params_map: dict, params, to_socket=False):
    if type(params) == list:
        out = []
        params_list = params
        for params in params_list:
            params_py = _convert_to_from_socket(params_map, params, to_socket)
            out.append(params_py)
    else:
        if to_socket:
            params_map = {v: k for k, v in params_map.items()}
        if type(params) == dict:
            out = {}
            for key, value in params.items():
                key = params_map.get(key, key)
                out[key] = value
        else:
            return params_map.get(params, params)
    return out


def convert_from_socket(params_map, params):
    return _convert_to_from_socket(params_map, params)


def convert_to_socket(params_map, params):
    return _convert_to_from_socket(params_map, params, to_socket=True)


def get_params_map_notification(type_py=None, type_sock=None):
    if not type_py:
        type_py = convert_from_socket(params_map_notification_providers, type_sock)
    return {
        **params_map_notification,
        **params_map_notification_providers,
        **params_map_notification_provider_options[type_py]
    }
