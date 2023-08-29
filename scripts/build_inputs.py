import glob
import re
from bs4 import BeautifulSoup

from utils import deduplicate_list, parse_vue_template, diff, type_html_to_py


input_ignores = {
    "settings": [
        "$root.styleElapsedTime"
    ]
}


def parse_model_keys(content, object_name):
    soup = BeautifulSoup(content, "html.parser")

    soup_inputs = soup.find_all(attrs={"v-model": True})
    inputs = []
    for soup_input in soup_inputs:
        key = soup_input["v-model"]
        if key in input_ignores.get(object_name, []):
            continue
        else:
            key = re.sub(r'^' + object_name + r'\.', "", key)
            type_ = soup_input.get("type", "text")
            type_ = type_html_to_py(type_)
            if type_ == "bool":
                value = True if soup_input.get("checked") else False
            else:
                value = soup_input.get("value")
            inputs.append({
                "key": key,
                "type": type_,
                "default": value,
            })
    return inputs


def parse_proxy_keys(root):
    content = parse_vue_template(f"{root}/src/components/ProxyDialog.vue")
    keys = parse_model_keys(content, "proxy")
    return keys


def parse_notification_keys(root):
    content = parse_vue_template(f"{root}/src/components/NotificationDialog.vue")
    keys = parse_model_keys(content, "notification")
    return keys


def parse_settings_keys(root):
    all_keys = []
    for path in glob.glob(f'{root}/src/components/settings/*'):
        content = parse_vue_template(path)
        keys = parse_model_keys(content, "settings")
        all_keys.extend(keys)
    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_monitor_keys(root):
    content = parse_vue_template(f"{root}/src/pages/EditMonitor.vue")
    keys = parse_model_keys(content, "monitor")
    return keys


def parse_status_page_keys(root):
    all_keys = ["id"]

    content = parse_vue_template(f"{root}/src/pages/StatusPage.vue")
    keys = parse_model_keys(content, "config")
    all_keys.extend(keys)

    content = parse_vue_template(f"{root}/src/pages/ManageStatusPage.vue")
    keys = parse_model_keys(content, "statusPage")
    all_keys.extend(keys)

    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_maintenance_keys(root):
    content = parse_vue_template(f"{root}/src/pages/EditMaintenance.vue")
    keys = parse_model_keys(content, "maintenance")
    return keys


def main():
    root_old = "uptime-kuma-old"
    root_new = "uptime-kuma"

    for name, func in [
        ["proxy", parse_proxy_keys],
        ["notification", parse_notification_keys],
        ["settings", parse_settings_keys],
        ["monitor", parse_monitor_keys],
        ["status_page", parse_status_page_keys],
        ["maintenance", parse_maintenance_keys],
    ]:
        keys_old = func(root_old)
        keys_new = func(root_new)
        print(f"{name}:")
        diff(keys_old, keys_new)


if __name__ == "__main__":
    main()
