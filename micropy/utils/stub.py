"""Micropy stub utils."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import micropy.data


def import_source_code(module_name: str, path: Path) -> ModuleType:
    """Dynamically create and load module from python source code.

    Args:
        module_name: name of new module to create.
        path: path to source code.

    Returns:
        Dynamically created module.

    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def import_stubber() -> ModuleType:
    """Dynamically import stubber.

    We do this because `micropython-stubs` is not a python package, so
    we can't import from it as you would normally.

    """
    vers_path = micropy.data.STUBBER / "src" / "version.py"
    src_path = micropy.data.STUBBER / "src" / "utils.py"
    # stubber utils expects an ambiguous 'version' import
    import_source_code("version", vers_path)
    mod = import_source_code("stubber.utils", src_path)
    return mod


def generate_stub(path, log_func=None):
    """Create Stub from local .py file.

    Args:
        path (str): Path to file
        log_func (func, optional): Callback function for logging.
            Defaults to None.

    Returns:
        tuple: Tuple of file path and generated stub path.

    """
    stubgen = import_stubber()
    # Monkeypatch print to prevent or wrap output
    logfn = log_func or (lambda *a: None)
    stubgen.print = logfn
    stubgen.stubgen.print = logfn
    file_path = Path(path).absolute()
    stubbed_path = file_path.with_suffix(".pyi")
    stubgen.generate_pyi_from_file(file_path)  # noqa
    # ensure stubs reside next to their source.
    result = next((file_path.parent.rglob(f"**/{stubbed_path.name}")), stubbed_path)
    if result.exists():
        result.replace(stubbed_path)
    if not any(result.parent.iterdir()):
        result.parent.rmdir()
    files = (file_path, stubbed_path)
    return files
