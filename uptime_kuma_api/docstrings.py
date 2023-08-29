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
        :param str, optional parent: Id of the monitor group, defaults to None
        :param str, optional description: Description, defaults to None
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
        :param str, optional httpBodyEncoding: Body Encoding, defaults to "json". Allowed values: "json", "xml".
        :param str, optional body: Body, defaults to None
        :param str, optional headers: Headers, defaults to None
        :param AuthMethod, optional authMethod: Method, defaults to :attr:`~.AuthMethod.NONE`
        :param str, optional tlsCert: Cert for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional tlsKey: Key for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional tlsCa: Ca for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional basic_auth_user: Username for ``authMethod`` :attr:`~.AuthMethod.HTTP_BASIC` and :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional basic_auth_pass: Password for ``authMethod`` :attr:`~.AuthMethod.HTTP_BASIC` and :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional authDomain: Domain for ``authMethod`` :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional authWorkstation: Workstation for ``authMethod`` :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional oauth_auth_method: Authentication Method, defaults to None
        :param str, optional oauth_token_url: OAuth Token URL, defaults to None
        :param str, optional oauth_client_id: Client ID, defaults to None
        :param str, optional oauth_client_secret: Client Secret, defaults to None
        :param str, optional oauth_scopes: OAuth Scope, defaults to None
        :param int, optional timeout: Request Timeout, defaults to None
        :param str, optional keyword: Keyword. Search keyword in plain HTML or JSON response. The search is case-sensitive., defaults to None
        :param bool, optional invertKeyword: Invert Keyword. Look for the keyword to be absent rather than present., defaults to False
        :param str, optional hostname: Hostname, defaults to None
        :param int, optional packetSize: Packet Size, defaults to None
        :param int, optional port: Port, ``type`` :attr:`~.MonitorType.DNS` defaults to ``53`` and ``type`` :attr:`~.MonitorType.RADIUS` defaults to ``1812``
        :param str, optional dns_resolve_server: Resolver Server, defaults to "1.1.1.1"
        :param str, optional dns_resolve_type: Resource Record Type, defaults to "A". Available values are:
            
            - "A"
            - "AAAA"
            - "CAA"
            - "CNAME"
            - "MX"
            - "NS"
            - "PTR"
            - "SOA"
            - "SRV"
            - "TXT"
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
        :param str, optional game: Game, defaults to None
        :param bool, optional gamedigGivenPortOnly: Gamedig: Guess Port. The port used by Valve Server Query Protocol may be different from the client port. Try this if the monitor cannot connect to your server., defaults to False
        :param str, optional jsonPath: Json Query, defaults to None
        :param str, optional expectedValue: Expected Value, defaults to None
        :param str, optional kafkaProducerBrokers: Kafka Broker list, defaults to None
        :param str, optional kafkaProducerTopic: Kafka Topic Name, defaults to None
        :param str, optional kafkaProducerMessage: Kafka Producer Message, defaults to None
        :param bool, optional kafkaProducerSsl: Enable Kafka SSL, defaults to False
        :param bool, optional kafkaProducerAllowAutoTopicCreation: Enable Kafka Producer Auto Topic Creation, defaults to False
        :param dict, optional kafkaProducerSaslOptions: Kafka SASL Options
        
            - **mechanism** (*str*, *optional*): Mechanism, defaults to "None". Available values are:
            
                - "None"
                - "plain"
                - "scram-sha-256"
                - "scram-sha-512"
                - "aws"
            - **username** (*str*, *optional*): Username, defaults to None
            - **password** (*str*, *optional*): Password, defaults to None
            - **authorizationIdentity** (*str*, *optional*): Authorization Identity, defaults to None
            - **accessKeyId** (*str*, *optional*): AccessKey Id, defaults to None
            - **secretAccessKey** (*str*, *optional*): Secret AccessKey, defaults to None
            - **sessionToken** (*str*, *optional*): Session Token, defaults to None
    """


def notification_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name        
        :param NotificationType{", optional" if mode == "edit" else ""} type: Notification Type        
        :param bool, optional isDefault: Default enabled. This notification will be enabled by default for new monitors. You can still disable the notification separately for each monitor., defaults to False
        :param bool, optional applyExisting: Apply on all existing monitors, defaults to False
        
        :param str, optional alertaApiEndpoint: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str, optional alertaApiKey: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str, optional alertaEnvironment: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str, optional alertaAlertState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str, optional alertaRecoverState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str, optional alertNowWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ALERTNOW`.
        :param str, optional phonenumber: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str, optional templateCode: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str, optional signName: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str, optional accessKeyId: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str, optional secretAccessKey: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str, optional appriseURL: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`.
        :param str title: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`.
        :param str, optional barkEndpoint: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str, optional barkGroup: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str, optional barkSound: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str, optional clicksendsmsLogin: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str, optional clicksendsmsPassword: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str, optional clicksendsmsToNumber: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str clicksendsmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str, optional webHookUrl: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str, optional secretKey: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str discordUsername: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional discordWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str discordPrefixMessage: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional feishuWebHookUrl: Notification option for ``type`` :attr:`~.NotificationType.FEISHU`.
        :param str, optional flashdutySeverity: Notification option for ``type`` :attr:`~.NotificationType.FLASHDUTY`.
        :param str flashdutyIntegrationKey: Notification option for ``type`` :attr:`~.NotificationType.FLASHDUTY`.
        :param str, optional freemobileUser: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`.
        :param str, optional freemobilePass: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`.
        :param str, optional goAlertBaseURL: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`.
        :param str, optional goAlertToken: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`.
        :param str, optional googleChatWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`.
        :param str, optional gorushDeviceToken: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gorushPlatform: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gorushTitle: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gorushPriority: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param int gorushRetry: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gorushTopic: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gorushServerURL: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gotifyserverurl: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param str, optional gotifyapplicationToken: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param int, optional gotifyPriority: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param str notificationService: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param str, optional homeAssistantUrl: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param str, optional longLivedAccessToken: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param str, optional kookGuildID: Notification option for ``type`` :attr:`~.NotificationType.KOOK`.
        :param str, optional kookBotToken: Notification option for ``type`` :attr:`~.NotificationType.KOOK`.
        :param str, optional lineChannelAccessToken: Notification option for ``type`` :attr:`~.NotificationType.LINE`.
        :param str, optional lineUserID: Notification option for ``type`` :attr:`~.NotificationType.LINE`.
        :param str, optional lineNotifyAccessToken: Notification option for ``type`` :attr:`~.NotificationType.LINENOTIFY`.
        :param str, optional lunaseaTarget: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. Allowed values: "device", "user".
        :param str lunaseaUserID: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. User ID.
        :param str lunaseaDevice: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. Device ID.
        :param str, optional internalRoomId: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str, optional accessToken: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str, optional homeserverUrl: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str mattermostusername: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str, optional mattermostWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str mattermostchannel: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str mattermosticonemo: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str mattermosticonurl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str, optional sender: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str, optional recipients: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str, optional relays: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str ntfyAuthenticationMethod: Notification option for ``type`` :attr:`~.NotificationType.NTFY`. Authentication Method.
        :param str ntfyusername: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str ntfypassword: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str ntfyaccesstoken: Notification option for ``type`` :attr:`~.NotificationType.NTFY`. Access Token.
        :param str, optional ntfytopic: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param int, optional ntfyPriority: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfyserverurl: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str ntfyIcon: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str octopushVersion: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional octopushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional octopushLogin: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional octopushPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str octopushSMSType: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str octopushSenderName: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional httpAddr: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str, optional accessToken: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str msgType: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str, optional recieverId: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param int opsgeniePriority: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. Priority. Available values are numbers between ``1`` and ``5``.
        :param str, optional opsgenieRegion: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. Region. Available values are:
            
            - ``us``: US (Default)
            - ``eu``: EU
        :param str, optional opsgenieApiKey: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. API Key.
        :param str pagerdutyAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str pagerdutyIntegrationUrl: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str pagerdutyPriority: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str, optional pagerdutyIntegrationKey: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str pagertreeAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`. 
        
            Available values are:
            
            - ``0``: Do Nothing
            - ``resolve``: Auto Resolve
        :param str pagertreeIntegrationUrl: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`.
        :param str pagertreeUrgency: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`. 
        
            Available values are:
            
            - ``silent``: Silent
            - ``low``: Low
            - ``medium``: Medium
            - ``high``: High
            - ``critical``: Critical
        :param bool promosmsAllowLongSMS: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`. Allow long SMS.
        :param str, optional promosmsLogin: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str, optional promosmsPassword: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str, optional promosmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`. Phone number (for Polish recipient You can skip area codes).
        :param str promosmsSMSType: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`. 
            
            Available values are:
            
            - ``0``: SMS FLASH - Message will automatically show on recipient device. Limited only to Polish recipients.
            - ``1``: SMS ECO - cheap but slow and often overloaded. Limited only to Polish recipients.
            - ``3``: SMS FULL - Premium tier of SMS, You can use your Sender Name (You need to register name first). Reliable for alerts.
            - ``4``: SMS SPEED - Highest priority in system. Very quick and reliable but costly (about twice of SMS FULL price).
        :param str promosmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str, optional pushbulletAccessToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHBULLET`.
        :param str pushdeerServer: Notification option for ``type`` :attr:`~.NotificationType.PUSHDEER`.
        :param str, optional pushdeerKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHDEER`.
        :param str, optional pushoveruserkey: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str, optional pushoverapptoken: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushoversounds: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushoverpriority: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushovertitle: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushoverdevice: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param int pushoverttl: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`. Message TTL (Seconds).
        :param str, optional pushyAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`.
        :param str, optional pushyToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`.
        :param str rocketchannel: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str rocketusername: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str rocketiconemo: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str, optional rocketwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str, optional serverChanSendKey: Notification option for ``type`` :attr:`~.NotificationType.SERVERCHAN`.
        :param str, optional serwersmsUsername: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsPassword: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str serwersmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional signalNumber: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str, optional signalRecipients: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str, optional signalURL: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param bool slackchannelnotify: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str slackchannel: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str slackusername: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str slackiconemo: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str, optional slackwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str smscTranslit: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str, optional smscLogin: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str, optional smscPassword: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str, optional smscToNumber: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str smscSenderName: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param bool smseagleEncoding: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. True to send messages in unicode.
        :param int smseaglePriority: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Message priority (0-9, default = 0).
        :param str smseagleRecipientType: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Recipient type.
            
            Available values are:
            
            - ``smseagle-to``: Phone number(s)
            - ``smseagle-group``: Phonebook group name(s)
            - ``smseagle-contact``: Phonebook contact name(s)
        :param str, optional smseagleToken: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. API Access token.
        :param str, optional smseagleRecipient: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Recipient(s) (multiple must be separated with comma).
        :param str, optional smseagleUrl: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Your SMSEagle device URL.
        :param str smsmanagerApiKey: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str numbers: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str messageType: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str, optional smtpHost: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param int, optional smtpPort: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpSecure: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param bool smtpIgnoreTLSError: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimDomain: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimKeySelector: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimPrivateKey: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimHashAlgo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimheaderFieldNames: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpDkimskipFields: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpUsername: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpPassword: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str customSubject: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpFrom: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpBCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpTo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str splunkAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Auto resolve or acknowledged.
        
            Available values are:
            
            - ``0``: do nothing
            - ``ACKNOWLEDGEMENT``: auto acknowledged
            - ``RECOVERY``: auto resolve
        :param str splunkSeverity: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Severity.
        
            Available values are:
            
            - ``INFO``
            - ``WARNING``
            - ``CRITICAL``
        :param str, optional splunkRestURL: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Splunk Rest URL.
        :param str, optional squadcastWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SQUADCAST`.
        :param str, optional stackfieldwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.STACKFIELD`.
        :param str, optional webhookUrl: Notification option for ``type`` :attr:`~.NotificationType.TEAMS`.
        :param str, optional pushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param str, optional telegramChatID: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param bool telegramSendSilently: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param bool telegramProtectContent: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str telegramMessageThreadID: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str, optional telegramBotToken: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str, optional twilioAccountSID: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. Account SID.
        :param str twilioApiKey: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`.
        :param str, optional twilioAuthToken: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. Auth Token.
        :param str, optional twilioToNumber: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. To Number.
        :param str, optional twilioFromNumber: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. From Number.
        :param str, optional webhookContentType: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str webhookCustomBody: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str webhookAdditionalHeaders: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str, optional webhookURL: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str, optional weComBotKey: Notification option for ``type`` :attr:`~.NotificationType.WECOM`.
        :param str, optional webhookUrl: Notification option for ``type`` :attr:`~.NotificationType.ZOHOCLIQ`.
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


def maintenance_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} title: Title
        :param MaintenanceStrategy{", optional" if mode == "edit" else ""} strategy: Strategy
        :param bool, optional active: True if maintenance is active, defaults to ``True``
        :param str, optional description: Description, defaults to ``""``
        :param list, optional dateRange: DateTime Range, defaults to ``["<current date>"]``
        :param int, optional intervalDay: Interval (Run once every day), defaults to ``1``
        :param list, optional weekdays: List that contains the days of the week on which the maintenance is enabled (Sun = ``0``, Mon = ``1``, ..., Sat = ``6``). Required for ``strategy`` :attr:`~.MaintenanceStrategy.RECURRING_WEEKDAY`., defaults to ``[]``.
        :param list, optional daysOfMonth: List that contains the days of the month on which the maintenance is enabled (Day 1 = ``1``, Day 2 = ``2``, ..., Day 31 = ``31``) and the last day of the month (``"lastDay1"``). Required for ``strategy`` :attr:`~.MaintenanceStrategy.RECURRING_DAY_OF_MONTH`., defaults to ``[]``.
        :param list, optional timeRange: Maintenance Time Window of a Day, defaults to ``[{{"hours": 2, "minutes": 0}}, {{"hours": 3, "minutes": 0}}]``.
        :param str, optional cron: Cron Schedule. Required for ``strategy`` :attr:`~.MaintenanceStrategy.CRON`., defaults to ``"30 3 * * *"``
        :param int, optional durationMinutes: Duration (Minutes). Required for ``strategy`` :attr:`~.MaintenanceStrategy.CRON`., defaults to ``60``
        :param str, optional timezone: Timezone, defaults to ``None`` (Server Timezone)
    """


def tag_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Tag name
        :param str{", optional" if mode == "edit" else ""} color: Tag color
    """
