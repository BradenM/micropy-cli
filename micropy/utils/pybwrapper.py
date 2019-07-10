# -*- coding: utf-8 -*-

"""
micropy.utils.pybwrapper
~~~~~~~~~~~~~~

This module contains utility functionality related
to communication with micropython devices
"""

from contextlib import contextmanager
from pathlib import Path

import rshell.main as rsh
from rshell.pyboard import PyboardError

from micropy.logger import Log


class PyboardWrapper:
    """Wrapper for rshell/pyboard

    Exposes the basic run/copy functionality
    Micropy needs

    Args:
        port (str): Port of Pyboard

    Kwargs:
        connect (bool): Connect on init. Defaults to True
    """

    def __init__(self, port, connect=True):
        self.connected = False
        self.port = port
        self.rsh = rsh
        self.rsh.ASCII_XFER = False
        self.log = Log.add_logger('PyboardWrapper')
        if connect:
            return self.connect()

    def _pyb_path(self, path):
        """returns path relative to pyboard

        Args:
            path (str): path to resolve
        """
        _path = path
        if path[0] == '/':
            _path = path[1:]
        pyb_path = f"{self.pyb_root}{_path}"
        return pyb_path

    @contextmanager
    def repl(self):
        """Pyboard raw repl context manager"""
        self.pyboard.enter_raw_repl()
        try:
            yield self.pyboard
        finally:
            self.pyboard.exit_raw_repl()

    def connect(self):
        """connect to pyboard"""
        self.log.debug(f"connecting to pydevice @ {self.port}")
        try:
            self.rsh.connect(self.port)
        except SystemExit as e:
            self.log.debug(f"failed to connect: {str(e)}")
            raise e
        else:
            self.log.debug("connected!")
            self.connected = True

    @property
    def pyboard(self):
        """rshell pyboard instance"""
        if self.connected:
            dev = rsh.find_serial_device_by_port(self.port)
            return getattr(dev, "pyb", None)

    @property
    def pyb_root(self):
        """pyboard root dirname"""
        if self.connected:
            dev = rsh.find_serial_device_by_port(self.port)
            return getattr(dev, 'name_path', '/pyboard/')

    def copy_file(self, source, dest=None):
        """Copies file to pyboard

        Args:
            source (str): path to file
            dest (str, optional): dest on pyboard. Defaults to None.
                If None, file is copied to pyboard root.

        Returns:
            str: path to dest on pyboard
        """
        src_path = Path(source).resolve()
        _dest = dest or src_path.name
        dest = self._pyb_path(_dest)
        self.rsh.cp(str(src_path), dest)
        return dest

    def run(self, path):
        """Execute a local script on the pyboard

        Args:
            path (str): path to file
        """
        # TODO: Better Exception handling
        file_path = Path(str(path)).resolve()
        with self.repl():
            try:
                out_bytes = self.pyboard.execfile(file_path)
            except PyboardError as e:
                self.log.debug(f"Failed to run script on pyboard: {str(e)}")
                raise Exception(str(e))
            out = str(out_bytes, 'utf-8')
            return out

    def list_dir(self, path):
        """List directory on pyboard

        Args:
            path (str): path to directory
        """
        dir_path = self._pyb_path(path)
        tree = self.rsh.auto(rsh.listdir, dir_path)
        return tree

    def copy_dir(self, path, dest, rsync={}):
        """Copy directory from pyboard to machine

        Args:
            path (str): path to directory
            dest (str): destination to copy to
            rsync (dict, optional): additonal args to pass to rsync call.
                Defaults to {}
        """
        dir_path = self._pyb_path(path)
        dest_path = Path(str(dest))
        rsync_args = {
            "recursed": True,
            "mirror": False,
            "dry_run": False,
            "print_func": lambda * args: None,
            "sync_hidden": False
        }
        rsync_args.update(rsync)
        self.rsh.rsync(dir_path, str(dest_path), **rsync_args)
        return dest_path
