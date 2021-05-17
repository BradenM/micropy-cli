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
    return spec.loader.load_module(module_name)


def import_stubber() -> ModuleType:
    """Dynamically import stubber.

    We do this because `micropython-stubs` is not a python package, so
    we can't import from it as you would normally.

    """
    src_path = micropy.data.STUBBER / "src" / "make_stub_files.py"
    return import_source_code("stubber", src_path)


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
    mod_path = Path(stubgen.__file__).parent
    # Monkeypatch print to prevent or wrap output
    stubgen.print = lambda *args: None
    if log_func:
        stubgen.print = log_func
    cfg_path = (mod_path / "make_stub_files.cfg").absolute()
    ctrl = stubgen.StandAloneMakeStubFile()
    ctrl.update_flag = True
    ctrl.config_fn = str(cfg_path)
    file_path = Path(path).absolute()
    stubbed_path = file_path.with_suffix(".pyi")
    ctrl.files = [file_path]
    ctrl.silent = True
    ctrl.scan_options()
    ctrl.run()
    files = (file_path, stubbed_path)
    return files
