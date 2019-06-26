# -*- coding: utf-8 -*-

import pytest
from click.testing import CliRunner

from micropy import cli, exceptions


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


def test_stub_list(mock_micropy, runner):
    """should list stubs"""
    result = runner.invoke(cli.list)
    stub_names = [str(s) for s in mock_micropy.STUBS]
    assert result.exit_code == 0
    for s in stub_names:
        assert s in result.output


def test_stub_create(mocker, runner):
    """should call create_stubs"""
    mock_mp = mocker.patch.object(cli, "mp")
    result = runner.invoke(cli.create, ["/dev/PORT"])
    mock_mp.create_stubs.assert_called_once_with("/dev/PORT")
    assert result.exit_code == 0


def test_cli_init(mocker, mock_prompt, runner):
    """should create project"""
    mock_project = mocker.patch.object(cli, "Project")
    result = runner.invoke(cli.init, ["TestProject"])
    mock_project.assert_called_once_with("TestProject", ["stub"])
    mock_project.return_value.create.assert_called_once()
    assert result.exit_code == 0


def test_cli_stubs_add(mocker, shared_datadir, runner):
    """should add stub"""
    test_stub = shared_datadir / 'esp8266_test_stub'
    test_invalid_stub = shared_datadir / 'esp8266_invalid_stub'
    mock_stubs = mocker.patch.object(cli.mp, "STUBS")
    mock_stubs.validate.side_effect = [exceptions.StubError,
                                       True]
    result = runner.invoke(cli.add, [str(test_invalid_stub.resolve())])
    assert result.exit_code == 1

    result = runner.invoke(cli.add, [str(test_stub.resolve())])
    mock_stubs.add.assert_called_with(test_stub)
    mock_stubs.validate.assert_called_with(test_stub)
    assert result.exit_code == 0
