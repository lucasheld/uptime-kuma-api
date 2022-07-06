import re
import os

from uptimekumaapi import notification_provider_options


def build_notification_provider_map():
    params_map_notification_providers = {}

    for notification_provider in notification_provider_options:
        options = notification_provider_options[notification_provider]
        provider_name = notification_provider.__dict__["_value_"].lower().replace(".", "")
        for option in options:
            option_orig = option

            prefix = os.path.commonprefix([o.lower() for o in options] + [provider_name])
            option = option[len(prefix):]

            option = re.sub('([A-Z]+)', r'_\1', option).lower()
            option = provider_name + "_" + option
            option = option.replace("__", "_")

            params_map_notification_providers[option_orig] = option
    return params_map_notification_providers


notification_provider_map = build_notification_provider_map()
print("params_map_notification_provider =", notification_provider_map)
