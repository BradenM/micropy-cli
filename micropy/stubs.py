# -*- coding: utf-8 -*-

from shutil import copytree


class Stub:
    """Handles Stub Directory

    :param str path: path to stub

    """

    def __init__(self, path, *args, **kwargs):
        self.path = path.absolute()
        self.name = self.path.name

    @classmethod
    def create_from_path(cls, stub_dir, path):
        """Creates Stub instance from path

        :param PosixPath stub_dir: path to stubs
        :param str path: path to new stub

        """
        out = stub_dir / path.name
        copytree(path, out)
        return cls(out)
