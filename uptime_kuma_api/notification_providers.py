from enum import Enum


class NotificationType(str, Enum):
    ALERTA = "alerta"
    ALIYUNSMS = "AliyunSMS"
    APPRISE = "apprise"
    CLICKSENDSMS = "clicksendsms"
    DINGDING = "DingDing"
    DISCORD = "discord"
    FEISHU = "Feishu"
    GOOGLECHAT = "GoogleChat"
    GORUSH = "gorush"
    GOTIFY = "gotify"
    LINE = "line"
    LUNASEA = "lunasea"
    MATRIX = "matrix"
    MATTERMOST = "mattermost"
    ONEBOT = "OneBot"
    PAGERDUTY = "PagerDuty"
    PROMOSMS = "promosms"
    PUSHBULLET = "pushbullet"
    PUSHDEER = "PushDeer"
    PUSHOVER = "pushover"
    PUSHY = "pushy"
    ROCKET_CHAT = "rocket.chat"
    SERWERSMS = "serwersms"
    SIGNAL = "signal"
    SLACK = "slack"
    SMTP = "smtp"
    STACKFIELD = "stackfield"
    PUSHBYTECHULUS = "PushByTechulus"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    WECOM = "WeCom"
    ALERTNOW = "AlertNow"
    HOMEASSISTANT = "HomeAssistant"
    LINENOTIFY = "LineNotify"
    BARK = "Bark"
    GOALERT = "GoAlert"
    OCTOPUSH = "octopush"
    SERVERCHAN = "ServerChan"
    SMSMANAGER = "SMSManager"
    SQUADCAST = "squadcast"
    TEAMS = "teams"
    FREEMOBILE = "FreeMobile"
    NTFY = "ntfy"


