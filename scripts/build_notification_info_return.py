from uptime_kuma_api import notification_provider_options


def build_providers():
    providers = []
    for provider_enum in notification_provider_options:
        provider = provider_enum.__dict__["_value_"]
        providers.append(provider)
    return providers


for provider in build_providers():
    options = notification_provider_options[provider]
    for option in options:
        print(f'{option}:')
        print(f'  description: {provider} provider option.')
        print(f'  returned: if type is {provider}')
        print('  type: str')
