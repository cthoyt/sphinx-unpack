from __future__ import annotations
from typing import Annotated, get_type_hints
import inspect
from sphinx.application import Sphinx
from typing import get_args, get_origin, Any
from typing_extensions import Doc


def extract_doc_from_annotated(annotation: Any) -> tuple[str, str | None]:
    """Extract the type and Doc string from an Annotated type."""
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        typ = args[0]
        doc = next((a.__doc__ if isinstance(a, Doc) else str(a)
                    for a in args[1:]
                    if isinstance(a, Doc)), None)
        return str(typ), doc
    return str(annotation), None


def process_docstring(app, what, name, obj, options, lines):
    if what != "function":
        return

    sig = inspect.signature(obj)
    type_hints = get_type_hints(obj, include_extras=True)

    doc_lines = []

    for param_name, param in sig.parameters.items():
        ann = type_hints.get(param_name, param.annotation)
        typ_str, doc = extract_doc_from_annotated(ann)
        if doc:
            doc_lines.append(f":param {param_name}: {doc}")
            doc_lines.append(f":type {param_name}: {typ_str}")

    # Handle return
    return_ann = type_hints.get("return", sig.return_annotation)
    typ_str, doc = extract_doc_from_annotated(return_ann)
    if doc:
        doc_lines.append(f":return: {doc}")
        doc_lines.append(f":rtype: {typ_str}")

    lines += doc_lines


def setup(app: Sphinx):
    app.connect("autodoc-process-docstring", process_docstring)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
