import glob
import re

import jinja2

notification_providers = []


def deduplicate_list(l):
    out = []
    for i in l:
        if i not in out:
            out.append(i)
    return out


for path in glob.glob('uptime-kuma/server/notification-providers/*'):
    with open(path) as f:
        content = f.read()
    match = re.search(r'class [^ ]+ extends NotificationProvider {', content)
    if match:
        match = re.search(r'name = "([^"]+)";', content)
        name = match.group(1)

        inputs = re.findall(r'notification\.([^ ,.;})\]]+)', content)
        inputs = deduplicate_list(inputs)
        inputs = [i.strip() for i in inputs]

        notification_providers.append({
            "name": name,
            "inputs": inputs,
        })

print(notification_providers)


def write_to_file(template, destination, **kwargs):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    template = env.get_template(template)
    rendered = template.render(**kwargs)
    with open(destination, "w") as f:
        f.write(rendered)


write_to_file("notification_providers.py.j2", "./../uptimekumaapi/notification_providers.py", notification_providers=notification_providers)
