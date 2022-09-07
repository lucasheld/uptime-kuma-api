import glob
import re

from utils import deduplicate_list, parse_vue_template


def parse_model_keys(content, object_name):
    match = re.findall(object_name + r"\.[0-9a-zA-Z_$]+", content)
    keys = []
    for m in match:
        key = m.replace(object_name + ".", "")
        keys.append(key)
    keys = deduplicate_list(keys)
    return keys


def parse_proxy_keys():
    content = parse_vue_template("uptime-kuma/src/components/ProxyDialog.vue")
    keys = parse_model_keys(content, "proxy")
    return keys


def parse_notification_keys():
    content = parse_vue_template("uptime-kuma/src/components/NotificationDialog.vue")
    keys = parse_model_keys(content, "notification")
    return keys


def parse_settings_keys():
    all_keys = []
    for path in glob.glob('uptime-kuma/src/components/settings/*'):
        content = parse_vue_template(path)
        keys = parse_model_keys(content, "settings")
        all_keys.extend(keys)
    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_monitor_keys():
    content = parse_vue_template("uptime-kuma/src/pages/EditMonitor.vue")
    keys = parse_model_keys(content, "monitor")
    return keys


def parse_status_page_keys():
    all_keys = ["id"]

    content = parse_vue_template("uptime-kuma/src/pages/StatusPage.vue")
    keys = parse_model_keys(content, "config")
    all_keys.extend(keys)

    content = parse_vue_template("uptime-kuma/src/pages/ManageStatusPage.vue")
    keys = parse_model_keys(content, "statusPage")
    all_keys.extend(keys)

    all_keys = deduplicate_list(all_keys)
    return all_keys


def main():
    proxy_keys = parse_proxy_keys()
    print("proxy:", proxy_keys)

    notification_keys = parse_notification_keys()
    print("notification:", notification_keys)

    settings_keys = parse_settings_keys()
    print("settings:", settings_keys)

    monitor_keys = parse_monitor_keys()
    print("monitor:", monitor_keys)

    status_page_keys = parse_status_page_keys()
    print("status_page:", status_page_keys)


if __name__ == "__main__":
    main()
