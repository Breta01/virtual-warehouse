# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import inspect
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
import virtual_warehouse

# -- Project information -----------------------------------------------------

project = "Virtual Warehouse"
copyright = "2021, Breta Hajek"
author = "Breta Hajek"

# The full version, including alpha/beta/rc tags
version = str(virtual_warehouse.__version__)
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",
    "sphinx.ext.linkcode",
    "sphinx_inline_tabs",
    "sphinx.ext.autosectionlabel",
]


autosectionlabel_maxdepth = 2

autosummary_generate = True

add_module_names = False
autoclass_content = "both"  # Add __init__ docstring to class def
autodoc_typehints = "description"
autodoc_default_options = {
    "members": True,
    # 'special-members': '__init__',
    "undoc-members": True,
    "inherited-members": False,
    "show-inheritance": True,
    "exclude-members": "__weakref__",
}

html_use_modindex = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    # "external_links": [{"name": "Breta Hajek", "url": "https://bretahajek.com/"}],
    "github_url": "https://github.com/Breta01/virtual-warehouse/",
    "twitter_url": "",
    "use_edit_page_button": True,
}


html_context = {
    "github_user": "Breta01",
    "github_repo": "virtual-warehouse",
    "github_version": "master",
    "doc_path": "docs/source",
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = [
    "css/custom.css",
]

# Footer
html_show_sphinx = False

# Napoleon - docstring parser
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_rtype = False  # Don't make separate field for return type

# based on numpy doc/source/conf.py
def linkcode_resolve(domain, info):
    """
    Determine the URL corresponding to Python object
    """
    if domain != "py":
        return None

    modname = info["module"]
    fullname = info["fullname"]

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            return None

    try:
        fn = inspect.getsourcefile(inspect.unwrap(obj))
    except TypeError:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        lineno = None

    if lineno:
        linespec = f"#L{lineno}-L{lineno + len(source) - 1}"
    else:
        linespec = ""

    fn = os.path.relpath(fn, start=os.path.dirname(virtual_warehouse.__file__))

    if "+" in virtual_warehouse.__version__:
        return f"https://github.com/Breta01/virtual-warehouse/blob/master/virtual_warehouse/{fn}{linespec}"
    else:
        return (
            f"https://github.com/Breta01/virtual-warehouse/blob/"
            f"v{virtual_warehouse.__version__}/virtual_warehouse/{fn}{linespec}"
        )
