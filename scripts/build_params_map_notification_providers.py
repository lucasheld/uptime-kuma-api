import re

from uptime_kuma_api import notification_provider_options


params_map_notification_providers = {}

for notification_provider in notification_provider_options:
    provider_name_orig = notification_provider.__dict__["_value_"]
    provider_name = re.sub('([A-Z]+)', r'_\1', provider_name_orig).lower().replace(".", "_").strip("_")
    params_map_notification_providers[provider_name_orig] = provider_name
print(params_map_notification_providers)
