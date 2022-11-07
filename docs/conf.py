#!/usr/bin/env python3
# built-in
import os
import sys
from datetime import date
from pathlib import Path

# external
import alabaster

# app
from flakeheaven import __version__

_docs_dir = Path(__file__).parent.resolve()
_root_dir = _docs_dir.parent
_package = _root_dir / 'src/flakeheaven'
_templates = _docs_dir / 'templates'
_apidoc_dst = _docs_dir / 'apidoc'

sys.path.append(os.path.abspath('../'))
extensions = [
    'alabaster',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['templates']
source_suffix = ['.rst', '.md']
root_doc = 'index'

project = 'FlakeHeaven'
copyright = '{}, Gram (@orsinium)'.format(date.today().year)
author = 'Gram (@orsinium)'

version = __version__
release = version

language = 'en'
exclude_patterns = []
todo_include_todos = True

pygments_style = 'sphinx'
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
html_static_path = [str(_root_dir / 'assets')]
html_theme_options = {
    # 'logo': 'logo.png',
    # 'logo_name': 'false',
    'description': 'Flake8 wrapper to make it nice, legacy-friendly, configurable.',

    'sidebar_width': '240px',
    'show_powered_by': 'false',
    'caption_font_size': '20px',

    # 'color': '#2c3e50',
    'github_banner': 'true',
    'github_user': 'flakeheaven',
    'github_repo': 'flakeheaven',
    'github_type': 'star',

    'extra_nav_links': {
        'GitHub repository': 'https://github.com/flakeheaven/flakeheaven',
    },
}


# -- autodoc config ---------------------------------------------------
autoclass_content = 'both'

# -- napoleon config ---------------------------------------------------
# See https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#getting-started
napoleon_google_docstring = True
# napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False
napoleon_preprocess_types = True
# napoleon_use_ivar = False
# napoleon_use_param = True
# napoleon_use_rtype = True
# napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'flakeheavendoc'


# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (root_doc, 'flakeheaven.tex', 'FlakeHeaven Documentation',
     '@orsinium', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(root_doc, 'flakeheaven', 'FlakeHeaven Documentation', [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (root_doc, 'flakeheaven', 'FlakeHeaven Documentation',
     author, 'FlakeHeaven', 'One line description of project.', 'Miscellaneous'),
]


def run_apidoc(_):
    from sphinx.ext.apidoc import main as apidoc_exec

    exclude_patterns = (
        _package / '__main__.py',
    )
    apidoc_exec([
        f'--templatedir={_templates}',
        '--separate',
        '--module-first',
        '--force',
        '--private',
        f'-o={_apidoc_dst}',
        f'{_package}',
        f'{", ".join(map(str, exclude_patterns))}',
    ])


def setup(app):
    app.connect('builder-inited', run_apidoc)
