import subprocess

from micropy.project import checks


def test_vscode_ext_min_version(mock_checks, mocker):
    """Test VSCode Extension Template Checks"""
    assert checks.vscode_ext_min_version("ms-python.python")
    assert not checks.vscode_ext_min_version("ms-python.python", min_version="2019.9.34911")
    mock_subproc = mocker.patch.object(subprocess, "run")
    mock_subproc.side_effect = [Exception]
    assert checks.vscode_ext_min_version("ms-python.python")
