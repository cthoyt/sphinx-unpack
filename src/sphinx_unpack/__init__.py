"""A Sphinx plugin that automatically documents type-annotated variadic keyword arguments."""

from __future__ import annotations

import inspect
import typing
from typing import Annotated, Any, NamedTuple, cast

from sphinx.application import Sphinx
from typing_extensions import Doc, ParamSpec, TypeVar, Unpack

__all__ = [
    "TypePair",
    "get_typeddict_docstrs",
    "get_unpacked_typed_dict_cls",
    "process_docstring",
    "setup",
]

P = ParamSpec("P")
T = TypeVar("T")


def setup(app: Sphinx) -> dict[str, Any]:
    """Attach the docstring processing function to the Sphinx app."""
    _register(app, process_docstring)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def _register(app: Sphinx, function: typing.Callable[P, T]) -> int:
    # this implements the secret naming convention for functions
    # to register with the app. I don't understand it
    norm_func_name = function.__name__.replace("_", "-")
    name = f"autodoc-{norm_func_name}"
    return app.connect(name, function)


def get_unpacked_typed_dict_cls(func: typing.Callable[P, T]) -> type | None:
    """Get the typed dict annotated on the function's variadic kwargs via Unpack."""
    sig = inspect.signature(func)
    for _name, param in sig.parameters.items():
        if param.kind != inspect.Parameter.VAR_KEYWORD:
            continue
        if typing.get_origin(param.annotation) is not Unpack:
            continue
        typed_dict_class = typing.get_args(param.annotation)[0]
        return cast(type, typed_dict_class)
    return None


class TypePair(NamedTuple):
    """A pair of a type and optional docstring."""

    type: type
    docstring: str | None


def get_typeddict_docstrs(typed_dict: type) -> dict[str, TypePair]:
    """Get a dictionary from fields in a TypedDict to their type/doc.

    Note, Python does not have a built-in mechanism to recognize nor access docstrings
    on attributes of classes. Sphinx is able to do this in a few places, but their code
    is totally impenetrable, so this implementation asks you to use the more explicit
    :class:`typing.Doc` construct like in the following:

    .. code-block:: python

        from typing import Annotated, Doc, TypedDict


        class GreetingKwargs(TypedDict):
            name: Annotated[str, Doc("the person to greet")]
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


def _process_docstring_helper(obj: typing.Callable[P, T], lines: list[str]) -> None:
    typed_dict_cls = get_unpacked_typed_dict_cls(obj)
    if typed_dict_cls is None:
        return None
    data = get_typeddict_docstrs(typed_dict_cls)

    already_documented = _identify_already_documented(lines)
    doc_lines: list[str] = []
    for param_name, (type_str, doc) in data.items():
        if param_name in already_documented:
            continue
        if doc:
            doc_lines.append(f":param {type_str.__name__} {param_name}: {doc}")
        else:
            doc_lines.append(f":type {param_name}: {type_str.__name__}")

    _insert(lines, doc_lines)
    return None


def _identify_already_documented(lines: list[str]) -> set[str]:
    # TODO
    return set()


def process_docstring(
    app: Sphinx, what: str, name: str, obj: Any, options: Any, lines: list[str]
) -> None:
    """Insert docstrings based on type-annotated variadic kwargs."""
    if what != "function":
        return None
    _process_docstring_helper(obj, lines)
    return None


PARTS = {":return:", ":returns:", ":rtype:"}


def _insert(lines: list[str], doc_lines: list[str]) -> None:
    position, add_extra_lines = _get_position(lines)
    if add_extra_lines:
        lines[position:position] = ["", *doc_lines]
    else:
        lines[position:position] = doc_lines


def _get_position(lines: list[str]) -> tuple[int, bool]:
    """Get the position where new lines should be inserted."""
    try:
        position = min(i for i, line in enumerate(lines) if any(part in line for part in PARTS))
    except ValueError:
        try:
            # if there aren't any lines inside the docstring that are already
            # the return values, then we will look for the first blank line
            # to insert it into. This is because the convention for docstrings
            # is that the first line is a short explanation of what the function
            # does, then the rest is long-form explanation. So stick the params
            # first before the long-form explanation
            position = min(i for i, line in enumerate(lines) if not line.strip())
        except ValueError:
            # there are no blank lines, just pick the end
            # find the first empty line and stick it there
            position = len(lines)
        return position, True
    else:
        return position, False
