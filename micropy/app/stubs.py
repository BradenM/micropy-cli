from __future__ import annotations

import sys
import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Optional, Type

import micropy.exceptions as exc
import typer
from micropy.exceptions import PyDeviceError
from micropy.logger import Log
from micropy.main import MicroPy
from micropy.pyd import (
    DevicePath,
    MessageHandlers,
    MetaPyDeviceBackend,
    ProgressStreamConsumer,
    PyDevice,
)
from micropy.pyd.backend_rshell import RShellPyDeviceBackend
from micropy.pyd.backend_upydevice import UPyDeviceBackend
from micropy.stubs import source as stubs_source
from micropy.utils.stub import prepare_create_stubs
from stubber.codemod import board as stub_board
from stubber.codemod.modify_list import ListChangeSet

stubs_app = typer.Typer(name="stubs", rich_markup_mode="markdown", no_args_is_help=True)


@stubs_app.callback()
def stubs_callback():
    """Manage Micropy Stubs.

    \b
    Stub files are what enable linting,
    Intellisense, Autocompletion, and more.

    \b
    To achieve the best results, you can install
    stubs specific to your device/firmware using:

     -  *micropy stubs search* `STUB_NAME`

     -  *micropy stubs add* `STUB_NAME`



    For more info, please check micropy stubs add --help
    """
    pass


class CreateBackend(str, Enum):
    upydevice = ("upydevice", UPyDeviceBackend)
    rshell = ("rshell", RShellPyDeviceBackend)

    def __new__(cls, value: str, backend: Type[MetaPyDeviceBackend]):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.backend = backend
        return obj


def create_changeset(
    value: Optional[List[str]], *, replace: bool = False
) -> Optional[ListChangeSet]:
    if value is None:
        return value
    return ListChangeSet.from_strings(add=value, replace=replace)


@stubs_app.command(name="create")
def stubs_create(
    ctx: typer.Context,
    port: str = typer.Argument(..., help="Serial port used to connect to device"),
    backend: CreateBackend = typer.Option(CreateBackend.upydevice, help="PyDevice backend to use."),
    variant: stub_board.CreateStubsVariant = typer.Option(
        stub_board.CreateStubsVariant.BASE,
        "-v",
        "--variant",
        help="Create Stubs variant.",
        rich_help_panel="Stubs",
    ),
    module: Optional[List[str]] = typer.Option(
        None,
        "-m",
        "--module",
        help="Modules to look for and stub. This flag can be used multiple times.",
        rich_help_panel="Stubs",
    ),
    module_defaults: bool = typer.Option(
        True, help="Include createstubs.py default modules.", rich_help_panel="Stubs"
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "-e",
        "--exclude",
        help="Modules to exclude from stubber. This flag can be used multiple times.",
        rich_help_panel="Stubs",
    ),
    exclude_defaults: bool = typer.Option(
        True,
        help="Include createstubs.py default module excludes. This flag can be used multiple times.",
        rich_help_panel="Stubs",
    ),
    compile: bool = typer.Option(
        True,
        "-c",
        "--compile",
        help="Cross compile to .mpy via mpy-cross.",
        rich_help_panel="Stubs",
    ),
):
    """Create stubs from micropython-enabled devices.

    Utilize Josverl's [micropython-stubber](https://github.com/josverl/micropython-stubber/)
    to generate stubs from your own micropython-enabled device.

    \n
    **Create stubs with defaults**:\n
     - `micropy stubs create /dev/ttyUSB0`

    \n
    **Specify additional modules**:\n
     - `micropy stubs create -m custom_module -m other_module /dev/ttyUSB0`\n
     - _Only given modules_: `micropy stubs create -m custom_module --no-module-defaults /dev/ttyUSB0`

    \n
    **Exclude additional modules**:\n
     - `micropy stubs create -e custom_module -e other_module /dev/ttyUSB0`\n
     - _Only exclude given modules_: `micropy stubs create -e custom_module --no-module-defaults /dev/ttyUSB0`

    \n
    **Create Stubs Variants**:\n
     - **mem**: Optimized for low memory devices._\n
     - **db**: Persist stub progress across reboots.\n
     - **lvgl**: Additional support for LVGL devices.\n

    """
    mp: MicroPy = ctx.ensure_object(MicroPy)
    log = mp.log
    log.title(f"Connecting to Pyboard @ $[{port}]")
    pyb_log = Log.add_logger("Pyboard", "bright_white")

    def _get_desc(name: str, cfg: dict):
        desc = f"{pyb_log.get_service()} {name}"
        return name, cfg | dict(desc=desc)

    message_handler = MessageHandlers(
        on_message=lambda x: isinstance(x, str) and pyb_log.info(x.strip())
    )
    try:
        pyb = PyDevice(
            port,
            auto_connect=True,
            stream_consumer=ProgressStreamConsumer(on_description=_get_desc),
            message_consumer=message_handler,
            backend=backend.backend,
        )
    except (SystemExit, PyDeviceError):
        log.error(f"Failed to connect, are you sure $[{port}] is correct?")
        return None

    log.success("Connected!")
    if module or exclude:
        log.title("Preparing createstubs for:")
        log.info(f"Modules: {', '.join(module or [])}")
        log.info(f"Exclude: {', '.join(exclude or [])}")
    create_stubs = prepare_create_stubs(
        variant=variant,
        modules_set=create_changeset(module, replace=not module_defaults),
        exclude_set=create_changeset(exclude, replace=not exclude_defaults),
        compile=compile,
    )
    dev_path = DevicePath("createstubs.mpy") if compile else DevicePath("createstubs.py")
    log.info("Executing stubber on pyboard...")
    try:
        pyb.run_script(create_stubs, DevicePath(dev_path))
    except Exception as e:
        # TODO: Handle more usage cases
        log.error(f"Failed to execute script: {str(e)}", exception=e)
        raise
    log.success("Done!")
    log.info("Copying stubs...")
    with tempfile.TemporaryDirectory() as tmpdir:
        pyb.copy_from(
            DevicePath("/stubs"),
            tmpdir,
            verify_integrity=True,
            # exclude due to ps1 var possibly different.
            exclude_integrity={"sys.py", "usys.py"},
        )
        out_dir = Path(tmpdir)
        stub_path = next(out_dir.iterdir())
        log.info(f"Copied Stubs: $[{stub_path.name}]")
        stub_path = mp.stubs.from_stubber(stub_path, out_dir)
        stub = mp.stubs.add(str(stub_path))
    pyb.remove(dev_path)
    pyb.disconnect()
    log.success(f"Added {stub.name} to stubs!")
    return stub


