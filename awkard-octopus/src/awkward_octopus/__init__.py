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
