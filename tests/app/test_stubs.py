from pathlib import Path

import pytest
from micropy.app import stubs as stubs_app
from micropy.app.stubs import stubs_app as app
from micropy.exceptions import StubError, StubNotFound
from micropy.pyd import PyDevice
from micropy.stubs import StubRepositoryPackage
from micropy.stubs.source import StubSource
from pytest_mock import MockerFixture
from stubber.codemod.modify_list import ListChangeSet
from tests.app.conftest import MicroPyScenario


@pytest.mark.parametrize(
    "input,expected",
    [(None, None), (["mod-1", "mod-2"], ListChangeSet.from_strings(add=["mod-1", "mod-2"]))],
)
def test_create_changeset(input, expected):
    result = stubs_app.create_changeset(input)
    if expected is None:
        assert result is None
    else:
        assert result.add[0].children == expected.add[0].children
        assert result.add[1].children == expected.add[1].children


@pytest.fixture()
def pydevice_mock(mocker: MockerFixture):
    def mock_copy_from(dev_path, tmp_dir, **kwargs):
        stub_dir = Path(tmp_dir) / "stubs"
        stub_dir.mkdir()

    pyb_mock = mocker.MagicMock(PyDevice, autospec=True)
    pyb_mock.return_value.copy_from = mock_copy_from
    return pyb_mock


@pytest.fixture()
def pyb_mock(request: pytest.FixtureRequest, mocker: MockerFixture):
    device_mock = request.getfixturevalue("pydevice_mock")
    pyb = device_mock.return_value
    mocker.patch("micropy.app.stubs.PyDevice", return_value=pyb)
    return pyb


@pytest.fixture
def stubs_locator_mock(mocker: MockerFixture):
    stubs_locator = mocker.MagicMock(StubSource, autospec=True)
    mocker.patch("micropy.app.stubs.stubs_source.StubSource", return_value=stubs_locator)
    return stubs_locator


@pytest.fixture()
def stub_search_data(mocker: MockerFixture):
    stub1 = mocker.MagicMock(StubRepositoryPackage, autospec=True)
    stub2 = mocker.MagicMock(StubRepositoryPackage, autospec=True)
    stub3 = mocker.MagicMock(StubRepositoryPackage, autospec=True)
    stub1.name = "test1"
    stub1.version = "1.0.0"
    stub2.name = "test2"
    stub2.version = "1.1.0"
    stub3.name = "test3"
    stub3.version = "0.9.0"
    return [
        stub1,
        stub2,
        stub3,
    ]


def test_stubs_create(mocker: MockerFixture, pyb_mock, micropy_obj, runner):
    result = runner.invoke(app, ["create", "/dev/port"], obj=micropy_obj)
    print(result.stdout)
    pyb_mock.run_script.assert_called_once()
    pyb_mock.disconnect.assert_called_once()


def test_stubs_create__connect_error(pydevice_mock, micropy_obj, runner):
    pydevice_mock.side_effect = SystemExit()
    result = runner.invoke(app, ["create", "/dev/port"], obj=micropy_obj)
    assert result.return_value is None


def test_stubs_create__script_error(pyb_mock, micropy_obj, runner):
    pyb_mock.run_script.side_effect = Exception("Script error")
    with pytest.raises(Exception, match="Script error"):
        result = runner.invoke(
            app, ["create", "/dev/port"], obj=micropy_obj, catch_exceptions=False
        )
        assert result.return_value is None


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.parametrize("micropy_obj", [MicroPyScenario(impl_add=False)], indirect=True)
def test_stubs_add_success(micropy_obj, runner, stubs_locator_mock, mock_repo, force):
    stubs_locator_mock.ready.return_value.__enter__.return_value = "test-stub"
    args = ["add", "test-stub"]
    if force:
        args.append("--force")
    result = runner.invoke(app, args, obj=micropy_obj, catch_exceptions=False)
    print(result.stdout)
    assert result.exit_code == 0
    assert "added!" in result.stdout
    stubs_locator_mock.ready.assert_called_once_with("test-stub")
    micropy_obj.stubs.add.assert_called_once_with("test-stub", force=force)


@pytest.mark.parametrize("micropy_obj", [MicroPyScenario(impl_add=False)], indirect=True)
def test_stubs_add__not_found(micropy_obj, runner, stubs_locator_mock, mock_repo):
    micropy_obj.stubs.add.side_effect = StubNotFound()
    result = runner.invoke(app, ["add", "nonexistent-stub"], obj=micropy_obj)
    assert result.exit_code == 1
    assert "could not be found" in result.stdout
    stubs_locator_mock.ready.assert_called_once_with("nonexistent-stub")


@pytest.mark.parametrize("micropy_obj", [MicroPyScenario(impl_add=False)], indirect=True)
def test_stubs_add__invalid(micropy_obj, runner, stubs_locator_mock, mock_repo):
    micropy_obj.stubs.add.side_effect = StubError()
    result = runner.invoke(app, ["add", "invalid-stub"], obj=micropy_obj)
    assert result.exit_code == 1
    assert "is not a valid stub!" in result.stdout
    stubs_locator_mock.ready.assert_called_once_with("invalid-stub")


@pytest.mark.parametrize(
    "micropy_obj", [MicroPyScenario(), MicroPyScenario(project_exists=False)], indirect=True
)
def test_stubs_list(micropy_obj, runner):
    result = runner.invoke(app, ["list"], obj=micropy_obj)
    assert result.exit_code == 0
    assert "Installed Stubs" in result.stdout
    print(result.stdout)
    if not micropy_obj.project.exists:
        micropy_obj.stubs.iter_by_firmware.assert_called_once()
    else:
        assert micropy_obj.stubs.iter_by_firmware.call_count == 2


@pytest.mark.parametrize("outdated", [True, False])
def test_stubs_search(stub_search_data, micropy_obj, runner, outdated):
    micropy_obj.stubs._loaded = {"test1", "test3"}
    micropy_obj.stubs._firmware = {"test1", "test3"}
    micropy_obj.repo.search.return_value = stub_search_data

    args = ["search", "test"]
    if outdated:
        args.append("--show-outdated")
    result = runner.invoke(app, args, obj=micropy_obj, catch_exceptions=False)

    assert result.exit_code == 0
    assert "Results for test" in result.stdout
    assert "test1" in result.stdout
    assert "test2" in result.stdout
    assert "test3" in result.stdout
    assert "Installed" in result.stdout


def test_stubs_search_no_results(mocker: MockerFixture, micropy_obj, runner):
    micropy_obj.repo.search.return_value = []

    result = runner.invoke(app, ["search", "nonexistent"], obj=micropy_obj)

    assert result.exit_code == 0
    assert "No results found for: nonexistent" in result.stdout
