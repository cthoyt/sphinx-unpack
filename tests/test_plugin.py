"""Trivial version test."""

import unittest
from textwrap import dedent
from typing import Annotated, Any

from typing_extensions import Doc, TypedDict, Unpack

from sphinx_unpack import (
    TypePair,
    _get_position,
    _insert,
    get_typeddict_docstrs,
    get_unpacked_typed_dict_cls,
)
from sphinx_unpack.version import get_version


class TestVersion(unittest.TestCase):
    """Trivially test a version."""

    def test_version_type(self) -> None:
        """Test the version is a string.

        This is only meant to be an example test.
        """
        version = get_version()
        self.assertIsInstance(version, str)


class TestPlugin(unittest.TestCase):
    """Tests for the plugin."""

    def test_get_unpacked(self) -> None:
        """Test getting the unpacked type dict."""

        def func_0() -> None:
            """Return none when passing no arguments."""

        self.assertIsNone(get_unpacked_typed_dict_cls(func_0))

        def func_1(arg: int) -> None:
            """Return none when passing a positional argument."""

        self.assertIsNone(get_unpacked_typed_dict_cls(func_1))

        def func_2(*args: int) -> None:
            """Return none when passing unannotated variadic positional args."""

        self.assertIsNone(get_unpacked_typed_dict_cls(func_2))

        def func_3(**kwargs: Any) -> None:
            """Return none when passing unannotated variadic kwargs."""

        self.assertIsNone(get_unpacked_typed_dict_cls(func_3))

        class Kwargs(TypedDict):
            """A typed dictionary with some keyword arguments."""

            name: str

        def func_4(**kwargs: Unpack[Kwargs]) -> None:
            """Print the keyword arguments."""

        self.assertEqual(Kwargs, get_unpacked_typed_dict_cls(func_4))

    def test_get_docstrs(self) -> None:
        """Test getting the docstrings from typed dictionaries."""

        class KwargsMissingDocs(TypedDict):
            """A type dictionary with no docstrings."""

            name: str

        self.assertEqual({"name": TypePair(str, None)}, get_typeddict_docstrs(KwargsMissingDocs))

        class KwargsWithDocs(TypedDict):
            """A typed dictionary with docstrings."""

            name: Annotated[str, Doc("test docstring")]

        self.assertEqual(
            {"name": TypePair(str, "test docstring")},
            get_typeddict_docstrs(KwargsWithDocs),
        )

    def test_get_position(self) -> None:
        """Test getting the position to insert."""
        lines = _f("""\
            First line.

            :param hello: something
            :returns: this is the place

            something else.
        """)
        self.assertEqual((3, False), _get_position(lines))

        lines = _f("Single line.")
        self.assertEqual((1, True), _get_position(lines))

        lines = _f("""\
            First line.

            something else.
        """)
        self.assertEqual((1, True), _get_position(lines))

    def test_insert_docs_exists(self) -> None:
        """Test inserting when there are already some other docs."""
        lines = _f("""\
            First line.

            :param hello: something
            :returns: this is the place

            something else.
        """)

        _insert(lines, [":param more: something"])
        lines_updated = _f("""\
            First line.

            :param hello: something
            :param more: something
            :returns: this is the place

            something else.
        """)
        self.assertEqual(lines_updated, lines)

    def test_insert_one_liner(self) -> None:
        """Test inserting when there is only a one-liner with no prior parameter docs."""
        lines = _f("First line.")
        _insert(lines, [":param more: something"])
        lines_updated = _f("""\
            First line.

            :param more: something
        """)
        self.assertEqual(lines_updated, lines)

    def test_insert_no_docs(self) -> None:
        """Test inserting when there are no prior parameter docs."""
        lines = _f("""\
            First line.

            something else.
        """)
        _insert(lines, [":param more: something"])
        lines_updated = _f("""\
            First line.

            :param more: something

            something else.
        """)
        self.assertEqual(lines_updated, lines)


def _f(s: str) -> list[str]:
    return dedent(s).rstrip().splitlines()
