from uptime_kuma_api import params_map_notification_providers, notification_provider_options, params_map_notification_provider_options, convert_from_socket

for provider_sock, provider_py in params_map_notification_providers.items():
    options = notification_provider_options[provider_sock]
    tmp = options

    params_map = params_map_notification_provider_options[provider_py]
    options = convert_from_socket(params_map, options)

    for option in options:
        print(f'{option}:')
        print(f'  description: {provider_py} provider option.')
        print(f'  returned: if type is {provider_py}')
        print('  type: str')
