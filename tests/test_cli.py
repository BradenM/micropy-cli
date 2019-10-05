# -*- coding: utf-8 -*-

from pathlib import Path

import click
import pytest
from click.testing import CliRunner

import micropy
from micropy import cli


@pytest.fixture
def runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def mock_mpy(mocker):
    mock_mp = mocker.patch("micropy.main.MicroPy")
    mocker.patch.object(click.Context, "find_object").return_value = mock_mp
    return mock_mp


def test_cli_micropy(runner, mocker):
    """should execute"""
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    expected = ("CLI Application for creating/managing"
                " Micropython Projects.")
    assert expected in result.output
    # should alert about update
    mocker.patch.object(
        cli.utils, 'is_update_available', return_value='1.0.0')
    log_spy = mocker.spy(cli, 'Log')
    runner.invoke(cli.cli, ["stubs"])
    log_spy.get_logger.assert_called_once_with("MicroPy")


def test_stub_list(mock_mpy, mocker, runner):
    """should list stubs"""
    mock_mpy.log.title = print
    mock_mpy.log.info = print
    m_data = [("FakeFirmware", ["dev1", "dev2"])]
    mock_project = mocker.patch.object(cli, "Project")
    mock_mpy.resolve_project.return_value = mock_project.return_value
    mock_mpy.project.name = "Test Project"
    mock_mpy.project.stubs = m_data
    mock_mpy.STUBS.iter_by_firmware.return_value = m_data
    result = runner.invoke(cli.list)
    assert result.exit_code == 0
    for s in ["dev1", "dev2"]:
        assert s in result.output


def test_stub_create(runner, mock_mpy):
    """should call create_stubs"""
    result = runner.invoke(cli.create, ["/dev/PORT"], obj=mock_mpy)
    mock_mpy.create_stubs.assert_called_once_with("/dev/PORT", verbose=False)
    assert result.exit_code == 0


def test_cli_init(mocker, mock_mpy, shared_datadir, mock_prompt, runner):
    """should create project"""
    mock_project = mocker.patch.object(cli, "Project")
    result = runner.invoke(cli.init, ["TestProject"])
    assert result.exit_code == 1
    mock_mpy.STUBS = ["stub"]
    result = runner.invoke(cli.init, ["TestProject", "-t", "vscode"])
    mock_project.assert_called_once_with(
        "TestProject", stubs=["stub"], stub_manager=mock_mpy.STUBS,
        name=None, templates=('vscode', ))
    mock_project.return_value.create.assert_called_once()
    assert result.exit_code == 0
    ptext_mock = mocker.patch.object(cli.prompt, 'text').return_value
    ptext_mock.ask.return_value = "ProjectName"
    result = runner.invoke(cli.init, ["-t", "vscode"])
    mock_project.assert_called_with(
        Path.cwd(), stubs=["stub"], stub_manager=mock_mpy.STUBS,
        name="ProjectName", templates=('vscode', ))


def test_cli_stubs_add(mocker, mock_mpy, shared_datadir,
                       runner, tmp_path, mock_checks):
    """should add stub"""
    test_stub = shared_datadir / 'esp8266_test_stub'
    test_invalid_stub = shared_datadir / 'esp8266_invalid_stub'

    mock_proj = mocker.patch.object(cli, 'Project').return_value
    mock_proj.exists.return_value = True
    mock_mpy.project = mock_proj
    mock_mpy.STUBS.add.side_effect = [micropy.exceptions.StubError,
                                      micropy.exceptions.StubNotFound,
                                      mocker.MagicMock()]

    mocker.spy(cli.sys, 'exit')

    result = runner.invoke(cli.add, [str(test_invalid_stub.resolve())])
    assert cli.sys.exit.called_with(1)
    # assert err_spy.call_count ==
    assert result.exit_code == 1

    result = runner.invoke(cli.add, ["not-real-stub"])
    assert cli.sys.exit.called_with(1)
    # assert err_spy.call_count ==
    assert result.exit_code == 1

    result = runner.invoke(cli.add, [str(test_stub.resolve())])
    assert mock_proj.add_stub.call_count == 1
    # assert err_spy.call_count ==
    assert result.exit_code == 0


def test_cli_stubs_search(mock_mpy, runner):
    """should search stubs"""
    mock_mpy.STUBS.search_remote.return_value = [
        ("esp8266-micropython-1.11.0", True, ),
        ("esp8266-micropython-1.10.0", False, )
    ]
    result = runner.invoke(cli.search, ["esp8266"])
    assert result.exit_code == 0


def test_cli_install(mocker, runner, mock_mpy):
    """should install packages"""
    mock_project = mocker.patch.object(cli, 'Project')
    mock_proj = mock_project.return_value
    mock_mpy.project = mock_proj
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
    mock_mpy.project = None
    result = runner.invoke(cli.install, ["package"])
    assert result.exit_code == 1
