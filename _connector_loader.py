from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

def load_connector(relative_path: str, module_name: str):
    root = Path(__file__).resolve().parent
    target = root / relative_path
    spec = spec_from_file_location(module_name, target)
    mod = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod
