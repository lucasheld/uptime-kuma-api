from enum import Enum


class NotificationType(str, Enum):
    """Enumerate notification types."""

    ALERTA = "alerta"
    """Alerta"""

    ALIYUNSMS = "AliyunSMS"
    """AliyunSMS"""

    APPRISE = "apprise"
    """Apprise (Support 50+ Notification services)"""

    CLICKSENDSMS = "clicksendsms"
    """ClickSend SMS"""

    DINGDING = "DingDing"
    """DingDing"""

    DISCORD = "discord"
    """Discord"""

    FEISHU = "Feishu"
    """Feishu"""

    GOOGLECHAT = "GoogleChat"
    """Google Chat (Google Workspace only)"""

    GORUSH = "gorush"
    """Gorush"""

    GOTIFY = "gotify"
    """Gotify"""

    LINE = "line"
    """Line Messenger"""

    LUNASEA = "lunasea"
    """LunaSea"""

    MATRIX = "matrix"
    """Matrix"""

    MATTERMOST = "mattermost"
    """Mattermost"""

    ONEBOT = "OneBot"
    """OneBot"""

    PAGERDUTY = "PagerDuty"
    """PagerDuty"""

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

    SERWERSMS = "serwersms"
    """SerwerSMS.pl"""

    SIGNAL = "signal"
    """Signal"""

    SLACK = "slack"
    """Slack"""

    SMTP = "smtp"
    """Email (SMTP)"""

    STACKFIELD = "stackfield"
    """Stackfield"""

    PUSHBYTECHULUS = "PushByTechulus"
    """Push by Techulus"""

    TELEGRAM = "telegram"
    """Telegram"""

    WEBHOOK = "webhook"
    """Webhook"""

    WECOM = "WeCom"
    """WeCom"""

    ALERTNOW = "AlertNow"
    """AlertNow"""

    HOMEASSISTANT = "HomeAssistant"
    """Home Assistant"""

    LINENOTIFY = "LineNotify"
    """LineNotify"""

    BARK = "Bark"
    """Bark"""

    GOALERT = "GoAlert"
    """GoAlert"""

    OCTOPUSH = "octopush"
    """Octopush"""

    SERVERCHAN = "ServerChan"
    """ServerChan"""

    SMSMANAGER = "SMSManager"
    """SMSManager"""

    SQUADCAST = "squadcast"
    """Squadcast"""

    TEAMS = "teams"
    """Microsoft Teams"""

    FREEMOBILE = "FreeMobile"
    """FreeMobile"""

    NTFY = "ntfy"
    """ntfy"""


