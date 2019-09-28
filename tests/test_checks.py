# -*- coding: utf-8 -*-

from micropy.project import checks


def test_vscode_ext_min_version(mock_checks):
    """Test VSCode Extension Template Checks"""
    assert checks.vscode_ext_min_version('ms-python.python')
    assert not checks.vscode_ext_min_version('ms-python.python',
                                             min_version="2019.9.34911")
