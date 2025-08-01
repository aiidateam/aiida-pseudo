# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import aiida_pseudo

# -- Project information -----------------------------------------------------

project = 'aiida-pseudo'
copyright = """\
2020-2022, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre
for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland
"""
release = aiida_pseudo.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx_copybutton', 'autoapi.extension', 'sphinx_click', 'sphinx.ext.intersphinx', 'myst_parser']

# Settings for the `sphinx_copybutton` extension
copybutton_selector = 'div:not(.no-copy)>div.highlight pre'
copybutton_prompt_text = r'>>> |\.\.\. |(?:\(.*\) )?\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

# Settings for the `autoapi` extension
autoapi_dirs = ['../../src/aiida_pseudo']
autoapi_ignore = ['*cli*']

# Settings for the `sphinx.ext.intersphinx` extension
intersphinx_mapping = {
    'aiida': ('http://aiida-core.readthedocs.io/en/latest/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_css_files = [
    'aiida-custom.css',
    'aiida-pseudo-custom.css'
]
html_theme_options = {
    'home_page_in_toc': True,
    'repository_url': 'https://github.com/aiidateam/aiida-pseudo',
    'repository_branch': 'master',
    'use_repository_button': True,
    'use_issues_button': True,
    'use_fullscreen_button': False,
    'path_to_docs': 'docs',
    'use_edit_page_button': True,
    'extra_footer': '<p>Made possible by the support of <a href="http://nccr-marvel.ch/" target="_blank"> NCCR MARVEL</a>, <a href="http://www.max-centre.eu/" target="_blank"> MaX CoE</a> and the <a href="https://www.materialscloud.org/swissuniversities" target="_blank"> swissuniversities P-5 project</a>.</p>'
}
html_domain_indices = True
html_logo = '_static/logo.png'
