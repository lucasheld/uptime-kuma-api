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
        :param type: {"(optional) " if mode == "edit" else ""} Monitor Type
        :type type: MonitorType

        :param name: {"(optional) " if mode == "edit" else ""} Friendly Name
        :type name: str

        :param interval: (optional) Heartbeat Interval
        :type interval: int

        :param retryInterval: (optional) Retry every X seconds
        :type retryInterval: int

        :param resendInterval: (optional) Resend every X times
        :type resendInterval: int

        :param maxretries: (optional) Retries. Maximum retries before the service is marked as down and a notification is sent.
        :type maxretries: int

        :param upsideDown: (optional) Upside Down Mode. Flip the status upside down. If the service is reachable, it is DOWN.
        :type upsideDown: bool

        :param notificationIDList: (optional) Notifications
        :type notificationIDList: list

        :param url: (optional) URL
        :type url: str

        :param expiryNotification: (optional) Certificate Expiry Notification
        :type expiryNotification: bool

        :param ignoreTls: (optional) Ignore TLS/SSL error for HTTPS websites
        :type ignoreTls: bool

        :param maxredirects: (optional) Max. Redirects. Maximum number of redirects to follow. Set to 0 to disable redirects.
        :type maxredirects: int

        :param accepted_statuscodes: (optional) Accepted Status Codes. Select status codes which are considered as a successful response.
        :type accepted_statuscodes: list

        :param proxyId: (optional) Proxy
        :type proxyId: int

        :param method: (optional) Method
        :type method: str

        :param body: (optional) Body
        :type body: str

        :param headers: (optional) Headers
        :type headers: str

        :param authMethod: (optional) Method
        :type authMethod: AuthMethod

        :param basic_auth_user: (optional) Username
        :type basic_auth_user: str

        :param basic_auth_pass: (optional) Password
        :type basic_auth_pass: str

        :param authDomain: (optional) Domain
        :type authDomain: str

        :param authWorkstation: (optional) Workstation
        :type authWorkstation: str

        :param keyword: (optional) Keyword. Search keyword in plain HTML or JSON response. The search is case-sensitive.
        :type keyword: str

        :param hostname: (optional) Hostname
        :type hostname: str

        :param port: (optional) Port
        :type port: int

        :param dns_resolve_server: (optional) Resolver Server
        :type dns_resolve_server: str

        :param dns_resolve_type: (optional) Resource Record Type
        :type dns_resolve_type: str

        :param mqttUsername: (optional) MQTT Username
        :type mqttUsername: str

        :param mqttPassword: (optional) MQTT Password
        :type mqttPassword: str

        :param mqttTopic: (optional) MQTT Topic
        :type mqttTopic: str

        :param mqttSuccessMessage: (optional) MQTT Success Message
        :type mqttSuccessMessage: str

        :param databaseConnectionString: (optional) Connection String
        :type databaseConnectionString: str

        :param databaseQuery: (optional) Query
        :type databaseQuery: str

        :param docker_container: (optional) Container Name / ID
        :type docker_container: str

        :param docker_host: (optional) Docker Host
        :type docker_host: int

        :param radiusUsername: (optional) Radius Username
        :type radiusUsername: str

        :param radiusPassword: (optional) Radius Password
        :type radiusPassword: str

        :param radiusSecret: (optional) Radius Secret. Shared Secret between client and server.
        :type radiusSecret: str

        :param radiusCalledStationId: (optional) Called Station Id. Identifier of the called device.
        :type radiusCalledStationId: str

        :param radiusCallingStationId: (optional) Calling Station Id. Identifier of the calling device.
        :type radiusCallingStationId: str
    """

def notification_docstring(mode) -> str:
    return f"""
        :param name: {"(optional) " if mode == "edit" else ""} Friendly Name
        :type name: str
        
        :param type: {"(optional) " if mode == "edit" else ""} Notification Type
        :type type: NotificationType
        
        :param isDefault: (optional) Default enabled. This notification will be enabled by default for new monitors. You can still disable the notification separately for each monitor.
        :type isDefault: bool
        
        :param applyExisting: (optional) Apply on all existing monitors
        :type applyExisting: bool
        
        :param alertaApiEndpoint: (optional) Notification option for type NotificationType.ALERTA
        :type alertaApiEndpoint: str
        
        :param alertaApiKey: (optional) Notification option for type NotificationType.ALERTA
        :type alertaApiKey: str
        
        :param alertaEnvironment: (optional) Notification option for type NotificationType.ALERTA
        :type alertaEnvironment: str
        
        :param alertaAlertState: (optional) Notification option for type NotificationType.ALERTA
        :type alertaAlertState: str
        
        :param alertaRecoverState: (optional) Notification option for type NotificationType.ALERTA
        :type alertaRecoverState: str
        
        :param phonenumber: (optional) Notification option for type NotificationType.ALIYUNSMS
        :type phonenumber: str
        
        :param templateCode: (optional) Notification option for type NotificationType.ALIYUNSMS
        :type templateCode: str
        
        :param signName: (optional) Notification option for type NotificationType.ALIYUNSMS
        :type signName: str
        
        :param accessKeyId: (optional) Notification option for type NotificationType.ALIYUNSMS
        :type accessKeyId: str
        
        :param secretAccessKey: (optional) Notification option for type NotificationType.ALIYUNSMS
        :type secretAccessKey: str
        
        :param appriseURL: (optional) Notification option for type NotificationType.APPRISE
        :type appriseURL: str
        
        :param title: (optional) Notification option for type NotificationType.APPRISE
        :type title: str
        
        :param clicksendsmsLogin: (optional) Notification option for type NotificationType.CLICKSENDSMS
        :type clicksendsmsLogin: str
        
        :param clicksendsmsPassword: (optional) Notification option for type NotificationType.CLICKSENDSMS
        :type clicksendsmsPassword: str
        
        :param clicksendsmsToNumber: (optional) Notification option for type NotificationType.CLICKSENDSMS
        :type clicksendsmsToNumber: str
        
        :param clicksendsmsSenderName: (optional) Notification option for type NotificationType.CLICKSENDSMS
        :type clicksendsmsSenderName: str
        
        :param webHookUrl: (optional) Notification option for type NotificationType.DINGDING
        :type webHookUrl: str
        
        :param secretKey: (optional) Notification option for type NotificationType.DINGDING
        :type secretKey: str
        
        :param discordUsername: (optional) Notification option for type NotificationType.DISCORD
        :type discordUsername: str
        
        :param discordWebhookUrl: (optional) Notification option for type NotificationType.DISCORD
        :type discordWebhookUrl: str
        
        :param discordPrefixMessage: (optional) Notification option for type NotificationType.DISCORD
        :type discordPrefixMessage: str
        
        :param feishuWebHookUrl: (optional) Notification option for type NotificationType.FEISHU
        :type feishuWebHookUrl: str
        
        :param googleChatWebhookURL: (optional) Notification option for type NotificationType.GOOGLECHAT
        :type googleChatWebhookURL: str
        
        :param gorushDeviceToken: (optional) Notification option for type NotificationType.GORUSH
        :type gorushDeviceToken: str
        
        :param gorushPlatform: (optional) Notification option for type NotificationType.GORUSH
        :type gorushPlatform: str
        
        :param gorushTitle: (optional) Notification option for type NotificationType.GORUSH
        :type gorushTitle: str
        
        :param gorushPriority: (optional) Notification option for type NotificationType.GORUSH
        :type gorushPriority: str
        
        :param gorushRetry: (optional) Notification option for type NotificationType.GORUSH
        :type gorushRetry: str
        
        :param gorushTopic: (optional) Notification option for type NotificationType.GORUSH
        :type gorushTopic: str
        
        :param gorushServerURL: (optional) Notification option for type NotificationType.GORUSH
        :type gorushServerURL: str
        
        :param gotifyserverurl: (optional) Notification option for type NotificationType.GOTIFY
        :type gotifyserverurl: str
        
        :param gotifyapplicationToken: (optional) Notification option for type NotificationType.GOTIFY
        :type gotifyapplicationToken: str
        
        :param gotifyPriority: (optional) Notification option for type NotificationType.GOTIFY
        :type gotifyPriority: int
        
        :param lineChannelAccessToken: (optional) Notification option for type NotificationType.LINE
        :type lineChannelAccessToken: str
        
        :param lineUserID: (optional) Notification option for type NotificationType.LINE
        :type lineUserID: str
        
        :param lunaseaDevice: (optional) Notification option for type NotificationType.LUNASEA
        :type lunaseaDevice: str
        
        :param internalRoomId: (optional) Notification option for type NotificationType.MATRIX
        :type internalRoomId: str
        
        :param accessToken: (optional) Notification option for type NotificationType.MATRIX
        :type accessToken: str
        
        :param homeserverUrl: (optional) Notification option for type NotificationType.MATRIX
        :type homeserverUrl: str
        
        :param mattermostusername: (optional) Notification option for type NotificationType.MATTERMOST
        :type mattermostusername: str
        
        :param mattermostWebhookUrl: (optional) Notification option for type NotificationType.MATTERMOST
        :type mattermostWebhookUrl: str
        
        :param mattermostchannel: (optional) Notification option for type NotificationType.MATTERMOST
        :type mattermostchannel: str
        
        :param mattermosticonemo: (optional) Notification option for type NotificationType.MATTERMOST
        :type mattermosticonemo: str
        
        :param mattermosticonurl: (optional) Notification option for type NotificationType.MATTERMOST
        :type mattermosticonurl: str
        
        :param httpAddr: (optional) Notification option for type NotificationType.ONEBOT
        :type httpAddr: str
        
        :param accessToken: (optional) Notification option for type NotificationType.ONEBOT
        :type accessToken: str
        
        :param msgType: (optional) Notification option for type NotificationType.ONEBOT
        :type msgType: str
        
        :param recieverId: (optional) Notification option for type NotificationType.ONEBOT
        :type recieverId: str
        
        :param pagerdutyAutoResolve: (optional) Notification option for type NotificationType.PAGERDUTY
        :type pagerdutyAutoResolve: str
        
        :param pagerdutyIntegrationUrl: (optional) Notification option for type NotificationType.PAGERDUTY
        :type pagerdutyIntegrationUrl: str
        
        :param pagerdutyPriority: (optional) Notification option for type NotificationType.PAGERDUTY
        :type pagerdutyPriority: str
        
        :param pagerdutyIntegrationKey: (optional) Notification option for type NotificationType.PAGERDUTY
        :type pagerdutyIntegrationKey: str
        
        :param promosmsLogin: (optional) Notification option for type NotificationType.PROMOSMS
        :type promosmsLogin: str
        
        :param promosmsPassword: (optional) Notification option for type NotificationType.PROMOSMS
        :type promosmsPassword: str
        
        :param promosmsPhoneNumber: (optional) Notification option for type NotificationType.PROMOSMS
        :type promosmsPhoneNumber: str
        
        :param promosmsSMSType: (optional) Notification option for type NotificationType.PROMOSMS
        :type promosmsSMSType: str
        
        :param promosmsSenderName: (optional) Notification option for type NotificationType.PROMOSMS
        :type promosmsSenderName: str
        
        :param pushbulletAccessToken: (optional) Notification option for type NotificationType.PUSHBULLET
        :type pushbulletAccessToken: str
        
        :param pushdeerKey: (optional) Notification option for type NotificationType.PUSHDEER
        :type pushdeerKey: str
        
        :param pushoveruserkey: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushoveruserkey: str
        
        :param pushoverapptoken: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushoverapptoken: str
        
        :param pushoversounds: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushoversounds: str
        
        :param pushoverpriority: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushoverpriority: str
        
        :param pushovertitle: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushovertitle: str
        
        :param pushoverdevice: (optional) Notification option for type NotificationType.PUSHOVER
        :type pushoverdevice: str
        
        :param pushyAPIKey: (optional) Notification option for type NotificationType.PUSHY
        :type pushyAPIKey: str
        
        :param pushyToken: (optional) Notification option for type NotificationType.PUSHY
        :type pushyToken: str
        
        :param rocketchannel: (optional) Notification option for type NotificationType.ROCKET_CHAT
        :type rocketchannel: str
        
        :param rocketusername: (optional) Notification option for type NotificationType.ROCKET_CHAT
        :type rocketusername: str
        
        :param rocketiconemo: (optional) Notification option for type NotificationType.ROCKET_CHAT
        :type rocketiconemo: str
        
        :param rocketwebhookURL: (optional) Notification option for type NotificationType.ROCKET_CHAT
        :type rocketwebhookURL: str
        
        :param rocketbutton: (optional) Notification option for type NotificationType.ROCKET_CHAT
        :type rocketbutton: str
        
        :param serwersmsUsername: (optional) Notification option for type NotificationType.SERWERSMS
        :type serwersmsUsername: str
        
        :param serwersmsPassword: (optional) Notification option for type NotificationType.SERWERSMS
        :type serwersmsPassword: str
        
        :param serwersmsPhoneNumber: (optional) Notification option for type NotificationType.SERWERSMS
        :type serwersmsPhoneNumber: str
        
        :param serwersmsSenderName: (optional) Notification option for type NotificationType.SERWERSMS
        :type serwersmsSenderName: str
        
        :param signalNumber: (optional) Notification option for type NotificationType.SIGNAL
        :type signalNumber: str
        
        :param signalRecipients: (optional) Notification option for type NotificationType.SIGNAL
        :type signalRecipients: str
        
        :param signalURL: (optional) Notification option for type NotificationType.SIGNAL
        :type signalURL: str
        
        :param slackbutton: (optional) Notification option for type NotificationType.SLACK
        :type slackbutton: str
        
        :param slackchannel: (optional) Notification option for type NotificationType.SLACK
        :type slackchannel: str
        
        :param slackusername: (optional) Notification option for type NotificationType.SLACK
        :type slackusername: str
        
        :param slackiconemo: (optional) Notification option for type NotificationType.SLACK
        :type slackiconemo: str
        
        :param slackwebhookURL: (optional) Notification option for type NotificationType.SLACK
        :type slackwebhookURL: str
        
        :param smtpHost: (optional) Notification option for type NotificationType.SMTP
        :type smtpHost: str
        
        :param smtpPort: (optional) Notification option for type NotificationType.SMTP
        :type smtpPort: int
        
        :param smtpSecure: (optional) Notification option for type NotificationType.SMTP
        :type smtpSecure: str
        
        :param smtpIgnoreTLSError: (optional) Notification option for type NotificationType.SMTP
        :type smtpIgnoreTLSError: str
        
        :param smtpDkimDomain: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimDomain: str
        
        :param smtpDkimKeySelector: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimKeySelector: str
        
        :param smtpDkimPrivateKey: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimPrivateKey: str
        
        :param smtpDkimHashAlgo: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimHashAlgo: str
        
        :param smtpDkimheaderFieldNames: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimheaderFieldNames: str
        
        :param smtpDkimskipFields: (optional) Notification option for type NotificationType.SMTP
        :type smtpDkimskipFields: str
        
        :param smtpUsername: (optional) Notification option for type NotificationType.SMTP
        :type smtpUsername: str
        
        :param smtpPassword: (optional) Notification option for type NotificationType.SMTP
        :type smtpPassword: str
        
        :param customSubject: (optional) Notification option for type NotificationType.SMTP
        :type customSubject: str
        
        :param smtpFrom: (optional) Notification option for type NotificationType.SMTP
        :type smtpFrom: str
        
        :param smtpCC: (optional) Notification option for type NotificationType.SMTP
        :type smtpCC: str
        
        :param smtpBCC: (optional) Notification option for type NotificationType.SMTP
        :type smtpBCC: str
        
        :param smtpTo: (optional) Notification option for type NotificationType.SMTP
        :type smtpTo: str
        
        :param stackfieldwebhookURL: (optional) Notification option for type NotificationType.STACKFIELD
        :type stackfieldwebhookURL: str
        
        :param pushAPIKey: (optional) Notification option for type NotificationType.PUSHBYTECHULUS
        :type pushAPIKey: str
        
        :param telegramBotToken: (optional) Notification option for type NotificationType.TELEGRAM
        :type telegramBotToken: str
        
        :param telegramChatID: (optional) Notification option for type NotificationType.TELEGRAM
        :type telegramChatID: str
        
        :param webhookContentType: (optional) Notification option for type NotificationType.WEBHOOK
        :type webhookContentType: str
        
        :param webhookURL: (optional) Notification option for type NotificationType.WEBHOOK
        :type webhookURL: str
        
        :param weComBotKey: (optional) Notification option for type NotificationType.WECOM
        :type weComBotKey: str
        
        :param alertNowWebhookURL: (optional) Notification option for type NotificationType.ALERTNOW
        :type alertNowWebhookURL: str
        
        :param homeAssistantUrl: (optional) Notification option for type NotificationType.HOMEASSISTANT
        :type homeAssistantUrl: str
        
        :param longLivedAccessToken: (optional) Notification option for type NotificationType.HOMEASSISTANT
        :type longLivedAccessToken: str
        
        :param lineNotifyAccessToken: (optional) Notification option for type NotificationType.LINENOTIFY
        :type lineNotifyAccessToken: str
        
        :param barkEndpoint: (optional) Notification option for type NotificationType.BARK
        :type barkEndpoint: str
        
        :param barkGroup: (optional) Notification option for type NotificationType.BARK
        :type barkGroup: str
        
        :param barkSound: (optional) Notification option for type NotificationType.BARK
        :type barkSound: str
        
        :param goAlertBaseURL: (optional) Notification option for type NotificationType.GOALERT
        :type goAlertBaseURL: str
        
        :param goAlertToken: (optional) Notification option for type NotificationType.GOALERT
        :type goAlertToken: str
        
        :param octopushVersion: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushVersion: str
        
        :param octopushAPIKey: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushAPIKey: str
        
        :param octopushLogin: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushLogin: str
        
        :param octopushPhoneNumber: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushPhoneNumber: str
        
        :param octopushSMSType: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushSMSType: str
        
        :param octopushSenderName: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushSenderName: str
        
        :param octopushDMLogin: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushDMLogin: str
        
        :param octopushDMAPIKey: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushDMAPIKey: str
        
        :param octopushDMPhoneNumber: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushDMPhoneNumber: str
        
        :param octopushDMSenderName: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushDMSenderName: str
        
        :param octopushDMSMSType: (optional) Notification option for type NotificationType.OCTOPUSH
        :type octopushDMSMSType: str
        
        :param serverChanSendKey: (optional) Notification option for type NotificationType.SERVERCHAN
        :type serverChanSendKey: str
        
        :param smsmanagerApiKey: (optional) Notification option for type NotificationType.SMSMANAGER
        :type smsmanagerApiKey: str
        
        :param numbers: (optional) Notification option for type NotificationType.SMSMANAGER
        :type numbers: str
        
        :param messageType: (optional) Notification option for type NotificationType.SMSMANAGER
        :type messageType: str
        
        :param squadcastWebhookURL: (optional) Notification option for type NotificationType.SQUADCAST
        :type squadcastWebhookURL: str
        
        :param webhookUrl: (optional) Notification option for type NotificationType.TEAMS
        :type webhookUrl: str
        
        :param freemobileUser: (optional) Notification option for type NotificationType.FREEMOBILE
        :type freemobileUser: str
        
        :param freemobilePass: (optional) Notification option for type NotificationType.FREEMOBILE
        :type freemobilePass: str
        
        :param ntfyusername: (optional) Notification option for type NotificationType.NTFY
        :type ntfyusername: str
        
        :param ntfypassword: (optional) Notification option for type NotificationType.NTFY
        :type ntfypassword: str
        
        :param ntfytopic: (optional) Notification option for type NotificationType.NTFY
        :type ntfytopic: str
        
        :param ntfyPriority: (optional) Notification option for type NotificationType.NTFY
        :type ntfyPriority: int
        
        :param ntfyserverurl: (optional) Notification option for type NotificationType.NTFY
        :type ntfyserverurl: str
    """

def proxy_docstring(mode) -> str:
    return f"""
        :param protocol: {"(optional) " if mode == "edit" else ""} Proxy Protocol
        :type protocol: ProxyProtocol
        
        :param host: {"(optional) " if mode == "edit" else ""} Proxy Server
        :type host: str
        
        :param port: {"(optional) " if mode == "edit" else ""} Port
        :type port: str
        
        :param auth: (optional) Proxy server has authentication
        :type auth: bool
        
        :param username: (optional) User
        :type username: str
        
        :param password: (optional) Password
        :type password: str
        
        :param active: (optional) Enabled. This proxy will not effect on monitor requests until it is activated. You can control temporarily disable the proxy from all monitors by activation status.
        :type active: bool
        
        :param default: (optional) Set As Default. This proxy will be enabled by default for new monitors. You can still disable the proxy separately for each monitor.
        :type default: bool
        
        :param applyExisting: (optional) Apply on all existing monitors
        :type applyExisting: bool
    """


def docker_host_docstring(mode) -> str:
    return f"""
        :param name: {"(optional) " if mode == "edit" else ""} Friendly Name
        :type name: str
        
        :param dockerType: {"(optional) " if mode == "edit" else ""} Connection Type
        :type dockerType: DockerType
        
        :param dockerDaemon: (optional) Docker Daemon
        :type dockerDaemon: str
    """
