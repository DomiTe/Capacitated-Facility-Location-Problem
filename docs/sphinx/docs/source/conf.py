# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ADM Semesterprojekt"
copyright = "2025, Ralf Lenz, Karl Blumenthal"
author = "Ralf Lenz, Karl Blumenthal"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


templates_path = ["_templates"]
exclude_patterns = []

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # für Google/NumPy-style docstrings
    "sphinx_autodoc_typehints",  # für Typannotationen
    "myst_parser",  # Markdown-Support
]

autodoc_typehints = "description"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme_options = {
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

html_theme = "sphinx_rtd_theme"
html_favicon = "_static/favicon.png"
html_static_path = ["_static"]


def setup(app):
    app.add_css_file("custom.css")