notification_provider_options = {
    NotificationType.ALERTA: dict(
        alertaApiEndpoint=dict(
            type="str"
        ),
        alertaApiKey=dict(type="str"),
        alertaEnvironment=dict(type="str"),
        alertaAlertState=dict(type="str"),
        alertaRecoverState=dict(type="str"),
    ),
    NotificationType.ALIYUNSMS: dict(
        phonenumber=dict(type="str"),
        templateCode=dict(type="str"),
        signName=dict(type="str"),
        accessKeyId=dict(type="str"),
        secretAccessKey=dict(type="str"),
    ),
    NotificationType.APPRISE: dict(
        appriseURL=dict(type="str"),
        title=dict(type="str"),
    ),
    NotificationType.CLICKSENDSMS: dict(
        clicksendsmsLogin=dict(type="str"),
        clicksendsmsPassword=dict(type="str"),
        clicksendsmsToNumber=dict(type="str"),
        clicksendsmsSenderName=dict(type="str"),
    ),
    NotificationType.DINGDING: dict(
        webHookUrl=dict(type="str"),
        secretKey=dict(type="str"),
    ),
    NotificationType.DISCORD: dict(
        discordUsername=dict(type="str"),
        discordWebhookUrl=dict(type="str"),
        discordPrefixMessage=dict(type="str"),
    ),
    NotificationType.FEISHU: dict(
        feishuWebHookUrl=dict(type="str"),
    ),
    NotificationType.GOOGLECHAT: dict(
        googleChatWebhookURL=dict(type="str"),
    ),
    NotificationType.GORUSH: dict(
        gorushDeviceToken=dict(type="str"),
        gorushPlatform=dict(type="str"),
        gorushTitle=dict(type="str"),
        gorushPriority=dict(type="str"),
        gorushRetry=dict(type="str"),
        gorushTopic=dict(type="str"),
        gorushServerURL=dict(type="str"),
    ),
    NotificationType.GOTIFY: dict(
        gotifyserverurl=dict(type="str"),
        gotifyapplicationToken=dict(type="str"),
        gotifyPriority=dict(type="int"),
    ),
    NotificationType.LINE: dict(
        lineChannelAccessToken=dict(type="str"),
        lineUserID=dict(type="str"),
    ),
    NotificationType.LUNASEA: dict(
        lunaseaDevice=dict(type="str"),
    ),
    NotificationType.MATRIX: dict(
        internalRoomId=dict(type="str"),
        accessToken=dict(type="str"),
        homeserverUrl=dict(type="str"),
    ),
    NotificationType.MATTERMOST: dict(
        mattermostusername=dict(type="str"),
        mattermostWebhookUrl=dict(type="str"),
        mattermostchannel=dict(type="str"),
        mattermosticonemo=dict(type="str"),
        mattermosticonurl=dict(type="str"),
    ),
    NotificationType.ONEBOT: dict(
        httpAddr=dict(type="str"),
        accessToken=dict(type="str"),
        msgType=dict(type="str"),
        recieverId=dict(type="str"),
    ),
    NotificationType.PAGERDUTY: dict(
        pagerdutyAutoResolve=dict(type="str"),
        pagerdutyIntegrationUrl=dict(type="str"),
        pagerdutyPriority=dict(type="str"),
        pagerdutyIntegrationKey=dict(type="str"),
    ),
    NotificationType.PROMOSMS: dict(
        promosmsLogin=dict(type="str"),
        promosmsPassword=dict(type="str"),
        promosmsPhoneNumber=dict(type="str"),
        promosmsSMSType=dict(type="str"),
        promosmsSenderName=dict(type="str"),
    ),
    NotificationType.PUSHBULLET: dict(
        pushbulletAccessToken=dict(type="str"),
    ),
    NotificationType.PUSHDEER: dict(
        pushdeerKey=dict(type="str"),
    ),
    NotificationType.PUSHOVER: dict(
        pushoveruserkey=dict(type="str"),
        pushoverapptoken=dict(type="str"),
        pushoversounds=dict(type="str"),
        pushoverpriority=dict(type="str"),
        pushovertitle=dict(type="str"),
        pushoverdevice=dict(type="str"),
    ),
    NotificationType.PUSHY: dict(
        pushyAPIKey=dict(type="str"),
        pushyToken=dict(type="str"),
    ),
    NotificationType.ROCKET_CHAT: dict(
        rocketchannel=dict(type="str"),
        rocketusername=dict(type="str"),
        rocketiconemo=dict(type="str"),
        rocketwebhookURL=dict(type="str"),
        rocketbutton=dict(type="str"),
    ),
    NotificationType.SERWERSMS: dict(
        serwersmsUsername=dict(type="str"),
        serwersmsPassword=dict(type="str"),
        serwersmsPhoneNumber=dict(type="str"),
        serwersmsSenderName=dict(type="str"),
    ),
    NotificationType.SIGNAL: dict(
        signalNumber=dict(type="str"),
        signalRecipients=dict(type="str"),
        signalURL=dict(type="str"),
    ),
    NotificationType.SLACK: dict(
        slackbutton=dict(type="str"),
        slackchannel=dict(type="str"),
        slackusername=dict(type="str"),
        slackiconemo=dict(type="str"),
        slackwebhookURL=dict(type="str"),
    ),
    NotificationType.SMTP: dict(
        smtpHost=dict(type="str"),
        smtpPort=dict(type="int"),
        smtpSecure=dict(type="str"),
        smtpIgnoreTLSError=dict(type="str"),
        smtpDkimDomain=dict(type="str"),
        smtpDkimKeySelector=dict(type="str"),
        smtpDkimPrivateKey=dict(type="str"),
        smtpDkimHashAlgo=dict(type="str"),
        smtpDkimheaderFieldNames=dict(type="str"),
        smtpDkimskipFields=dict(type="str"),
        smtpUsername=dict(type="str"),
        smtpPassword=dict(type="str"),
        customSubject=dict(type="str"),
        smtpFrom=dict(type="str"),
        smtpCC=dict(type="str"),
        smtpBCC=dict(type="str"),
        smtpTo=dict(type="str"),
    ),
    NotificationType.STACKFIELD: dict(
        stackfieldwebhookURL=dict(type="str"),
    ),
    NotificationType.PUSHBYTECHULUS: dict(
        pushAPIKey=dict(type="str"),
    ),
    NotificationType.TELEGRAM: dict(
        telegramBotToken=dict(type="str"),
        telegramChatID=dict(type="str"),
    ),
    NotificationType.WEBHOOK: dict(
        webhookContentType=dict(type="str"),
        webhookURL=dict(type="str"),
    ),
    NotificationType.WECOM: dict(
        weComBotKey=dict(type="str"),
    ),
    NotificationType.ALERTNOW: dict(
        alertNowWebhookURL=dict(type="str"),
    ),
    NotificationType.HOMEASSISTANT: dict(
        homeAssistantUrl=dict(type="str"),
        longLivedAccessToken=dict(type="str"),
    ),
    NotificationType.LINENOTIFY: dict(
        lineNotifyAccessToken=dict(type="str"),
    ),
    NotificationType.BARK: dict(
        barkEndpoint=dict(type="str"),
        barkGroup=dict(type="str"),
        barkSound=dict(type="str"),
    ),
    NotificationType.GOALERT: dict(
        goAlertBaseURL=dict(type="str"),
        goAlertToken=dict(type="str"),
    ),
    NotificationType.OCTOPUSH: dict(
        octopushVersion=dict(type="str"),
        octopushAPIKey=dict(type="str"),
        octopushLogin=dict(type="str"),
        octopushPhoneNumber=dict(type="str"),
        octopushSMSType=dict(type="str"),
        octopushSenderName=dict(type="str"),
        octopushDMLogin=dict(type="str"),
        octopushDMAPIKey=dict(type="str"),
        octopushDMPhoneNumber=dict(type="str"),
        octopushDMSenderName=dict(type="str"),
        octopushDMSMSType=dict(type="str"),
    ),
    NotificationType.SERVERCHAN: dict(
        serverChanSendKey=dict(type="str"),
    ),
    NotificationType.SMSMANAGER: dict(
        smsmanagerApiKey=dict(type="str"),
        numbers=dict(type="str"),
        messageType=dict(type="str"),
    ),
    NotificationType.SQUADCAST: dict(
        squadcastWebhookURL=dict(type="str"),
    ),
    NotificationType.TEAMS: dict(
        webhookUrl=dict(type="str"),
    ),
    NotificationType.FREEMOBILE: dict(
        freemobileUser=dict(type="str"),
        freemobilePass=dict(type="str"),
    ),
    NotificationType.NTFY: dict(
        ntfyusername=dict(type="str"),
        ntfypassword=dict(type="str"),
        ntfytopic=dict(type="str"),
        ntfyPriority=dict(type="int"),
        ntfyserverurl=dict(type="str"),
    ),
}

notification_provider_conditions = dict(
    gotifyPriority=dict(
        min=0,
        max=10
    ),
    smtpPort=dict(
        min=0,
        max=65535
    ),
    ntfyPriority=dict(
        min=1,
        max=5
    ),
)
