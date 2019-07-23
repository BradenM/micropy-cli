# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
from click.testing import CliRunner

from micropy import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    return runner


def test_cli_micropy(runner):
    """should execute"""
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    expected = ("CLI Application for creating/managing"
                " Micropython Projects.")
    assert expected in result.output


def test_stub_list(mock_mp_stubs, mocker, runner):
    """should list stubs"""
    mocker.patch.object(cli, "MicroPy").return_value = mock_mp_stubs
    mock_project = mocker.patch.object(cli, "Project")
    mock_project.resolve.return_value = mock_project.return_value
    mock_proj = mock_project.return_value
    mock_proj.name = "Test Project"
    mock_proj.stubs = list(mock_mp_stubs.STUBS)[:2]
    result = runner.invoke(cli.list)
    stub_names = [str(s) for s in mock_mp_stubs.STUBS]
    assert result.exit_code == 0
    for s in stub_names:
        assert s in result.output


def test_stub_create(mocker, runner):
    """should call create_stubs"""
    mock_mp = mocker.patch.object(cli, "MicroPy").return_value
    result = runner.invoke(cli.create, ["/dev/PORT"])
    mock_mp.create_stubs.assert_called_once_with("/dev/PORT")
    assert result.exit_code == 0


def test_cli_init(mocker, mock_micropy, shared_datadir, mock_prompt, runner):
    """should create project"""
    mocker.patch.object(cli, "MicroPy").return_value = mock_micropy
    mock_project = mocker.patch.object(cli, "Project")
    result = runner.invoke(cli.init, ["TestProject"])
    assert result.exit_code == 1
    mock_micropy.STUBS = ["stub"]
    result = runner.invoke(cli.init, ["TestProject", "-t", "vscode"])
    mock_project.assert_called_once_with(
        "TestProject", stubs=["stub"], stub_manager=mock_micropy.STUBS,
        name=None, templates=('vscode', ))
    mock_project.return_value.create.assert_called_once()
    assert result.exit_code == 0
    ptext_mock = mocker.patch.object(cli.prompt, 'text').return_value
    ptext_mock.ask.return_value = "ProjectName"
    result = runner.invoke(cli.init, ["-t", "vscode"])
    mock_project.assert_called_with(
        Path.cwd(), stubs=["stub"], stub_manager=mock_micropy.STUBS,
        name="ProjectName", templates=('vscode', ))


def test_cli_stubs_add(mocker, mock_micropy, shared_datadir,
                       runner, tmp_path):
    """should add stub"""
    test_stub = shared_datadir / 'esp8266_test_stub'
    test_invalid_stub = shared_datadir / 'esp8266_invalid_stub'
    mocker.patch.object(cli, "MicroPy").return_value = mock_micropy
    mock_micropy.STUBS.add((shared_datadir / 'fware_test_stub'))

    mock_proj = mocker.patch.object(cli, 'Project').return_value
    mock_proj.exists.return_value = True

    mocker.spy(cli.sys, 'exit')
    err_spy = mocker.spy(mock_micropy.log, 'error')
    result = runner.invoke(cli.add, [str(test_invalid_stub.resolve())])
    assert cli.sys.exit.called_with(1)
    assert err_spy.call_count == 1
    assert result.exit_code == 1

    result = runner.invoke(cli.add, ["not-real-stub"])
    assert cli.sys.exit.called_with(1)
    assert err_spy.call_count == 2
    assert result.exit_code == 1

    result = runner.invoke(cli.add, [str(test_stub.resolve())])
    assert mock_proj.add_stub.call_count == 1
    assert err_spy.call_count == 2
    assert result.exit_code == 0


def test_cli_stubs_search(mock_mp_stubs, mocker, runner):
    """should search stubs"""
    mp_mock = mocker.patch.object(cli, "MicroPy").return_value
    mp_mock.STUBS.search_remote.return_value = [
        ("esp8266-micropython-1.11.0", True, ),
        ("esp8266-micropython-1.10.0", False, )
    ]
    result = runner.invoke(cli.search, ["esp8266"])
    assert result.exit_code == 0


def test_cli_install(mocker, runner):
    """should install packages"""
    mock_project = mocker.patch.object(cli, 'Project')
    mock_proj = mock_project.return_value
    mock_project.resolve.return_value = mock_proj
    # Test Normal
    result = runner.invoke(cli.install, ["package", "--dev"])
    assert result.exit_code == 0
    mock_proj.add_package.assert_called_once_with("package", dev=True)
    # Test from requirements
    result = runner.invoke(cli.install, "")
    assert result.exit_code == 0
    mock_proj.add_from_requirements.return_value = None
    result = runner.invoke(cli.install, "")
    assert result.exit_code == 1
    # Test no project found
    mock_project.resolve.return_value = None
    result = runner.invoke(cli.install, ["package"])
    assert result.exit_code == 1
