def append_docstring(value):
    def _doc(func):
        # inserts the value into the existing docstring before the :return: line
        split_value = ":return:"
        splitted = func.__doc__.split(split_value)
        part1 = splitted[0]
        line = [i for i in part1.split("\n") if i][0]
        indent = len(line) - len(line.lstrip())
        line_start = " " * indent
        part2 = split_value + line_start.join(splitted[1:])
        func.__doc__ = part1 + "\n" + line_start + value + "\n" + line_start + part2
        return func

    return _doc


def monitor_docstring(mode) -> str:
    return f"""
        :param MonitorType{", optional" if mode == "edit" else ""} type: Monitor Type
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name
        :param int, optional interval: Heartbeat Interval, defaults to 60
        :param int, optional retryInterval: Retry every X seconds, defaults to 60
        :param int, optional resendInterval: Resend every X times, defaults to 0
        :param int, optional maxretries: Retries. Maximum retries before the service is marked as down and a notification is sent., defaults to 0
        :param bool, optional upsideDown: Upside Down Mode. Flip the status upside down. If the service is reachable, it is DOWN., defaults to False
        :param list, optional notificationIDList: Notifications, defaults to None
        :param str, optional url: URL, defaults to None
        :param bool, optional expiryNotification: Certificate Expiry Notification, defaults to False
        :param bool, optional ignoreTls: Ignore TLS/SSL error for HTTPS websites, defaults to False
        :param int, optional maxredirects: Max. Redirects. Maximum number of redirects to follow. Set to 0 to disable redirects., defaults to 10
        :param list, optional accepted_statuscodes: Accepted Status Codes. Select status codes which are considered as a successful response., defaults to None
        :param int, optional proxyId: Proxy, defaults to None
        :param str, optional method: Method, defaults to "GET"
        :param str, optional body: Body, defaults to None
        :param str, optional headers: Headers, defaults to None
        :param AuthMethod, optional authMethod: Method, defaults to :attr:`~.AuthMethod.NONE`
        :param str, optional basic_auth_user: Username, defaults to None
        :param str, optional basic_auth_pass: Password, defaults to None
        :param str, optional authDomain: Domain, defaults to None
        :param str, optional authWorkstation: Workstation, defaults to None
        :param str, optional keyword: Keyword. Search keyword in plain HTML or JSON response. The search is case-sensitive., defaults to None
        :param str, optional hostname: Hostname, defaults to None
        :param int, optional port: Port, defaults to 53
        :param str, optional dns_resolve_server: Resolver Server, defaults to "1.1.1.1"
        :param str, optional dns_resolve_type: Resource Record Type, defaults to "A"
        :param str, optional mqttUsername: MQTT Username, defaults to None
        :param str, optional mqttPassword: MQTT Password, defaults to None
        :param str, optional mqttTopic: MQTT Topic, defaults to None
        :param str, optional mqttSuccessMessage: MQTT Success Message, defaults to None
        :param str, optional databaseConnectionString: Connection String, defaults to None
        :param str, optional databaseQuery: Query, defaults to None
        :param str, optional docker_container: Container Name / ID, defaults to ""
        :param int, optional docker_host: Docker Host, defaults to None
        :param str, optional radiusUsername: Radius Username, defaults to None
        :param str, optional radiusPassword: Radius Password, defaults to None
        :param str, optional radiusSecret: Radius Secret. Shared Secret between client and server., defaults to None
        :param str, optional radiusCalledStationId: Called Station Id. Identifier of the called device., defaults to None
        :param str, optional radiusCallingStationId: Calling Station Id. Identifier of the calling device., defaults to None
    """

