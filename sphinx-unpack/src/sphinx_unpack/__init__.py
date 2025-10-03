"""Implementation of a Sphinx plugin to handle unpacking typed dicts in variadic keyword arguments."""

from __future__ import annotations

import inspect
import typing
from typing import Annotated, Any, NamedTuple
from typing_extensions import Doc, Unpack, TypedDict

from sphinx.application import Sphinx

__all__ = [
    "setup",
    "process_docstring",
    "TypePair",
    "get_typeddict_docstrs",
    "get_unpacked_typed_dict_cls",
]


def setup(app: Sphinx) -> dict[str, Any]:
    """Attach the docstring processing function to the Sphinx app."""
    _register(app, process_docstring)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _register(app: Sphinx, function) -> int:
    # this implements the secret naming convention for functions
    # to register with the app. I don't understand it
    norm_func_name = function.__name__.replace("_", "-")
    name = f"autodoc-{norm_func_name}"
    return app.connect(name, function)


def get_unpacked_typed_dict_cls(func: typing.Callable) -> type[TypedDict] | None:
    """Return the TypedDict class annotated with Unpack on the variadic keyword arguments to a function."""
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        if param.kind != inspect.Parameter.VAR_KEYWORD:
            continue
        if typing.get_origin(param.annotation) is not Unpack:
            continue
        typed_dict_class = typing.get_args(param.annotation)[0]
        return typed_dict_class
    return None


class TypePair(NamedTuple):
    """A pair of a type and optional docstring."""

    type: type
    docstring: str | None


def get_typeddict_docstrs(typed_dict: type[TypedDict]) -> dict[str, TypePair]:
    """Get a dictionary from fields in a TypedDict to their type/doc.

    Note, Python does not have a built-in mechanism to recognize nor access
    docstrings on attributes of classes. Sphinx is able to do this in a few
    places, but their code is totally impenetrable, so this implementation
    asks you to use the more explicit :class:`typing.Doc` construct like in
    the following:

    .. code-block:: python

        from typing import Annotated, Doc, TypedDict

        class GreetingKwargs(TypedDict):
            name: Annotated[str, Doc("the person to greet")
            title: Annotated[str | None, Doc("the optional title to use in their greeting")]
            favorite_color: str | None

    Not all arguments are required to have docs attached on to them.
    """
    hints = typing.get_type_hints(typed_dict, include_extras=True)
    result = {}
    for param_name, hint in hints.items():
        if typing.get_origin(hint) is not Annotated:
            result[param_name] = TypePair(hint, None)
        else:
            base_type, *metadata = typing.get_args(hint)
            result[param_name] = TypePair(base_type, _get_first_doc(metadata))
    return result


def _get_first_doc(args: typing.Iterable[Any]) -> str | None:
    for arg in args:
        if isinstance(arg, Doc):
            return arg.documentation
    return None


def process_docstring(
    app: Sphinx, what: str, name: str, obj: Any, options: Any, lines: list[str]
) -> None:
    """Append parameter docstrings and types based on unpacked typed dict annotations on variadic keyword arguments."""
    if what != "function":
        return None

    typed_dict_cls = get_unpacked_typed_dict_cls(obj)
    if typed_dict_cls is None:
        return None
    d = get_typeddict_docstrs(typed_dict_cls)

    doc_lines: list[str] = []
    for param_name, (type_str, doc) in d.items():
        if doc:
            doc_lines.append(f":param {param_name}: {doc}")

        doc_lines.append(f":type {param_name}: {type_str.__name__}")

    # TODO find the minimum index of lines that have :return: :returns: or :rtype:
    lines.extend(doc_lines)
    return None


PARTS = {":return:", ":returns:", ":rtype:"}


def _minimum(lines: list[str]) -> int:
    rv = min(i for i, line in enumerate(lines) if any(part in line for part in PARTS))
    return rv or len(lines)
