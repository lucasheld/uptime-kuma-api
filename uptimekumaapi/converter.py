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
    "userId": "user_id"
}

params_map_notification_provider = {
    'alertaApiEndpoint': 'alerta_api_endpoint',
    'alertaApiKey': 'alerta_api_key',
    'alertaEnvironment': 'alerta_environment',
    'alertaAlertState': 'alerta_alert_state',
    'alertaRecoverState': 'alerta_recover_state',
    'phonenumber': 'aliyunsms_phonenumber',
    'templateCode': 'aliyunsms_template_code',
    'signName': 'aliyunsms_sign_name',
    'accessKeyId': 'aliyunsms_access_key_id',
    'secretAccessKey': 'aliyunsms_secret_access_key',
    'appriseURL': 'apprise_apprise_url',
    'title': 'apprise_title',
    'barkEndpoint': 'bark_endpoint',
    'clicksendsmsLogin': 'clicksendsms_login',
    'clicksendsmsPassword': 'clicksendsms_password',
    'clicksendsmsToNumber': 'clicksendsms_to_number',
    'clicksendsmsSenderName': 'clicksendsms_sender_name',
    'webHookUrl': 'dingding_web_hook_url',
    'secretKey': 'dingding_secret_key',
    'discordUsername': 'discord_username',
    'discordWebhookUrl': 'discord_webhook_url',
    'discordPrefixMessage': 'discord_prefix_message',
    'feishuWebHookUrl': 'feishu_web_hook_url',
    'googleChatWebhookURL': 'googlechat_webhook_url',
    'gorushDeviceToken': 'gorush_device_token',
    'gorushPlatform': 'gorush_platform',
    'gorushTitle': 'gorush_title',
    'gorushPriority': 'gorush_priority',
    'gorushRetry': 'gorush_retry',
    'gorushTopic': 'gorush_topic',
    'gorushServerURL': 'gorush_server_url',
    'gotifyserverurl': 'gotify_serverurl',
    'gotifyapplicationToken': 'gotify_application_token',
    'gotifyPriority': 'gotify_priority',
    'lineChannelAccessToken': 'line_channel_access_token',
    'lineUserID': 'line_user_id',
    'lunaseaDevice': 'lunasea_device',
    'internalRoomId': 'matrix_internal_room_id',
    'accessToken': 'onebot_access_token',
    'homeserverUrl': 'matrix_homeserver_url',
    'mattermostusername': 'mattermost_username',
    'mattermostWebhookUrl': 'mattermost_webhook_url',
    'mattermostchannel': 'mattermost_channel',
    'mattermosticonemo': 'mattermost_iconemo',
    'mattermosticonurl': 'mattermost_iconurl',
    'ntfyserverurl': 'ntfy_serverurl',
    'ntfytopic': 'ntfy_topic',
    'ntfyPriority': 'ntfy_priority',
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
    'httpAddr': 'onebot_http_addr',
    'msgType': 'onebot_msg_type',
    'recieverId': 'onebot_reciever_id',
    'pagerdutyAutoResolve': 'pagerduty_auto_resolve',
    'pagerdutyIntegrationUrl': 'pagerduty_integration_url',
    'pagerdutyPriority': 'pagerduty_priority',
    'pagerdutyIntegrationKey': 'pagerduty_integration_key',
    'promosmsLogin': 'promosms_login',
    'promosmsPassword': 'promosms_password',
    'promosmsPhoneNumber': 'promosms_phone_number',
    'promosmsSMSType': 'promosms_smstype',
    'promosmsSenderName': 'promosms_sender_name',
    'pushbulletAccessToken': 'pushbullet_access_token',
    'pushdeerKey': 'pushdeer_key',
    'pushoveruserkey': 'pushover_userkey',
    'pushoverapptoken': 'pushover_apptoken',
    'pushoversounds': 'pushover_sounds',
    'pushoverpriority': 'pushover_priority',
    'pushovertitle': 'pushover_title',
    'pushoverdevice': 'pushover_device',
    'pushyAPIKey': 'pushy_apikey',
    'pushyToken': 'pushy_token',
    'rocketchannel': 'rocketchat_channel',
    'rocketusername': 'rocketchat_username',
    'rocketiconemo': 'rocketchat_iconemo',
    'rocketwebhookURL': 'rocketchat_webhook_url',
    'rocketbutton': 'rocketchat_button',
    'serwersmsUsername': 'serwersms_username',
    'serwersmsPassword': 'serwersms_password',
    'serwersmsPhoneNumber': 'serwersms_phone_number',
    'serwersmsSenderName': 'serwersms_sender_name',
    'signalNumber': 'signal_number',
    'signalRecipients': 'signal_recipients',
    'signalURL': 'signal_url',
    'slackbutton': 'slack_button',
    'slackchannel': 'slack_channel',
    'slackusername': 'slack_username',
    'slackiconemo': 'slack_iconemo',
    'slackwebhookURL': 'slack_webhook_url',
    'smtpHost': 'smtp_smtp_host',
    'smtpPort': 'smtp_smtp_port',
    'smtpSecure': 'smtp_smtp_secure',
    'smtpIgnoreTLSError': 'smtp_smtp_ignore_tlserror',
    'smtpDkimDomain': 'smtp_smtp_dkim_domain',
    'smtpDkimKeySelector': 'smtp_smtp_dkim_key_selector',
    'smtpDkimPrivateKey': 'smtp_smtp_dkim_private_key',
    'smtpDkimHashAlgo': 'smtp_smtp_dkim_hash_algo',
    'smtpDkimheaderFieldNames': 'smtp_smtp_dkimheader_field_names',
    'smtpDkimskipFields': 'smtp_smtp_dkimskip_fields',
    'smtpUsername': 'smtp_smtp_username',
    'smtpPassword': 'smtp_smtp_password',
    'customSubject': 'smtp_custom_subject',
    'smtpFrom': 'smtp_smtp_from',
    'smtpCC': 'smtp_smtp_cc',
    'smtpBCC': 'smtp_smtp_bcc',
    'smtpTo': 'smtp_smtp_to',
    'stackfieldwebhookURL': 'stackfield_webhook_url',
    'webhookUrl': 'teams_webhook_url',
    'pushAPIKey': 'pushbytechulus_apikey',
    'telegramBotToken': 'telegram_bot_token',
    'telegramChatID': 'telegram_chat_id',
    'webhookContentType': 'webhook_content_type',
    'webhookURL': 'webhook_url',
    'weComBotKey': 'wecom_bot_key'
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
    "theme": "dark_theme",
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


def _convert_to_from_socket(params_map: dict[str, str], params: list[dict] | dict | str, to_socket=False):
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