def notification_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name        
        :param NotificationType{", optional" if mode == "edit" else ""} type: Notification Type        
        :param bool, optional isDefault: Default enabled. This notification will be enabled by default for new monitors. You can still disable the notification separately for each monitor., defaults to False
        :param bool, optional applyExisting: Apply on all existing monitors, defaults to False
        
        :param str, optional alertaApiEndpoint: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`
        :param str, optional alertaApiKey: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`
        :param str, optional alertaEnvironment: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`
        :param str, optional alertaAlertState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`
        :param str, optional alertaRecoverState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`
        :param str, optional phonenumber: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`
        :param str, optional templateCode: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`
        :param str, optional signName: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`
        :param str, optional accessKeyId: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`
        :param str, optional secretAccessKey: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`
        :param str, optional appriseURL: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`
        :param str, optional title: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`
        :param str, optional clicksendsmsLogin: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`
        :param str, optional clicksendsmsPassword: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`
        :param str, optional clicksendsmsToNumber: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`
        :param str, optional clicksendsmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`
        :param str, optional webHookUrl: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`
        :param str, optional secretKey: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`
        :param str, optional discordUsername: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`
        :param str, optional discordWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`
        :param str, optional discordPrefixMessage: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`
        :param str, optional feishuWebHookUrl: Notification option for ``type`` :attr:`~.NotificationType.FEISHU`
        :param str, optional googleChatWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`
        :param str, optional gorushDeviceToken: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushPlatform: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushTitle: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushPriority: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushRetry: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushTopic: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gorushServerURL: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`
        :param str, optional gotifyserverurl: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`
        :param str, optional gotifyapplicationToken: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`
        :param int, optional gotifyPriority: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`
        :param str, optional lineChannelAccessToken: Notification option for ``type`` :attr:`~.NotificationType.LINE`
        :param str, optional lineUserID: Notification option for ``type`` :attr:`~.NotificationType.LINE`
        :param str, optional lunaseaDevice: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`
        :param str, optional internalRoomId: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`
        :param str, optional accessToken: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`
        :param str, optional homeserverUrl: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`
        :param str, optional mattermostusername: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`
        :param str, optional mattermostWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`
        :param str, optional mattermostchannel: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`
        :param str, optional mattermosticonemo: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`
        :param str, optional mattermosticonurl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`
        :param str, optional httpAddr: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`
        :param str, optional accessToken: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`
        :param str, optional msgType: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`
        :param str, optional recieverId: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`
        :param str, optional pagerdutyAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`
        :param str, optional pagerdutyIntegrationUrl: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`
        :param str, optional pagerdutyPriority: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`
        :param str, optional pagerdutyIntegrationKey: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`
        :param str, optional promosmsLogin: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`
        :param str, optional promosmsPassword: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`
        :param str, optional promosmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`
        :param str, optional promosmsSMSType: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`
        :param str, optional promosmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`
        :param str, optional pushbulletAccessToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHBULLET`
        :param str, optional pushdeerKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHDEER`
        :param str, optional pushoveruserkey: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushoverapptoken: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushoversounds: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushoverpriority: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushovertitle: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushoverdevice: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`
        :param str, optional pushyAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`
        :param str, optional pushyToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`
        :param str, optional rocketchannel: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`
        :param str, optional rocketusername: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`
        :param str, optional rocketiconemo: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`
        :param str, optional rocketwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`
        :param str, optional rocketbutton: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`
        :param str, optional serwersmsUsername: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`
        :param str, optional serwersmsPassword: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`
        :param str, optional serwersmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`
        :param str, optional serwersmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`
        :param str, optional signalNumber: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`
        :param str, optional signalRecipients: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`
        :param str, optional signalURL: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`
        :param str, optional slackbutton: Notification option for ``type`` :attr:`~.NotificationType.SLACK`
        :param str, optional slackchannel: Notification option for ``type`` :attr:`~.NotificationType.SLACK`
        :param str, optional slackusername: Notification option for ``type`` :attr:`~.NotificationType.SLACK`
        :param str, optional slackiconemo: Notification option for ``type`` :attr:`~.NotificationType.SLACK`
        :param str, optional slackwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SLACK`
        :param str, optional smtpHost: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param int, optional smtpPort: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpSecure: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpIgnoreTLSError: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimDomain: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimKeySelector: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimPrivateKey: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimHashAlgo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimheaderFieldNames: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpDkimskipFields: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpUsername: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpPassword: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional customSubject: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpFrom: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpBCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional smtpTo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`
        :param str, optional stackfieldwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.STACKFIELD`
        :param str, optional pushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`
        :param str, optional telegramBotToken: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`
        :param str, optional telegramChatID: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`
        :param str, optional webhookContentType: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`
        :param str, optional webhookURL: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`
        :param str, optional weComBotKey: Notification option for ``type`` :attr:`~.NotificationType.WECOM`
        :param str, optional alertNowWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ALERTNOW`
        :param str, optional homeAssistantUrl: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`
        :param str, optional longLivedAccessToken: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`
        :param str, optional lineNotifyAccessToken: Notification option for ``type`` :attr:`~.NotificationType.LINENOTIFY`
        :param str, optional barkEndpoint: Notification option for ``type`` :attr:`~.NotificationType.BARK`
        :param str, optional barkGroup: Notification option for ``type`` :attr:`~.NotificationType.BARK`
        :param str, optional barkSound: Notification option for ``type`` :attr:`~.NotificationType.BARK`
        :param str, optional goAlertBaseURL: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`
        :param str, optional goAlertToken: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`
        :param str, optional octopushVersion: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushLogin: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushSMSType: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushSenderName: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushDMLogin: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushDMAPIKey: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushDMPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushDMSenderName: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional octopushDMSMSType: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`
        :param str, optional serverChanSendKey: Notification option for ``type`` :attr:`~.NotificationType.SERVERCHAN`
        :param str, optional smsmanagerApiKey: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`
        :param str, optional numbers: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`
        :param str, optional messageType: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`
        :param str, optional squadcastWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SQUADCAST`
        :param str, optional webhookUrl: Notification option for ``type`` :attr:`~.NotificationType.TEAMS`
        :param str, optional freemobileUser: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`
        :param str, optional freemobilePass: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`
        :param str, optional ntfyusername: Notification option for ``type`` :attr:`~.NotificationType.NTFY`
        :param str, optional ntfypassword: Notification option for ``type`` :attr:`~.NotificationType.NTFY`
        :param str, optional ntfytopic: Notification option for ``type`` :attr:`~.NotificationType.NTFY`
        :param int, optional ntfyPriority: Notification option for ``type`` :attr:`~.NotificationType.NTFY`
        :param str, optional ntfyserverurl: Notification option for ``type`` :attr:`~.NotificationType.NTFY`
    """

def proxy_docstring(mode) -> str:
    return f"""
        :param ProxyProtocol{", optional" if mode == "edit" else ""} protocol: Proxy Protocol
        :param str{", optional" if mode == "edit" else ""} host: Proxy Server
        :param str{", optional" if mode == "edit" else ""} port: Port
        :param bool, optional auth: Proxy server has authentication, defaults to False
        :param str, optional username: User, defaults to None
        :param str, optional password: Password, defaults to None
        :param bool, optional active: Enabled. This proxy will not effect on monitor requests until it is activated. You can control temporarily disable the proxy from all monitors by activation status., defaults to True
        :param bool, optional default: Set As Default. This proxy will be enabled by default for new monitors. You can still disable the proxy separately for each monitor., , defaults to False
        :param bool, optional applyExisting: Apply on all existing monitors, defaults to False
    """

def docker_host_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name
        :param DockerType{", optional" if mode == "edit" else ""} dockerType: Connection Type
        :param str, optional dockerDaemon: Docker Daemon, defaults to None
    """
