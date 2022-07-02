from enum import Enum


class NotificationType(str, Enum):
    ALERTA = "alerta"
    ALIYUNSMS = "AliyunSMS"
    APPRISE = "apprise"
    BARK = "Bark"
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
    NTFY = "ntfy"
    OCTOPUSH = "octopush"
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
    TEAMS = "teams"
    PUSHBYTECHULUS = "PushByTechulus"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    WECOM = "WeCom"


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
    NotificationType.BARK: [
        "barkEndpoint",
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
    NotificationType.NTFY: [
        "ntfyserverurl",
        "ntfytopic",
        "ntfyPriority",
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
    NotificationType.TEAMS: [
        "webhookUrl",
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
}
