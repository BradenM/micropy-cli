"""Micropy stub utils."""
from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional

import libcst as cst
import libcst.codemod as codemod
import micropy.data
from stubber import minify
from stubber.codemod import board as stub_board
from stubber.utils import stubmaker


def locate_create_stubs() -> Path:
    """Locate createstubs.py"""
    return Path(importlib.util.find_spec("stubber.board.createstubs").origin)


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
    if stubmaker is None:
        raise ImportError("micropython-stubber requires a python version of >= 3.8")
    stubmaker.STUBGEN_OPT.quiet = True
    file_path = Path(path).absolute()
    stubbed_path = file_path.with_suffix(".pyi")
    stubmaker.generate_pyi_from_file(file_path)
    # ensure stubs reside next to their source.
    result = next((file_path.parent.rglob(f"**/{stubbed_path.name}")), stubbed_path)
    if result.exists():
        result.replace(stubbed_path)
    if not any(result.parent.iterdir()):
        result.parent.rmdir()
    files = (file_path, stubbed_path)
    return files


def prepare_create_stubs(
    *,
    variant: Optional[stub_board.CreateStubsVariant] = None,
    modules_set: Optional[stub_board.ListChangeSet] = None,
    problem_set: Optional[stub_board.ListChangeSet] = None,
    exclude_set: Optional[stub_board.ListChangeSet] = None,
    compile: bool = False,
) -> io.StringIO | io.BytesIO:
    if stub_board is None:
        raise ImportError("micropython-stubber requires a python version of >= 3.8")
    variant = variant or stub_board.CreateStubsVariant.BASE
    ctx = codemod.CodemodContext()
    code_mod = stub_board.CreateStubsCodemod(
        ctx, variant=variant, modules=modules_set, problematic=problem_set, excluded=exclude_set
    )
    create_stubs = cst.parse_module(locate_create_stubs().read_text())
    result = code_mod.transform_module_impl(create_stubs).code
    result_io = io.StringIO(result)
    minified_io = io.StringIO()
    minify.minify(result_io, minified_io, keep_report=True, diff=False)
    minified_io.seek(0)
    # TODO: compile w/ mpy-cross
    if compile:
        compiled_io = io.BytesIO()
        minify.cross_compile(minified_io, compiled_io)
        compiled_io.seek(0)
        return compiled_io
    return minified_io
