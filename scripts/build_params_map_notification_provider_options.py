import re
import os
import jinja2

from uptime_kuma_api import params_map_notification_providers, notification_provider_options


def build_notification_provider_map():
    params_map_notification_provider_options = {}

    for provider_sock, provider_py in params_map_notification_providers.items():
        options_sock = notification_provider_options[provider_sock]

        params_map_notification_provider_options[provider_py] = {}
        for option in options_sock:
            option_orig = option

            # for example for rocket_chat
            prefix = os.path.commonprefix([o.lower() for o in options_sock] + [provider_py])
            option = option[len(prefix):]

            option = re.sub('([A-Z]+)', r'_\1', option).lower()

            # for example for smtp
            if option.startswith(provider_py):
                option = option[len(provider_py):]

            option = provider_py + "_" + option
            option = option.replace("__", "_")

            params_map_notification_provider_options[provider_py][option_orig] = option
    return params_map_notification_provider_options


notification_provider_map = build_notification_provider_map()

env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
template = env.get_template("build_params_map_notification_provider_options.j2")
rendered = template.render(notification_provider_map=notification_provider_map)
print(rendered)
