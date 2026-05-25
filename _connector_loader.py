"""Utilities for loading connector modules by filesystem path."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_connector(relative_path: str, module_name: str) -> ModuleType:
    """Load a connector implementation module from a repository-relative path."""
    root = Path(__file__).resolve().parent
    target = (root / relative_path).resolve()

    if not target.exists() or not target.is_file():
        raise ImportError(f"Cannot load connector module '{module_name}' from '{target}'")

    spec = spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load connector module '{module_name}' from '{target}'")

    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError as exc:
        raise ImportError(
            f"Cannot load connector module '{module_name}' from '{target}'"
        ) from exc

    return module
