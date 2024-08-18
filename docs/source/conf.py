# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "install_process"
copyright = "2024, zaicruvoir1rominet"
author = "zaicruvoir1rominet"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
master_doc = "index"
language = "en"
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {"logo_only": False}
html_static_path = ['_static']

# -- Options for myst-parser -------------------------------------------------
myst_enable_extensions = [
  "attrs_block",
  "attrs_inline",
  "colon_fence",
  "deflist",
]
