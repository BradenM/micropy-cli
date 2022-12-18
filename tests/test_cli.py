import sys
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from micropy import cli
from micropy.exceptions import RequirementException
from pytest_mock import MockFixture


@pytest.fixture
def runner():
    runner = CliRunner()
    return runner


@pytest.fixture
def mock_mpy(mocker):
    mock_mp = mocker.patch("micropy.main.MicroPy")
    mocker.patch.object(click.Context, "find_object").return_value = mock_mp
    return mock_mp


def test_cli_micropy(runner, mocker, mock_cwd):
    """should execute"""
    if (mock_cwd / ".micropy").exists():
        (mock_cwd / ".micropy").unlink()
    result = runner.invoke(cli.cli)
    assert result.exit_code == 0
    expected = "CLI Application for creating/managing" " Micropython Projects."
    assert expected in result.output
    # should alert about update
    mocker.patch.object(cli.utils, "is_update_available", return_value="1.0.0")
    log_spy = mocker.spy(cli, "Log")
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
    mock_mpy.stubs.iter_by_firmware.return_value = m_data
    result = runner.invoke(cli.list)
    assert result.exit_code == 0
    for s in ["dev1", "dev2"]:
        assert s in result.output


def test_stub_create(runner, mock_mpy):
    """should call create_stubs"""
    result = runner.invoke(cli.create, ["/dev/PORT"], obj=mock_mpy)
    mock_mpy.create_stubs.assert_called_once_with("/dev/PORT", verbose=False)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "cliargs,expargs",
    [
        (
            "TestProject -t vscode",
            {
                "project": {"path": "TestProject", "name": None},
                "template": {"templates": ("vscode",)},
            },
        ),
        (
            "-t vscode",
            {
                "project": {"path": Path.cwd(), "name": "TestProject"},
                "template": {"templates": ("vscode",)},
            },
        ),
    ],
)
def test_cli_init(mocker, mock_mpy, shared_datadir, mock_prompt, runner, cliargs, expargs):
    """should create project"""
    # Mock Project
    mock_project = mocker.patch.object(cli, "Project")
    mock_modules = mocker.patch.object(cli, "modules")
    # Mock Text Prompt
    ptext_mock = mocker.patch.object(cli.prompt, "text").return_value
    ptext_mock.ask.return_value = "TestProject"
    # Test with no stubs (should fail)
    result = runner.invoke(cli.init, cliargs.split())
    assert result.exit_code == 1
    # Test with Stubs
    mock_mpy.stubs = ["stub"]
    result = runner.invoke(cli.init, cliargs.split())
    # Assert Project
    exp_project = expargs.pop("project", {})
    exp_path = exp_project.pop("path", mocker.ANY)
    mock_project.assert_called_once_with(exp_path, **exp_project)
    # mock_add = mock_project.return_value.add
    # Assert Templates
    expect_calls = [
        mocker.call(mock_modules.StubsModule, mock_mpy.stubs, stubs=["stub"]),
        mocker.call(mock_modules.PackagesModule, "requirements.txt"),
        mocker.call(mock_modules.DevPackagesModule, "dev-requirements.txt"),
        mocker.call(mock_modules.TemplatesModule, templates=("vscode",), run_checks=mocker.ANY),
    ]
    mock_project.return_value.add.assert_has_calls(expect_calls, any_order=True)
    # # Assert Exit Code
    mock_project.return_value.create.assert_called_once()
    assert result.exit_code == 0


@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="Some change in behavior with magic mock possibly."
)
def test_cli_stubs_add(mocker, mock_mpy, shared_datadir, runner, tmp_path, mock_checks):
    """should add stub"""
    mock_proj = mocker.patch.object(cli, "Project").return_value
    mock_proj.exists.return_value = True
    mock_mpy.project = mock_proj
    mock_mpy.stubs.add.side_effect = [cli.exc.StubError, cli.exc.StubNotFound, mocker.MagicMock()]
    mock_mpy.log.error = print

    mocker.spy(cli.sys, "exit")

    result = runner.invoke(cli.add, ["invalid-stub"], obj=mock_mpy)
    assert cli.sys.exit.called_with(1)
    assert "is not a valid stub" in result.output
    assert result.exit_code == 1

    result = runner.invoke(cli.add, ["not-real-stub"])
    assert cli.sys.exit.called_with(1)
    assert "could not be found" in result.output
    assert result.exit_code == 1

    result = runner.invoke(cli.add, ["real-stub"])
    assert mock_proj.add_stub.call_count == 1
    assert result.exit_code == 0


def test_cli_stubs_search(mock_mpy, mocker: MockFixture, runner):
    """should search stubs"""
    pkg_stub = mocker.stub()
    pkg_stub.repo_name = "Test1"
    pkg_stub.name = "stub-pkg"
    pkg_stub.version = "1.0.0"
    mock_mpy.repo.search.return_value = [pkg_stub]
    result = runner.invoke(cli.search, ["esp8266"])
    assert result.exit_code == 0


class TestInstall:
    @pytest.fixture
    def mock_proj(self, mocker, mock_mpy):
        mock_project = mocker.patch.object(cli, "Project")
        mock_proj = mock_project.return_value
        mock_mpy.project = mock_proj
        return mock_proj

    def test_normal(self, runner, mock_proj):
        result = runner.invoke(cli.install, ["package", "--dev"])
        assert result.exit_code == 0
        mock_proj.add_package.assert_called_once_with("package", dev=True)

    def test_from_requirements(self, runner, mock_proj):
        result = runner.invoke(cli.install, "")
        assert result.exit_code == 0
        mock_proj.add_from_file.side_effect = [FileNotFoundError]
        result = runner.invoke(cli.install, "")
        assert result.exit_code == 1
        assert "Aborted!" in result.output

    def test_no_project_found(self, runner):
        result = runner.invoke(cli.install, ["package"])
        assert result.exit_code == 1

    def test_bad_package_name(self, runner, mock_proj):
        mock_proj.add_package.side_effect = [RequirementException]
        result = runner.invoke(cli.install, ["badpackage"])
        assert result.exit_code == 1
        assert "Aborted!" in result.output

    def test_from_path(self, runner, mock_proj, tmp_path):
        tmp_package = tmp_path / "mycustompackage"
        tmp_package.mkdir()
        result = runner.invoke(cli.install, ["--path", str(tmp_package)])
        assert result.exit_code == 0
