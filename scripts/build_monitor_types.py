from bs4 import BeautifulSoup

from utils import parse_vue_template, write_to_file


titles = {
    "http": "HTTP(s)",
    "port": "TCP Port",
    "ping": "Ping",
    "keyword": "HTTP(s) - Keyword",
    "grpc-keyword": "gRPC(s) - Keyword",
    "dns": "DNS",
    "docker": "Docker Container",
    "push": "Push",
    "steam": "Steam Game Server",
    "gamedig": "GameDig",
    "mqtt": "MQTT",
    "sqlserver": "Microsoft SQL Server",
    "postgres": "PostgreSQL",
    "mysql": "MySQL/MariaDB",
    "mongodb": "MongoDB",
    "radius": "Radius",
    "redis": "Redis",
    "group": "Group",
    "json-query": "HTTP(s) - Json Query",
    "real-browser": "HTTP(s) - Browser Engine (Chrome/Chromium)",
    "kafka-producer": "Kafka Producer",
    "tailscale-ping": "Tailscale Ping"
}


def parse_monitor_types():
    content = parse_vue_template("uptime-kuma/src/pages/EditMonitor.vue")

    soup = BeautifulSoup(content, "html.parser")
    select = soup.find("select", id="type")
    options = select.find_all("option")

    types = {}
    for o in options:
        type_ = o.attrs["value"]
        types[type_] = {
            "value": type_,
            "title": titles[type_]
        }
    return types


monitor_types = parse_monitor_types()

write_to_file(
    "monitor_type.py.j2", "./../uptime_kuma_api/monitor_type.py",
    monitor_types=monitor_types
)
