# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../pyastrobackend'))
print(sys.path)

autodoc_mock_imports = ['win32com', 'pythoncom', 'comtypes']

# -- Project information -----------------------------------------------------

project = 'pyastrobackend'
copyright = '2019, Michael Fulbright'
author = 'Michael Fulbright'

# The short X.Y version
version = ''

# The full version, including alpha/beta/rc tags
release = '0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# extensions = [
#     'sphinx.ext.autodoc',
#     'sphinx.ext.doctest',
#     'sphinx.ext.intersphinx',
#     'sphinx.ext.todo',
#     'sphinx.ext.coverage',
#     'sphinx.ext.mathjax',
#     'sphinx.ext.ifconfig',
#     'sphinx.ext.viewcode',
#     'sphinx.ext.githubpages',
# ]

extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.autosummary',
        'sphinx.ext.autosectionlabel',
        'sphinx.ext.napoleon',
        'sphinx_rtd_theme'
]


# prevent name collision from 'Bugfixes' in all release notes
autosectionlabel_prefix_document = True

# disable Google style (use NumPy)
napoleon_google_docstring = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

autosummary_generate = True

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# document __init__() also
autoclass_content = 'both'

master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'agogo'
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {
#                         'body_max_width' : '80%'
#                      }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
