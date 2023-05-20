import glob
import re

from bs4 import BeautifulSoup

from utils import deduplicate_list, write_to_file


# deprecated or wrong inputs
ignored_inputs = {
    "slack": [
        "slackbutton"
    ],
    "rocket.chat": [
        "rocketbutton"
    ],
    "octopush": [
        "octopushDMLogin",
        "octopushDMAPIKey",
        "octopushDMPhoneNumber",
        "octopushDMSenderName",
        "octopushDMSMSType"
    ],
    "Splunk": [
        "pagerdutyIntegrationKey"
    ]
}

titles = {
    "alerta": "Alerta",
    "AlertNow": "AlertNow",
    "apprise": "Apprise (Support 50+ Notification services)",
    "Bark": "Bark",
    "clicksendsms": "ClickSend SMS",
    "discord": "Discord",
    "GoogleChat": "Google Chat (Google Workspace)",
    "gorush": "Gorush",
    "gotify": "Gotify",
    "HomeAssistant": "Home Assistant",
    "Kook": "Kook",
    "line": "LINE Messenger",
    "LineNotify": "LINE Notify",
    "lunasea": "LunaSea",
    "matrix": "Matrix",
    "mattermost": "Mattermost",
    "ntfy": "Ntfy",
    "octopush": "Octopush",
    "OneBot": "OneBot",
    "Opsgenie": "Opsgenie",
    "PagerDuty": "PagerDuty",
    "pushbullet": "Pushbullet",
    "PushByTechulus": "Push by Techulus",
    "pushover": "Pushover",
    "pushy": "Pushy",
    "rocket.chat": "Rocket.Chat",
    "signal": "Signal",
    "slack": "Slack",
    "squadcast": "SquadCast",
    "SMSEagle": "SMSEagle",
    "smtp": "Email (SMTP)",
    "stackfield": "Stackfield",
    "teams": "Microsoft Teams",
    "telegram": "Telegram",
    "twilio": "Twilio",
    "Splunk": "Splunk",
    "webhook": "Webhook",
    "GoAlert": "GoAlert",
    "ZohoCliq": "ZohoCliq",
    "AliyunSMS": "AliyunSMS",
    "DingDing": "DingDing",
    "Feishu": "Feishu",
    "FreeMobile": "FreeMobile (mobile.free.fr)",
    "PushDeer": "PushDeer",
    "promosms": "PromoSMS",
    "serwersms": "SerwerSMS.pl",
    "SMSManager": "SmsManager (smsmanager.cz)",
    "WeCom": "WeCom",
    "ServerChan": "ServerChan",
}


def build_notification_providers(root):
    providers = {}

    # get providers and input names
    for path in sorted(glob.glob(f'{root}/server/notification-providers/*')):
        with open(path) as f:
            content = f.read()
        match = re.search(r'class [^ ]+ extends NotificationProvider {', content)
        if match:
            match = re.search(r'name = "([^"]+)";', content)
            name = match.group(1)

            inputs = re.findall(r'notification\??\.([^ ,.;})\]]+)', content)
            inputs = deduplicate_list(inputs)
            inputs = [i.strip() for i in inputs]

            providers[name] = {
                "title": titles.get(name, name),
                "inputs": {},
            }
            for input_ in inputs:
                if input_ not in ignored_inputs.get(name, []):
                    providers[name]["inputs"][input_] = {}

    # get inputs
    for path in glob.glob(f'{root}/src/components/notifications/*'):
        if path.endswith("index.js"):
            continue
        with open(path) as f:
            content = f.read()
        match = re.search(r'<template>[\s\S]+</template>', content, re.MULTILINE)
        html = match.group(0)
        soup = BeautifulSoup(html, "html.parser")
        inputs = soup.find_all(attrs={"v-model": True})
        for input_ in inputs:
            conditions = {}
            attrs = input_.attrs
            v_model = attrs.get("v-model")
            param_name = re.match(r'\$parent.notification.(.*)$', v_model).group(1)

            type_ = attrs.get("type")
            if type_ == "number":
                type_ = "int"
            elif type_ == "checkbox":
                type_ = "bool"
            else:
                type_ = "str"

            required_true_values = ['', 'true']
            if attrs.get("required") in required_true_values or attrs.get(":required") in required_true_values:
                required = True
            else:
                required = False

            min_ = attrs.get("min")
            if min_:
                conditions["min"] = int(min_)

            max_ = attrs.get("max")
            if max_:
                conditions["max"] = int(max_)

            # find provider inputs dict
            input_found = False
            for name in list(providers.keys()):
                inputs = providers[name]["inputs"]
                for provider_input in inputs:
                    if provider_input == param_name:
                        input_found = True
                        providers[name]["inputs"][provider_input] = {
                            "conditions": conditions,
                            "type": type_,
                            "required": required
                        }
            assert input_found
    return providers


def diff(old, new):
    for i in new:
        if i not in old:
            print("+", i)
    for i in old:
        if i not in new:
            print("-", i)
    print("")


notification_providers = build_notification_providers("uptime-kuma")

notification_provider_conditions = {}
for notification_provider in notification_providers:
    for notification_provider_input_name in notification_providers[notification_provider]["inputs"]:
        notification_provider_input = notification_providers[notification_provider]["inputs"][notification_provider_input_name]
        if notification_provider_input["conditions"]:
            notification_provider_conditions[notification_provider_input_name] = notification_provider_input["conditions"]

write_to_file(
    "notification_providers.py.j2", "./../uptime_kuma_api/notification_providers.py",
    notification_providers=notification_providers,
    notification_provider_conditions=notification_provider_conditions
)

# notification_providers_old = build_notification_providers("uptime-kuma-old")
# notification_providers_new = build_notification_providers("uptime-kuma")
# diff(notification_providers_old, notification_providers_new)
#
# notification_provider_conditions_old = build_notification_provider_conditions("uptime-kuma-old")
# notification_provider_conditions_new = build_notification_provider_conditions("uptime-kuma")
# diff(notification_provider_conditions_old, notification_provider_conditions_new)
