import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath('./_ext'))

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
