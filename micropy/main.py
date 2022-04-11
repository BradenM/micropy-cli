# -*- coding: utf-8 -*-

"""Main Module."""

import tempfile
from pathlib import Path

from micropy import data, utils
from micropy.exceptions import PyDeviceError
from micropy.lib.stubber import process as stubber
from micropy.logger import Log
from micropy.project import Project, modules
from micropy.pyd import DevicePath, MessageHandlers, ProgressStreamConsumer, PyDevice
from micropy.stubs import StubManager, source


class MicroPy:
    """Handles App State Management."""

    RUN_CHECKS = True

    def __init__(self):
        self.log = Log.get_logger("MicroPy")
        self.verbose = True
        self.log.debug("MicroPy Loaded")
        if not data.STUB_DIR.exists():
            self.setup()

    def setup(self):
        """Creates necessary directories for micropy."""
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {data.FILES}")
        data.FILES.mkdir(exist_ok=True)
        data.STUB_DIR.mkdir()

    @utils.lazy_property
    def stubs(self):
        """Primary Stub Manager for MicroPy.

        Returns:
            StubManager: StubManager Instance

        """
        repo_list = data.REPO_SOURCES.read_text()
        repos = source.StubRepo.from_json(repo_list)
        return StubManager(resource=data.STUB_DIR, repos=repos)

    @utils.lazy_property
    def project(self):
        """Current active project if available.

        Returns:
            Project: Instance of Current Project

        """
        proj = self.resolve_project(".", verbose=self.verbose)
        return proj

    def resolve_project(self, path, verbose=True):
        """Returns project from path if it exists.

        Args:
            path (str): Path to test
            verbose (bool): Log to stdout. Defaults to True.

        Returns:
            Project if it exists

        """
        path = Path(path).absolute()
        proj = Project(path)
        proj.add(modules.StubsModule, self.stubs)
        proj.add(modules.PackagesModule, "requirements.txt")
        proj.add(modules.DevPackagesModule, "dev-requirements.txt")
        proj.add(modules.TemplatesModule, run_checks=self.RUN_CHECKS)
        if proj.exists:
            if verbose:
                self.log.title(f"Loading Project")
            proj.load()
            if verbose:
                self.log.success("Ready!")
            return proj
        return proj

    def create_stubs(self, port, verbose=False):
        """Create and add stubs from Pyboard.

        Todo:
            Extract and cleanup this mess.

        Args:
            port (str): Port of Pyboard

        Returns:
            Stub: generated stub

        """
        self.log.title(f"Connecting to Pyboard @ $[{port}]")
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
            )
        except (SystemExit, PyDeviceError):
            self.log.error(f"Failed to connect, are you sure $[{port}] is correct?")
            return None
        self.log.success("Connected!")
        script = stubber.minify_script(stubber.source_script)
        self.log.info("Executing stubber on pyboard...")
        try:
            pyb.run_script(script, DevicePath("createstubs.py"))
        except Exception as e:
            # TODO: Handle more usage cases
            self.log.error(f"Failed to execute script: {str(e)}", exception=e)
            raise
        self.log.success("Done!")
        self.log.info("Copying stubs...")
        with tempfile.TemporaryDirectory() as tmpdir:
            pyb.copy_from(DevicePath("/stubs"), tmpdir)
            out_dir = Path(tmpdir)
            stub_path = next(out_dir.iterdir())
            self.log.info(f"Copied Stubs: $[{stub_path.name}]")
            stub_path = self.stubs.from_stubber(stub_path, out_dir)
            stub = self.stubs.add(stub_path)
        pyb.disconnect()
        self.log.success(f"Added {stub.name} to stubs!")
        return stub
