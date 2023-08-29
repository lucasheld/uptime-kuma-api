from enum import Enum


class NotificationType(str, Enum):
    """Enumerate notification types."""

    ALERTA = "alerta"
    """Alerta"""

    ALERTNOW = "AlertNow"
    """AlertNow"""

    ALIYUNSMS = "AliyunSMS"
    """AliyunSMS"""

    APPRISE = "apprise"
    """Apprise (Support 50+ Notification services)"""

    BARK = "Bark"
    """Bark"""

    CLICKSENDSMS = "clicksendsms"
    """ClickSend SMS"""

    DINGDING = "DingDing"
    """DingDing"""

    DISCORD = "discord"
    """Discord"""

    FEISHU = "Feishu"
    """Feishu"""

    FLASHDUTY = "FlashDuty"
    """FlashDuty"""

    FREEMOBILE = "FreeMobile"
    """FreeMobile (mobile.free.fr)"""

    GOALERT = "GoAlert"
    """GoAlert"""

    GOOGLECHAT = "GoogleChat"
    """Google Chat (Google Workspace)"""

    GORUSH = "gorush"
    """Gorush"""

    GOTIFY = "gotify"
    """Gotify"""

    HOMEASSISTANT = "HomeAssistant"
    """Home Assistant"""

    KOOK = "Kook"
    """Kook"""

    LINE = "line"
    """LINE Messenger"""

    LINENOTIFY = "LineNotify"
    """LINE Notify"""

    LUNASEA = "lunasea"
    """LunaSea"""

    MATRIX = "matrix"
    """Matrix"""

    MATTERMOST = "mattermost"
    """Mattermost"""

    NOSTR = "nostr"
    """Nostr"""

    NTFY = "ntfy"
    """Ntfy"""

    OCTOPUSH = "octopush"
    """Octopush"""

    ONEBOT = "OneBot"
    """OneBot"""

    OPSGENIE = "Opsgenie"
    """Opsgenie"""

    PAGERDUTY = "PagerDuty"
    """PagerDuty"""

    PAGERTREE = "PagerTree"
    """PagerTree"""

    PROMOSMS = "promosms"
    """PromoSMS"""

    PUSHBULLET = "pushbullet"
    """Pushbullet"""

    PUSHDEER = "PushDeer"
    """PushDeer"""

    PUSHOVER = "pushover"
    """Pushover"""

    PUSHY = "pushy"
    """Pushy"""

    ROCKET_CHAT = "rocket.chat"
    """Rocket.Chat"""

    SERVERCHAN = "ServerChan"
    """ServerChan"""

    SERWERSMS = "serwersms"
    """SerwerSMS.pl"""

    SIGNAL = "signal"
    """Signal"""

    SLACK = "slack"
    """Slack"""

    SMSC = "smsc"
    """SMSC"""

    SMSEAGLE = "SMSEagle"
    """SMSEagle"""

    SMSMANAGER = "SMSManager"
    """SmsManager (smsmanager.cz)"""

    SMTP = "smtp"
    """Email (SMTP)"""

    SPLUNK = "Splunk"
    """Splunk"""

    SQUADCAST = "squadcast"
    """SquadCast"""

    STACKFIELD = "stackfield"
    """Stackfield"""

    TEAMS = "teams"
    """Microsoft Teams"""

    PUSHBYTECHULUS = "PushByTechulus"
    """Push by Techulus"""

    TELEGRAM = "telegram"
    """Telegram"""

    TWILIO = "twilio"
    """Twilio"""

    WEBHOOK = "webhook"
    """Webhook"""

    WECOM = "WeCom"
    """WeCom"""

    ZOHOCLIQ = "ZohoCliq"
    """ZohoCliq"""


