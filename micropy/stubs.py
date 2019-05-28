# -*- coding: utf-8 -*-

from shutil import copytree
import re

class Stub:
    """Handles Stub Directory

    :param str path: path to stub

    """

    def __init__(self, path, *args, **kwargs):
        self.path = path.absolute()
        self.name = self.path.name

    @staticmethod
    def clean_stub_name(stub_path):
        """Cleans stub names"""
        name = stub_path.name
        cleaned = re.sub(r'\([^)]*\)', '', name)
        return stub_path.with_name(cleaned)                               

    @classmethod
    def create_from_path(cls, stub_dir, path):
        """Creates Stub instance from path

        :param PosixPath stub_dir: path to stubs
        :param str path: path to new stub

        """
        stub_path = Stub.clean_stub_name(path)
        out = stub_dir / stub_path.name
        copytree(path, out)
        return cls(out)
