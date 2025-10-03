from typing import Annotated
from typing_extensions import Doc

__all__ = [
    "greet",
]


def greet(
    name: Annotated[str, Doc("The name of the person to greet")]
) -> Annotated[str, Doc("A greeting message")]:
    """Return a greeting."""
    return f"Hello, {name}!"
