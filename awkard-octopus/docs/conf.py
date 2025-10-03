from datetime import date

project = "Sphinx Unpack Demo"
copyright = f"{date.today().year}, Charles Tapley Hoyt"
author = "Charles Tapley Hoyt"
version = "0.0.1-dev"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    # This is the module which can be imported directly.
    # inside the module is a ``setup()`` function
    #
    'sphinx_unpack',
]
