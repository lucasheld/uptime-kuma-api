# uptime-kuma-api

A wrapper for the Uptime Kuma Socket.IO API
---
uptime-kuma-api is a Python wrapper for the [Uptime Kuma](https://github.com/louislam/uptime-kuma) Socket.IO API.

This package was developed to configure Uptime Kuma with Ansible. The Ansible collection can be found at https://github.com/lucasheld/ansible-uptime-kuma.

Python version 3.7+ is required.

Supported Uptime Kuma versions:

| Uptime Kuma     | uptime-kuma-api |
|-----------------|-----------------|
| 1.21.3 - 1.23.1 | 1.0.0 - 1.2.0   |
| 1.17.0 - 1.21.2 | 0.1.0 - 0.13.0  |

Installation
---
uptime-kuma-api is available on the [Python Package Index (PyPI)](https://pypi.org/project/uptime-kuma-api/).

You can install it using pip:

```
pip install uptime-kuma-api
```

Documentation
---
The API Reference is available on [Read the Docs](https://uptime-kuma-api.readthedocs.io).

Example
---
Once you have installed the python package, you can use it to communicate with an Uptime Kuma instance.

To do so, import `UptimeKumaApi` from the library and specify the Uptime Kuma server url (e.g. 'http://127.0.0.1:3001'), username and password to initialize the connection.

```python
>>> from uptime_kuma_api import UptimeKumaApi, MonitorType
>>> api = UptimeKumaApi('INSERT_URL')
>>> api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
```

Now you can call one of the existing methods of the instance. For example create a new monitor:

```python
>>> result = api.add_monitor(type=MonitorType.HTTP, name="Google", url="https://google.com")
>>> print(result)
{'msg': 'Added Successfully.', 'monitorId': 1}
```

At the end, the connection to the API must be disconnected so that the program does not block.

```python
>>> api.disconnect()
```

With a context manager, the disconnect method is called automatically:

```python
from uptime_kuma_api import UptimeKumaApi

with UptimeKumaApi('INSERT_URL') as api:
    api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Google",
        url="https://google.com"
    )
```
