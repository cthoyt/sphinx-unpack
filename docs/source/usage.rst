Usage
=====

Sphinx plugins are typically pretty hard to use.

Here's a minimal example project with the following format:

.. code-block::

    .
    ├── docs
    │   ├── conf.py
    │   ├── index.rst
    ├── src
    │   ├── awkward_octopus
    │      ├── __init__.py
    └── pyproject.toml

Here's what you need in ``docs/conf.py``:

.. code-block:: python

    # conf.py
    project = "Sphinx Unpack Demo"
    extensions = [
        # maybe these are required? I can't imagine using
        # Sphinx for anything without them
        "sphinx.ext.autosummary",
        "sphinx.ext.autodoc",
        "sphinx_autodoc_typehints",
        # this is the important part!
        "sphinx_unpack",
    ]

Inside your ``docs/index.rst``, you need to include
at minimum ``.. automodule:: awkward_octopus``
(sorry, I couldn't figure out how to escape it in here with
a full file example).

Here's what you need in ``pyproject.toml``:

.. code-block:: toml

    # pyproject.toml
    [build-system]
    requires = ["uv_build>=0.6.6,<1.0"]
    build-backend = "uv_build"

    [project]
    name = "awkward_octopus"
    version = "0.0.1-dev"

    requires-python = ">=3.10"
    dependencies = [
        "typing-extensions",
    ]

    [dependency-groups]
    docs = [
        "sphinx>=8",
        "sphinx-autodoc-typehints",
        "sphinx-unpack",
    ]

Here's what you need in ``src/awkward_octopus/__init__.py``:

.. code-block:: python

    # __init__.py
    from typing_extensions import Unpack, TypedDict, Annotated, Doc

    __all__ = [
        "greet",
    ]


    class GreetingKwargs(TypedDict):
        """Keyword argument used for greetings."""

        name: Annotated[str, Doc("The name of the person to greet")]


    def greet(**kwargs: Unpack[GreetingKwargs]) -> str:
        """Return a greeting.

        :return: A greeting
        """
        return f"Hello, {kwargs['name']}!"

This is *probably* a minimum viable example! Then, in the root, run the following
commands to build the docs and open them up:

.. code-block:: console

    $ uv run --group docs sphinx-build docs/ docs/build/
    $ open docs/build/index.html
