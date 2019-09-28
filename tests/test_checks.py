# -*- coding: utf-8 -*-

from micropy.project import checks

mock_vscode_exts = [
    'mock.ext@0.0.0',
    # meets req
    'ms-python.python@2019.9.34474'
]


def test_vscode_ext_min_version(mocker):
    m_run = mocker.patch.object(checks, 'subproc').run.return_value
    type(m_run).stdout = mocker.PropertyMock(
        return_value="\n".join(mock_vscode_exts))
    assert checks.vscode_ext_min_version('ms-python.python')
    assert not checks.vscode_ext_min_version('ms-python.python',
                                             min_version="2019.9.34911")