@stubs_app.command(name="add")
def stubs_add(ctx: typer.Context, stub_name: str, force: bool = False):
    """Add Stubs from package or path.

    \b
    In general, stub package names follow this schema:
        <device>-<firmware>-<version>

    \b
    For example:
        esp32-micropython-1.11.0

    \b
    You can search premade stub packages using:
        micropy stubs search <QUERY>

    Checkout the docs on Github for more info.

    """
    mpy: MicroPy = ctx.find_object(MicroPy)
    proj = mpy.project
    mpy.log.title(f"Adding $[{stub_name}] to stubs")
    locator = stubs_source.StubSource(
        [stubs_source.RepoStubLocator(mpy.repo), stubs_source.StubInfoSpecLocator()]
    )
    with locator.ready(stub_name) as stub:
        stub_name = stub
    try:
        stub = mpy.stubs.add(stub_name, force=force)
    except exc.StubNotFound:
        mpy.log.error(f"$[{stub_name}] could not be found!")
        sys.exit(1)
    except exc.StubError:
        mpy.log.error(f"$[{stub_name}] is not a valid stub!")
        sys.exit(1)
    else:
        mpy.log.success(f"{stub.name} added!")
        if proj.exists:
            mpy.log.title(f"Adding $[{stub.name}] to $[{proj.name}]")
            proj.add_stub(stub)


@stubs_app.command(name="search")
def stubs_search(ctx: typer.Context, query: str, show_outdated: bool = False):
    """Search available stubs."""
    mpy: MicroPy = ctx.find_object(MicroPy)
    installed_stubs = map(str, mpy.stubs._loaded | mpy.stubs._firmware)
    results = [
        (r, r.name in installed_stubs)
        for r in mpy.repo.search(query, include_versions=show_outdated)
    ]
    results = sorted(results, key=lambda pkg: pkg[0].name)
    if not any(results):
        mpy.log.warn(f"No results found for: $[{query}].")
        sys.exit(0)
    mpy.log.title(f"Results for $[{query}]:")
    max_name = max(len(n[0].repo_name) for n in results)
    for pkg, installed in results:
        pad = max_name - len(pkg.repo_name) + 2
        pad = pad if (pad % 2 == 0) else pad + 1
        spacer = "{:>{pad}}".format("::", pad=pad)
        repo_logger = Log.add_logger(f"{pkg.repo_name} {spacer}", "bright_white")
        name = "{:>{pad}}".format(f"{pkg.name} ($w[{pkg.version}])", pad=pad)
        name = f"{name} $B[(Installed)]" if installed else name
        repo_logger.info(name)


@stubs_app.command(name="list")
def stubs_list(ctx: typer.Context):
    """List installed stubs."""
    mpy: MicroPy = ctx.find_object(MicroPy)

    def print_stubs(stub_list):
        for firm, stubs in stub_list:
            if stubs:
                title = str(firm).capitalize()
                mpy.log.title(f"$[{title}]:")
                for stub in stubs:
                    mpy.log.info(str(stub))

    mpy.log.title("Installed Stubs:")
    mpy.log.info(f"Total: {len(mpy.stubs)}")
    print_stubs(mpy.stubs.iter_by_firmware())
    mpy.verbose = False
    proj = mpy.project
    if proj.exists:
        mpy.log.title(f"Stubs used in {proj.name}:")
        mpy.log.info(f"Total: {len(proj.stubs)}")
        stubs = mpy.stubs.iter_by_firmware(stubs=proj.stubs)
        print_stubs(stubs)