notification_provider_options = {
    NotificationType.ALERTA: [
        "alertaApiEndpoint",
        "alertaApiKey",
        "alertaEnvironment",
        "alertaAlertState",
        "alertaRecoverState",
    ],
    NotificationType.ALIYUNSMS: [
        "phonenumber",
        "templateCode",
        "signName",
        "accessKeyId",
        "secretAccessKey",
    ],
    NotificationType.APPRISE: [
        "appriseURL",
        "title",
    ],
    NotificationType.CLICKSENDSMS: [
        "clicksendsmsLogin",
        "clicksendsmsPassword",
        "clicksendsmsToNumber",
        "clicksendsmsSenderName",
    ],
    NotificationType.DINGDING: [
        "webHookUrl",
        "secretKey",
    ],
    NotificationType.DISCORD: [
        "discordUsername",
        "discordWebhookUrl",
        "discordPrefixMessage",
    ],
    NotificationType.FEISHU: [
        "feishuWebHookUrl",
    ],
    NotificationType.GOOGLECHAT: [
        "googleChatWebhookURL",
    ],
    NotificationType.GORUSH: [
        "gorushDeviceToken",
        "gorushPlatform",
        "gorushTitle",
        "gorushPriority",
        "gorushRetry",
        "gorushTopic",
        "gorushServerURL",
    ],
    NotificationType.GOTIFY: [
        "gotifyserverurl",
        "gotifyapplicationToken",
        "gotifyPriority",
    ],
    NotificationType.LINE: [
        "lineChannelAccessToken",
        "lineUserID",
    ],
    NotificationType.LUNASEA: [
        "lunaseaDevice",
    ],
    NotificationType.MATRIX: [
        "internalRoomId",
        "accessToken",
        "homeserverUrl",
    ],
    NotificationType.MATTERMOST: [
        "mattermostusername",
        "mattermostWebhookUrl",
        "mattermostchannel",
        "mattermosticonemo",
        "mattermosticonurl",
    ],
    NotificationType.ONEBOT: [
        "httpAddr",
        "accessToken",
        "msgType",
        "recieverId",
    ],
    NotificationType.PAGERDUTY: [
        "pagerdutyAutoResolve",
        "pagerdutyIntegrationUrl",
        "pagerdutyPriority",
        "pagerdutyIntegrationKey",
    ],
    NotificationType.PROMOSMS: [
        "promosmsLogin",
        "promosmsPassword",
        "promosmsPhoneNumber",
        "promosmsSMSType",
        "promosmsSenderName",
    ],
    NotificationType.PUSHBULLET: [
        "pushbulletAccessToken",
    ],
    NotificationType.PUSHDEER: [
        "pushdeerKey",
    ],
    NotificationType.PUSHOVER: [
        "pushoveruserkey",
        "pushoverapptoken",
        "pushoversounds",
        "pushoverpriority",
        "pushovertitle",
        "pushoverdevice",
    ],
    NotificationType.PUSHY: [
        "pushyAPIKey",
        "pushyToken",
    ],
    NotificationType.ROCKET_CHAT: [
        "rocketchannel",
        "rocketusername",
        "rocketiconemo",
        "rocketwebhookURL",
        "rocketbutton",
    ],
    NotificationType.SERWERSMS: [
        "serwersmsUsername",
        "serwersmsPassword",
        "serwersmsPhoneNumber",
        "serwersmsSenderName",
    ],
    NotificationType.SIGNAL: [
        "signalNumber",
        "signalRecipients",
        "signalURL",
    ],
    NotificationType.SLACK: [
        "slackbutton",
        "slackchannel",
        "slackusername",
        "slackiconemo",
        "slackwebhookURL",
        "slackbutton",
    ],
    NotificationType.SMTP: [
        "smtpHost",
        "smtpPort",
        "smtpSecure",
        "smtpIgnoreTLSError",
        "smtpDkimDomain",
        "smtpDkimKeySelector",
        "smtpDkimPrivateKey",
        "smtpDkimHashAlgo",
        "smtpDkimheaderFieldNames",
        "smtpDkimskipFields",
        "smtpUsername",
        "smtpPassword",
        "customSubject",
        "smtpFrom",
        "smtpCC",
        "smtpBCC",
        "smtpTo",
    ],
    NotificationType.STACKFIELD: [
        "stackfieldwebhookURL",
    ],
    NotificationType.PUSHBYTECHULUS: [
        "pushAPIKey",
    ],
    NotificationType.TELEGRAM: [
        "telegramBotToken",
        "telegramChatID",
    ],
    NotificationType.WEBHOOK: [
        "webhookContentType",
        "webhookURL",
    ],
    NotificationType.WECOM: [
        "weComBotKey",
    ],
    NotificationType.ALERTNOW: [
        "alertNowWebhookURL",
    ],
    NotificationType.HOMEASSISTANT: [
        "homeAssistantUrl",
        "longLivedAccessToken",
    ],
    NotificationType.LINENOTIFY: [
        "lineNotifyAccessToken",
    ],
    NotificationType.BARK: [
        "barkEndpoint",
        "barkGroup",
        "barkSound",
    ],
    NotificationType.GOALERT: [
        "goAlertBaseURL",
        "goAlertToken",
    ],
    NotificationType.OCTOPUSH: [
        "octopushVersion",
        "octopushAPIKey",
        "octopushLogin",
        "octopushPhoneNumber",
        "octopushSMSType",
        "octopushSenderName",
        "octopushDMLogin",
        "octopushDMAPIKey",
        "octopushDMPhoneNumber",
        "octopushDMSenderName",
        "octopushDMSMSType",
    ],
    NotificationType.SERVERCHAN: [
        "serverChanSendKey",
    ],
    NotificationType.SMSMANAGER: [
        "smsmanagerApiKey",
        "numbers",
        "messageType",
    ],
    NotificationType.SQUADCAST: [
        "squadcastWebhookURL",
    ],
    NotificationType.TEAMS: [
        "webhookUrl",
    ],
    NotificationType.FREEMOBILE: [
        "freemobileUser",
        "freemobilePass",
    ],
    NotificationType.NTFY: [
        "ntfyusername",
        "ntfypassword",
        "ntfytopic",
        "ntfyPriority",
        "ntfyserverurl",
    ],
}

notification_provider_conditions = {
    "gotifyPriority": {
        "min": 0,
        "max": 10,
    },
    "smtpPort": {
        "min": 0,
        "max": 65535,
    },
    "ntfyPriority": {
        "min": 1,
        "max": 5,
    },
}
