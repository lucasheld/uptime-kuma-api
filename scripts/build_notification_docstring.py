from uptime_kuma_api import notification_provider_options

data = {
    "lunaseaTarget": """Allowed values: "device", "user".""",

    "lunaseaUserID": """User ID.""",

    "lunaseaDevice": """Device ID.""",

    "pagertreeAutoResolve": """

    Available values are:
    
    - ``0``: Do Nothing
    - ``resolve``: Auto Resolve""",

    "pagertreeUrgency": """

    Available values are:
    
    - ``silent``: Silent
    - ``low``: Low
    - ``medium``: Medium
    - ``high``: High
    - ``critical``: Critical""",

    "promosmsAllowLongSMS": "Allow long SMS.",

    "promosmsPhoneNumber": "Phone number (for Polish recipient You can skip area codes).",

    "promosmsSMSType": """
    
    Available values are:
    
    - ``0``: SMS FLASH - Message will automatically show on recipient device. Limited only to Polish recipients.
    - ``1``: SMS ECO - cheap but slow and often overloaded. Limited only to Polish recipients.
    - ``3``: SMS FULL - Premium tier of SMS, You can use your Sender Name (You need to register name first). Reliable for alerts.
    - ``4``: SMS SPEED - Highest priority in system. Very quick and reliable but costly (about twice of SMS FULL price).""",

    "smseagleEncoding": "True to send messages in unicode.",

    "smseaglePriority": "Message priority (0-9, default = 0).",

    "smseagleRecipientType": """Recipient type.
    
    Available values are:
    
    - ``smseagle-to``: Phone number(s)
    - ``smseagle-group``: Phonebook group name(s)
    - ``smseagle-contact``: Phonebook contact name(s)""",

    "smseagleToken": "API Access token.",

    "smseagleRecipient": "Recipient(s) (multiple must be separated with comma).",

    "smseagleUrl": "Your SMSEagle device URL.",

    "splunkAutoResolve": """Auto resolve or acknowledged.

    Available values are:
    
    - ``0``: do nothing
    - ``ACKNOWLEDGEMENT``: auto acknowledged
    - ``RECOVERY``: auto resolve""",

    "splunkSeverity": """Severity.

    Available values are:
    
    - ``INFO``
    - ``WARNING``
    - ``CRITICAL``""",

    "splunkRestURL": "Splunk Rest URL.",

    "opsgeniePriority": "Priority. Available values are numbers between ``1`` and ``5``.",

    "opsgenieRegion": """Region. Available values are:
    
    - ``us``: US (Default)
    - ``eu``: EU""",

    "opsgenieApiKey": "API Key.",

    "twilioAccountSID": "Account SID.",

    "twilioAuthToken": "Auth Token.",

    "twilioToNumber": "To Number.",

    "twilioFromNumber": "From Number.",

    "pushoverttl": "Message TTL (Seconds).",

    "ntfyaccesstoken": "Access Token.",

    "ntfyAuthenticationMethod": "Authentication Method.",
}

for provider in notification_provider_options:
    provider_options = notification_provider_options[provider]
    for option in provider_options:
        type_ = provider_options[option]["type"]
        required = provider_options[option]["required"]
        text = data.get(option)
        line = f":param {type_}{', optional' if required else ''} {option}: Notification option for ``type`` :attr:`~.NotificationType.{provider.name}`."
        if text:
            line += f" {text}"
        print(line)
