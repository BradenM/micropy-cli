# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys

import recommonmark
from recommonmark.transform import AutoStructify

sys.path.insert(0, os.path.abspath('..'))


source_suffix = ['.rst', '.md']

# -- Project information -----------------------------------------------------

project = 'micropy-cli'
copyright = '2019, Braden Mars'
author = 'Braden Mars'

github_doc_root = 'https://github.com/BradenM/micropy-cli/tree/master/docs/'

# The full version, including alpha/beta/rc tags
release = '3.4.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.coverage',
              'sphinx.ext.napoleon',
              'sphinx_autodoc_typehints',
              'sphinx.ext.autosummary',
              'sphinx.ext.autosectionlabel',
              'sphinx_click.ext',
              'recommonmark']

autodoc_default_flags = ['members',
                         'show-inheritance']  # Defaults
autosummary_generate = True  # Enable Autosummary
autosummary_imported_members = True
autosectionlabel_prefix_document = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# At the bottom of conf.py


def setup(app):
    app.add_config_value(
        'recommonmark_config',
        {
            'url_resolver': lambda url: github_doc_root + url,
            'auto_toc_tree_section': 'Contents',
            'enable_eval_rst': True,
        },
        True)
    app.add_transform(AutoStructify)
