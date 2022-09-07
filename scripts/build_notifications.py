import glob
import re

from bs4 import BeautifulSoup

from utils import deduplicate_list, write_to_file


def build_notification_providers():
    providers = []
    for path in glob.glob('uptime-kuma/server/notification-providers/*'):
        with open(path) as f:
            content = f.read()
        match = re.search(r'class [^ ]+ extends NotificationProvider {', content)
        if match:
            match = re.search(r'name = "([^"]+)";', content)
            name = match.group(1)

            inputs = re.findall(r'notification\.([^ ,.;})\]]+)', content)
            inputs = deduplicate_list(inputs)
            inputs = [i.strip() for i in inputs]

            providers.append({
                "name": name,
                "inputs": inputs,
            })
    return providers


def build_notification_provider_conditions():
    conditions = {}
    for path in glob.glob('uptime-kuma/src/components/notifications/*'):
        if path.endswith("index.js"):
            continue
        with open(path) as f:
            content = f.read()
        match = re.search(r'<template>[\s\S]+</template>', content, re.MULTILINE)
        html = match.group(0)
        soup = BeautifulSoup(html, "html.parser")
        inputs = soup.find_all("input")
        for input in inputs:
            condition = {}
            attrs = input.attrs
            v_model = attrs.get("v-model")
            min_ = attrs.get("min")
            max_ = attrs.get("max")
            if min_:
                condition["min"] = int(min_)
            if max_:
                condition["max"] = int(max_)
            param_name = re.match(r'\$parent.notification.(.*)$', v_model).group(1)
            if condition:
                conditions[param_name] = condition
    return conditions


notification_providers = build_notification_providers()
notification_provider_conditions = build_notification_provider_conditions()

write_to_file(
    "notification_providers.py.j2", "./../uptime_kuma_api/notification_providers.py",
    notification_providers=notification_providers,
    notification_provider_conditions=notification_provider_conditions
)
