from uptime_kuma_api import notification_provider_options

for provider in notification_provider_options:
    provider_options = notification_provider_options[provider]
    for option in provider_options:
        type_ = provider_options[option]["type"]
        print(f":param {type_} {option}: (optional) Notification option for ``type`` :attr:`~.NotificationType.{provider.name}`")
