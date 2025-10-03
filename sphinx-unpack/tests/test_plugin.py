import unittest

from sphinx_unpack import get_unpacked_typed_dict_cls, get_typeddict_docstrs, TypePair
from typing import Annotated, Unpack, Any
from typing_extensions import Doc, TypedDict


class TestPlugin(unittest.TestCase):
    """Tests for the plugin."""

    def test_get_unpacked(self) -> None:
        """Test getting the unpacked type dict."""

        def func_0():
            pass

        self.assertIsNone(get_unpacked_typed_dict_cls(func_0))

        def func_1(arg: int):
            pass

        self.assertIsNone(get_unpacked_typed_dict_cls(func_1))

        def func_2(*args: int):
            pass

        self.assertIsNone(get_unpacked_typed_dict_cls(func_2))

        def func_3(**kwargs: Any):
            pass

        self.assertIsNone(get_unpacked_typed_dict_cls(func_3))

        class Kwargs(TypedDict):
            name: str

        def func_4(**kwargs: Unpack[Kwargs]) -> None:
            """Print the keyword arguments."""
            print(kwargs)

        self.assertEqual(Kwargs, get_unpacked_typed_dict_cls(func_4))

    def test_next_step(self) -> None:
        class KwargsMissingDocs(TypedDict):
            name: str

        self.assertEqual(
            {"name": TypePair(str, None)}, get_typeddict_docstrs(KwargsMissingDocs)
        )

        class KwargsWithDocs(TypedDict):
            name: Annotated[str, Doc("test docstring")]

        self.assertEqual(
            {"name": TypePair(str, "test docstring")},
            get_typeddict_docstrs(KwargsWithDocs),
        )
