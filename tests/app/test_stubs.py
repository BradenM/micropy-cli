from pathlib import Path

import pytest
from micropy.app import stubs as stubs_app
from micropy.app.stubs import stubs_app as app
from micropy.pyd import PyDevice
from pytest_mock import MockerFixture
from stubber.codemod.modify_list import ListChangeSet


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
    def mock_copy_from(dev_path, tmp_dir):
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
