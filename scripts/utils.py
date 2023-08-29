import re
import jinja2


def deduplicate_list(l):
    out = []
    for i in l:
        if i not in out:
            out.append(i)
    return out


def parse_vue_template(path):
    with open(path) as f:
        vue = f.read()
    match = re.search(r'<template>[\s\S]+</template>', vue, re.MULTILINE)
    template = match.group(0)
    return template


def write_to_file(template, destination, **kwargs):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("./"))
    template = env.get_template(template)
    rendered = template.render(**kwargs)
    with open(destination, "w") as f:
        f.write(rendered)


def diff(old, new):
    for i in new:
        if i not in old:
            print("+", i)
    for i in old:
        if i not in new:
            print("-", i)
    print("")


def type_html_to_py(type_):
    if type_ == "number":
        type_ = "int"
    elif type_ == "checkbox":
        type_ = "bool"
    else:
        type_ = "str"
    return type_
