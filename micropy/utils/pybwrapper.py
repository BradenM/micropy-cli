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

    def __init__(self, port, connect=True, verbose=False):
        self.connected = False
        self.port = port
        self.rsh = rsh
        self.rsh.ASCII_XFER = False
        self.rsh.QUIET = not verbose
        self.log = Log.add_logger('Pyboard', 'bright_white')
        self._outline = []
        self.format_output = None
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

    def _output(self, data):
        """Yields everything up to a newline

        Args:
            data (str): Anything to yield before newline
        """
        if data == "\n":
            line = "".join(self._outline)
            self._outline = []
            yield line
        self._outline.append(data)

    def _consumer(self, char):
        """Pyboard data consumer

        When a full line of output is detected,
        it is formatted then logged to stdout
        and log file.

        Args:
            char (byte): Byte from PyBoard

        Returns:
            str: Converted char
        """
        char = char.decode('utf-8')
        line = next(self._output(char), None)
        if line:
            if self.format_output:
                line = self.format_output(line)
            self.log.info(line)
        return char

    def _exec(self, command):
        """Execute bytes on pyboard"""
        ret, ret_err = self.pyboard.exec_raw(
            command, data_consumer=self._consumer)
        if ret_err:
            raise PyboardError('exception', ret, ret_err)
        return ret

    def run(self, file, format_output=None):
        """Execute a local script on the pyboard

        Args:
            file (str): path to file or string to run
            format_output (callable, optional): Callback to format output.
                Defaults to None. If none, uses print.
        """
        self.format_output = format_output
        try:
            with file.open('rb') as f:
                pyfile = f.read()
        except AttributeError:
            pyfile = file.encode('utf-8')
        with self.repl():
            try:
                out_bytes = self._exec(pyfile)
            except PyboardError as e:
                self.log.debug(f"Failed to run script on pyboard: {str(e)}")
                raise Exception(str(e))
            out = out_bytes.decode('utf-8')
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
