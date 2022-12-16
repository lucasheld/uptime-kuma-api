# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
import uptime_kuma_api

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'uptime-kuma-api'
copyright = '2022, Lucas Held'
author = 'Lucas Held'

version = uptime_kuma_api.__version__
release = uptime_kuma_api.__version__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

toc_object_entries_show_parents = "hide"
autodoc_member_order = "bysource"
add_module_names = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    "show_powered_by": False,
    "github_user": "lucasheld",
    "github_repo": "uptime-kuma-api",
    "github_banner": True,
    "show_related": False,
    "note_bg": "#FFF59C",
    "github_button": True,
    "github_type": "star"
}
