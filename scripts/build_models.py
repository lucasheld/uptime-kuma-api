import re

from utils import deduplicate_list, diff


def parse_json_keys(data):
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


def parse_heartbeat(root):
    with open(f'{root}/server/model/heartbeat.js') as f:
        content = f.read()
    all_keys = []
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    all_keys.extend(keys)
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    all_keys.extend(keys)
    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_incident(root):
    with open(f'{root}/server/model/incident.js') as f:
        content = f.read()
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    return keys


def parse_monitor(root):
    # todo: toPublicJSON ???
    with open(f'{root}/server/model/monitor.js') as f:
        content = f.read()
    matches = re.findall(r'data = {([^}]+)}', content)
    all_keys = []
    for match in matches:
        keys = parse_json_keys(match)
        keys = [i for i in keys if i != "...data"]
        all_keys.extend(keys)
    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_proxy(root):
    with open(f'{root}/server/model/proxy.js') as f:
        content = f.read()
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    return keys


# def parse_function(regex_name, content):
#     match = re.search(regex_name, content)
#     name = match.group(0)
#     rest = "".join(content.split(name)[1:])
#
#     brackets = 0
#     opening_bracket_found = False
#     code = ""
#     for i in rest:
#         code += i
#         if i == "{":
#             opening_bracket_found = True
#             brackets += 1
#         if i == "}":
#             opening_bracket_found = True
#             brackets -= 1
#         if opening_bracket_found and brackets == 0:
#             break
#     return code


# # input (add, edit proxy)
# def parse_proxy2():
#     with open(f'{root}/server/proxy.js') as f:
#         content = f.read()
#
#     code = parse_function(r'async save\([^)]+\) ', content)
#     keys = parse_object_keys(code, "proxy")
#     return keys


def parse_status_page(root):
    with open(f'{root}/server/model/status_page.js') as f:
        content = f.read()
    all_keys = []
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    all_keys.extend(keys)
    match = re.search(r'toPublicJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    all_keys.extend(keys)
    all_keys = deduplicate_list(all_keys)
    return all_keys


def parse_tag(root):
    with open(f'{root}/server/model/tag.js') as f:
        content = f.read()
    match = re.search(r'toJSON\(\) {\s+return.*{([^}]+)}', content)
    data = match.group(1)
    keys = parse_json_keys(data)
    return keys


if __name__ == "__main__":
    root_old = "uptime-kuma-old"
    root_new = "uptime-kuma"

    for name, func in [
        ["heartbeat", parse_heartbeat],
        ["incident", parse_incident],
        ["monitor", parse_monitor],
        ["proxy", parse_proxy],
        ["status page", parse_status_page],
        ["tag", parse_tag],
    ]:
        keys_old = func(root_old)
        keys_new = func(root_new)
        print(f"{name}:")
        diff(keys_old, keys_new)


# TODO:
# https://github.com/louislam/uptime-kuma/blob/2adb142ae25984ecebfa4b51c739fec5e492763a/server/proxy.js#L20
# https://github.com/louislam/uptime-kuma/blob/239611a016a85712305100818d4c7b88a14664a9/server/socket-handlers/status-page-socket-handler.js#L118