notification_provider_options = {
    NotificationType.ALERTA: dict(
        alertaApiEndpoint=dict(type="str", required=True),
        alertaApiKey=dict(type="str", required=True),
        alertaEnvironment=dict(type="str", required=True),
        alertaAlertState=dict(type="str", required=True),
        alertaRecoverState=dict(type="str", required=True),
    ),
    NotificationType.ALERTNOW: dict(
        alertNowWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.ALIYUNSMS: dict(
        phonenumber=dict(type="str", required=True),
        templateCode=dict(type="str", required=True),
        signName=dict(type="str", required=True),
        accessKeyId=dict(type="str", required=True),
        secretAccessKey=dict(type="str", required=True),
    ),
    NotificationType.APPRISE: dict(
        appriseURL=dict(type="str", required=True),
        title=dict(type="str", required=False),
    ),
    NotificationType.BARK: dict(
        barkEndpoint=dict(type="str", required=True),
        barkGroup=dict(type="str", required=True),
        barkSound=dict(type="str", required=True),
    ),
    NotificationType.CLICKSENDSMS: dict(
        clicksendsmsLogin=dict(type="str", required=True),
        clicksendsmsPassword=dict(type="str", required=True),
        clicksendsmsToNumber=dict(type="str", required=True),
        clicksendsmsSenderName=dict(type="str", required=False),
    ),
    NotificationType.DINGDING: dict(
        webHookUrl=dict(type="str", required=True),
        secretKey=dict(type="str", required=True),
    ),
    NotificationType.DISCORD: dict(
        discordUsername=dict(type="str", required=False),
        discordWebhookUrl=dict(type="str", required=True),
        discordPrefixMessage=dict(type="str", required=False),
    ),
    NotificationType.FEISHU: dict(
        feishuWebHookUrl=dict(type="str", required=True),
    ),
    NotificationType.FLASHDUTY: dict(
        flashdutySeverity=dict(type="str", required=True),
        flashdutyIntegrationKey=dict(type="str", required=False),
    ),
    NotificationType.FREEMOBILE: dict(
        freemobileUser=dict(type="str", required=True),
        freemobilePass=dict(type="str", required=True),
    ),
    NotificationType.GOALERT: dict(
        goAlertBaseURL=dict(type="str", required=True),
        goAlertToken=dict(type="str", required=True),
    ),
    NotificationType.GOOGLECHAT: dict(
        googleChatWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.GORUSH: dict(
        gorushDeviceToken=dict(type="str", required=True),
        gorushPlatform=dict(type="str", required=False),
        gorushTitle=dict(type="str", required=False),
        gorushPriority=dict(type="str", required=False),
        gorushRetry=dict(type="int", required=False),
        gorushTopic=dict(type="str", required=False),
        gorushServerURL=dict(type="str", required=True),
    ),
    NotificationType.GOTIFY: dict(
        gotifyserverurl=dict(type="str", required=True),
        gotifyapplicationToken=dict(type="str", required=True),
        gotifyPriority=dict(type="int", required=True),
    ),
    NotificationType.HOMEASSISTANT: dict(
        notificationService=dict(type="str", required=False),
        homeAssistantUrl=dict(type="str", required=True),
        longLivedAccessToken=dict(type="str", required=True),
    ),
    NotificationType.KOOK: dict(
        kookGuildID=dict(type="str", required=True),
        kookBotToken=dict(type="str", required=True),
    ),
    NotificationType.LINE: dict(
        lineChannelAccessToken=dict(type="str", required=True),
        lineUserID=dict(type="str", required=True),
    ),
    NotificationType.LINENOTIFY: dict(
        lineNotifyAccessToken=dict(type="str", required=True),
    ),
    NotificationType.LUNASEA: dict(
        lunaseaTarget=dict(type="str", required=True),
        lunaseaUserID=dict(type="str", required=False),
        lunaseaDevice=dict(type="str", required=False),
    ),
    NotificationType.MATRIX: dict(
        internalRoomId=dict(type="str", required=True),
        accessToken=dict(type="str", required=True),
        homeserverUrl=dict(type="str", required=True),
    ),
    NotificationType.MATTERMOST: dict(
        mattermostusername=dict(type="str", required=False),
        mattermostWebhookUrl=dict(type="str", required=True),
        mattermostchannel=dict(type="str", required=False),
        mattermosticonemo=dict(type="str", required=False),
        mattermosticonurl=dict(type="str", required=False),
    ),
    NotificationType.NOSTR: dict(
        sender=dict(type="str", required=True),
        recipients=dict(type="str", required=True),
        relays=dict(type="str", required=True),
    ),
    NotificationType.NTFY: dict(
        ntfyAuthenticationMethod=dict(type="str", required=False),
        ntfyusername=dict(type="str", required=False),
        ntfypassword=dict(type="str", required=False),
        ntfyaccesstoken=dict(type="str", required=False),
        ntfytopic=dict(type="str", required=True),
        ntfyPriority=dict(type="int", required=True),
        ntfyserverurl=dict(type="str", required=True),
        ntfyIcon=dict(type="str", required=False),
    ),
    NotificationType.OCTOPUSH: dict(
        octopushVersion=dict(type="str", required=False),
        octopushAPIKey=dict(type="str", required=True),
        octopushLogin=dict(type="str", required=True),
        octopushPhoneNumber=dict(type="str", required=True),
        octopushSMSType=dict(type="str", required=False),
        octopushSenderName=dict(type="str", required=False),
    ),
    NotificationType.ONEBOT: dict(
        httpAddr=dict(type="str", required=True),
        accessToken=dict(type="str", required=True),
        msgType=dict(type="str", required=False),
        recieverId=dict(type="str", required=True),
    ),
    NotificationType.OPSGENIE: dict(
        opsgeniePriority=dict(type="int", required=False),
        opsgenieRegion=dict(type="str", required=True),
        opsgenieApiKey=dict(type="str", required=True),
    ),
    NotificationType.PAGERDUTY: dict(
        pagerdutyAutoResolve=dict(type="str", required=False),
        pagerdutyIntegrationUrl=dict(type="str", required=False),
        pagerdutyPriority=dict(type="str", required=False),
        pagerdutyIntegrationKey=dict(type="str", required=True),
    ),
    NotificationType.PAGERTREE: dict(
        pagertreeAutoResolve=dict(type="str", required=False),
        pagertreeIntegrationUrl=dict(type="str", required=False),
        pagertreeUrgency=dict(type="str", required=False),
    ),
    NotificationType.PROMOSMS: dict(
        promosmsAllowLongSMS=dict(type="bool", required=False),
        promosmsLogin=dict(type="str", required=True),
        promosmsPassword=dict(type="str", required=True),
        promosmsPhoneNumber=dict(type="str", required=True),
        promosmsSMSType=dict(type="str", required=False),
        promosmsSenderName=dict(type="str", required=False),
    ),
    NotificationType.PUSHBULLET: dict(
        pushbulletAccessToken=dict(type="str", required=True),
    ),
    NotificationType.PUSHDEER: dict(
        pushdeerServer=dict(type="str", required=False),
        pushdeerKey=dict(type="str", required=True),
    ),
    NotificationType.PUSHOVER: dict(
        pushoveruserkey=dict(type="str", required=True),
        pushoverapptoken=dict(type="str", required=True),
        pushoversounds=dict(type="str", required=False),
        pushoverpriority=dict(type="str", required=False),
        pushovertitle=dict(type="str", required=False),
        pushoverdevice=dict(type="str", required=False),
        pushoverttl=dict(type="int", required=False),
    ),
    NotificationType.PUSHY: dict(
        pushyAPIKey=dict(type="str", required=True),
        pushyToken=dict(type="str", required=True),
    ),
    NotificationType.ROCKET_CHAT: dict(
        rocketchannel=dict(type="str", required=False),
        rocketusername=dict(type="str", required=False),
        rocketiconemo=dict(type="str", required=False),
        rocketwebhookURL=dict(type="str", required=True),
    ),
    NotificationType.SERVERCHAN: dict(
        serverChanSendKey=dict(type="str", required=True),
    ),
    NotificationType.SERWERSMS: dict(
        serwersmsUsername=dict(type="str", required=True),
        serwersmsPassword=dict(type="str", required=True),
        serwersmsPhoneNumber=dict(type="str", required=True),
        serwersmsSenderName=dict(type="str", required=False),
    ),
    NotificationType.SIGNAL: dict(
        signalNumber=dict(type="str", required=True),
        signalRecipients=dict(type="str", required=True),
        signalURL=dict(type="str", required=True),
    ),
    NotificationType.SLACK: dict(
        slackchannelnotify=dict(type="bool", required=False),
        slackchannel=dict(type="str", required=False),
        slackusername=dict(type="str", required=False),
        slackiconemo=dict(type="str", required=False),
        slackwebhookURL=dict(type="str", required=True),
    ),
    NotificationType.SMSC: dict(
        smscTranslit=dict(type="str", required=False),
        smscLogin=dict(type="str", required=True),
        smscPassword=dict(type="str", required=True),
        smscToNumber=dict(type="str", required=True),
        smscSenderName=dict(type="str", required=False),
    ),
    NotificationType.SMSEAGLE: dict(
        smseagleEncoding=dict(type="bool", required=False),
        smseaglePriority=dict(type="int", required=False),
        smseagleRecipientType=dict(type="str", required=False),
        smseagleToken=dict(type="str", required=True),
        smseagleRecipient=dict(type="str", required=True),
        smseagleUrl=dict(type="str", required=True),
    ),
    NotificationType.SMSMANAGER: dict(
        smsmanagerApiKey=dict(type="str", required=False),
        numbers=dict(type="str", required=False),
        messageType=dict(type="str", required=False),
    ),
    NotificationType.SMTP: dict(
        smtpHost=dict(type="str", required=True),
        smtpPort=dict(type="int", required=True),
        smtpSecure=dict(type="str", required=False),
        smtpIgnoreTLSError=dict(type="bool", required=False),
        smtpDkimDomain=dict(type="str", required=False),
        smtpDkimKeySelector=dict(type="str", required=False),
        smtpDkimPrivateKey=dict(type="str", required=False),
        smtpDkimHashAlgo=dict(type="str", required=False),
        smtpDkimheaderFieldNames=dict(type="str", required=False),
        smtpDkimskipFields=dict(type="str", required=False),
        smtpUsername=dict(type="str", required=False),
        smtpPassword=dict(type="str", required=False),
        customSubject=dict(type="str", required=False),
        smtpFrom=dict(type="str", required=True),
        smtpCC=dict(type="str", required=False),
        smtpBCC=dict(type="str", required=False),
        smtpTo=dict(type="str", required=False),
    ),
    NotificationType.SPLUNK: dict(
        splunkAutoResolve=dict(type="str", required=False),
        splunkSeverity=dict(type="str", required=False),
        splunkRestURL=dict(type="str", required=True),
    ),
    NotificationType.SQUADCAST: dict(
        squadcastWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.STACKFIELD: dict(
        stackfieldwebhookURL=dict(type="str", required=True),
    ),
    NotificationType.TEAMS: dict(
        webhookUrl=dict(type="str", required=True),
    ),
    NotificationType.PUSHBYTECHULUS: dict(
        pushAPIKey=dict(type="str", required=True),
    ),
    NotificationType.TELEGRAM: dict(
        telegramChatID=dict(type="str", required=True),
        telegramSendSilently=dict(type="bool", required=False),
        telegramProtectContent=dict(type="bool", required=False),
        telegramMessageThreadID=dict(type="str", required=False),
        telegramBotToken=dict(type="str", required=True),
    ),
    NotificationType.TWILIO: dict(
        twilioAccountSID=dict(type="str", required=True),
        twilioApiKey=dict(type="str", required=False),
        twilioAuthToken=dict(type="str", required=True),
        twilioToNumber=dict(type="str", required=True),
        twilioFromNumber=dict(type="str", required=True),
    ),
    NotificationType.WEBHOOK: dict(
        webhookContentType=dict(type="str", required=True),
        webhookCustomBody=dict(type="str", required=False),
        webhookAdditionalHeaders=dict(type="str", required=False),
        webhookURL=dict(type="str", required=True),
    ),
    NotificationType.WECOM: dict(
        weComBotKey=dict(type="str", required=True),
    ),
    NotificationType.ZOHOCLIQ: dict(
        webhookUrl=dict(type="str", required=True),
    ),
}

notification_provider_conditions = dict(
    gotifyPriority=dict(
        min=0,
        max=10,
    ),
    ntfyPriority=dict(
        min=1,
        max=5,
    ),
    opsgeniePriority=dict(
        min=1,
        max=5,
    ),
    pushoverttl=dict(
        min=0,
    ),
    smseaglePriority=dict(
        min=0,
        max=9,
    ),
    smtpPort=dict(
        min=0,
        max=65535,
    ),
)
