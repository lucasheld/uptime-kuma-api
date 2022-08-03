import re
from pprint import pprint


def parse_data_keys(data):
    keys = []
    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^([^:]+):', line)  # example: "type: this.type,"
        if match:
            key = match.group(1)
        else:
            key = line.rstrip(",")  # example: "notificationIDList,"
        keys.append(key)
    return keys


def parse_heartbeat():
    with open('uptime-kuma/server/model/heartbeat.js') as f:
        content = f.read()
    all_keys = []
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    all_keys.extend(keys)
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    all_keys.extend(keys)
    all_keys = list(set(all_keys))
    return all_keys


def parse_incident():
    with open('uptime-kuma/server/model/incident.js') as f:
        content = f.read()
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    return keys


def parse_monitor():
    # todo: toPublicJSON ???
    with open('uptime-kuma/server/model/monitor.js') as f:
        content = f.read()
    matches = re.findall(r'data = {([^}]+)}', content)
    all_keys = []
    for match in matches:
        keys = parse_data_keys(match)
        keys = [i for i in keys if i != "...data"]
        all_keys.extend(keys)
    return all_keys


def parse_proxy():
    with open('uptime-kuma/server/model/proxy.js') as f:
        content = f.read()
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    return keys


def parse_status_page():
    with open('uptime-kuma/server/model/status_page.js') as f:
        content = f.read()
    all_keys = []
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    all_keys.extend(keys)
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    all_keys.extend(keys)
    all_keys = list(set(all_keys))
    return all_keys


def parse_tag():
    with open('uptime-kuma/server/model/tag.js') as f:
        content = f.read()
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_data_keys(data)
    return keys


pprint(parse_heartbeat())
pprint(parse_incident())
pprint(parse_monitor())
pprint(parse_proxy())
pprint(parse_status_page())
pprint(parse_tag())


# TODO:
# https://github.com/louislam/uptime-kuma/blob/2adb142ae25984ecebfa4b51c739fec5e492763a/server/proxy.js#L20
# https://github.com/louislam/uptime-kuma/blob/239611a016a85712305100818d4c7b88a14664a9/server/socket-handlers/status-page-socket-handler.js#L118
