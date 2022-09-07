from bs4 import BeautifulSoup

from utils import parse_vue_template, write_to_file


def parse_monitor_types():
    content = parse_vue_template("uptime-kuma/src/pages/EditMonitor.vue")

    soup = BeautifulSoup(content, "html.parser")
    select = soup.find("select", id="type")
    options = select.find_all("option")

    types = []
    for o in options:
        type_ = o.attrs["value"]
        types.append(type_)
    return types


monitor_types = parse_monitor_types()

write_to_file(
    "monitor_type.py.j2", "./../uptime_kuma_api/monitor_type.py",
    monitor_types=monitor_types
)
