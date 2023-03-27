from pathlib import Path
from typing import List, NamedTuple, Optional

import pytest
import typer
from micropy import utils
from micropy.app import main as main_app
from micropy.app.main import TemplateEnum, app
from micropy.project import Project
from pytest_mock import MockFixture
from tests.app.conftest import MicroPyScenario, context_mock

# current working directory symbol
CWD = object()


@pytest.fixture
def project_path(tmp_path):
    return tmp_path / "test_project"


class TemplateParamCase(NamedTuple):
    value: Optional[List[TemplateEnum]]
    expected: List[TemplateEnum]
    prompt: Optional[List[TemplateEnum]]
    confirm: Optional[bool] = None


@pytest.fixture(
    params=[
        TemplateParamCase(value=None, expected=[], prompt=[], confirm=True),
        TemplateParamCase(value=None, expected=[TemplateEnum.vscode], prompt=[TemplateEnum.vscode]),
        TemplateParamCase(value=[TemplateEnum.vscode], expected=[TemplateEnum.vscode], prompt=None),
    ]
)
def template_param(request: pytest.FixtureRequest, mocker: MockFixture):
    param: TemplateParamCase = request.param
    mock_prompt = mocker.MagicMock()
    mock_confirm = mocker.MagicMock(return_value=param.prompt)
    mock_prompt.ask.return_value = param.prompt
    mock_confirm.ask.return_value = param.confirm
    mocker.patch("questionary.checkbox", return_value=mock_prompt)
    mocker.patch("questionary.confirm", return_value=mock_confirm)
    ctx = request.getfixturevalue("context_mock")
    yield param
    if ctx.resilient_parsing:
        return
    if param.prompt is None:
        mock_prompt.ask.assert_not_called()
    else:
        mock_prompt.ask.assert_called_once()
    if param.confirm is None:
        mock_confirm.ask.assert_not_called()
    else:
        mock_confirm.ask.assert_called_once()


def test_template_callback(mocker: MockFixture, micropy_obj, context_mock, template_param):
    if context_mock.resilient_parsing:
        assert main_app.template_callback(context_mock, template_param.value) is None
        return
    assert main_app.template_callback(context_mock, template_param.value) == template_param.expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (None, CWD),
        ("NewProject", "NewProject"),
        ("/tmp/NewProject", "/tmp/NewProject"),
    ],
)
def test_path_callback(mocker: MockFixture, micropy_obj, context_mock, input, expected):
    expected = Path.cwd() if expected == CWD else expected
    if context_mock.resilient_parsing:
        assert main_app.path_callback(context_mock, input) is None
        return
    assert main_app.path_callback(context_mock, input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (None, CWD),
        ("NewProject", "NewProject"),
        ("/tmp/NewProject", "/tmp/NewProject"),
    ],
)
def test_name_callback(mocker: MockFixture, micropy_obj, context_mock, input, expected):
    expected = (Path.cwd()).name if expected == CWD else expected
    mock_ask = mocker.MagicMock()
    mock_ask.ask.return_value.strip.return_value = expected
    mocker.patch("questionary.text", return_value=mock_ask)
    if context_mock.resilient_parsing:
        assert main_app.name_callback(context_mock, input) is None
        return
    assert main_app.name_callback(context_mock, input) == expected


@pytest.mark.parametrize(
    "micropy_obj,expect",
    [
        (
            MicroPyScenario(),
            True,
        ),
        (MicroPyScenario(project_exists=False), None),
    ],
    indirect=["micropy_obj"],
)
def test_main_callback(mocker: MockFixture, context_mock, micropy_obj, expect):
    if context_mock.resilient_parsing:
        assert main_app.main_callback(context_mock) is None
        return
    util_mock = mocker.patch.object(utils, "is_update_available", return_value=False)
    main_app.main_callback(context_mock)
    if expect:
        util_mock.assert_called_once()
    else:
        util_mock.assert_not_called()


@pytest.mark.parametrize(
    "input,prompt,micropy_obj,expected",
    [
        (None, [], MicroPyScenario(has_stubs=False), typer.Abort),
        (None, [], MicroPyScenario(), typer.BadParameter),
        (["a-stub"], None, MicroPyScenario(), ["a-stub"]),
        (["a-stub"], None, MicroPyScenario(has_stubs=False), ["a-stub"]),
        (None, ["some-stub"], MicroPyScenario(), ["some-stub"]),
    ],
    indirect=["micropy_obj"],
)
def test_stubs_callback(mocker: MockFixture, context_mock, input, prompt, micropy_obj, expected):
    mock_ask = mocker.MagicMock()
    mock_ask.ask.return_value = prompt
    mocker.patch("questionary.checkbox", return_value=mock_ask)
    if context_mock.resilient_parsing:
        assert main_app.stubs_callback(context_mock, input) is None
        return
    if not isinstance(expected, list):
        with pytest.raises(expected):
            main_app.stubs_callback(context_mock, input)
    else:
        assert main_app.stubs_callback(context_mock, input) == expected
        if prompt is None:
            mock_ask.ask.assert_not_called()
        else:
            mock_ask.ask.assert_called_once()


# Test main_init function
def test_main_init(mocker, micropy_obj, project_path, runner):
    ask_mock = mocker.MagicMock()
    ask_mock.ask.return_value = "test_project"
    mocker.patch("questionary.text", return_value=ask_mock)
    mocker.patch("questionary.checkbox")

    result = runner.invoke(app, ["init", str(project_path)], obj=micropy_obj)
    print(result.stdout)
    assert result.exit_code == 0
    assert f"Initiating {project_path.name}" in result.stdout
    assert "Project Created" in result.stdout


ctx = context_mock


@pytest.mark.parametrize(
    "micropy_obj,expect",
    [
        (MicroPyScenario(), Project),
        (MicroPyScenario(project_exists=False), typer.Abort),
    ],
    indirect=["micropy_obj"],
)
def test_ensure_project(mocker: MockFixture, micropy_obj, expect, tmp_path):
    ctx = mocker.MagicMock(typer.Context, autospec=True).return_value
    ctx.ensure_object.return_value = micropy_obj
    if expect == typer.Abort:
        with pytest.raises(typer.Abort):
            main_app.ensure_project(ctx)
    else:
        project = main_app.ensure_project(ctx)
        assert project == micropy_obj.project


@pytest.mark.parametrize(
    "input,expected",
    [(None, None), (Path("somepath"), typer.Exit)],
)
def test_install_local_callback(micropy_obj, context_mock, input, expected):
    if context_mock.resilient_parsing:
        assert main_app.install_local_callback(context_mock, input) is None
        return
    if expected == typer.Exit:
        with pytest.raises(typer.Exit):
            main_app.install_local_callback(context_mock, input)
        micropy_obj.project.add_package.assert_called_once()
        return
    assert main_app.install_local_callback(context_mock, input) == expected
    micropy_obj.project.add_package.assert_not_called()


@pytest.mark.parametrize(
    "packages, path_in_params",
    [(None, True), (None, False), (["pkg1", "pkg2"], False), (["pkg1", "pkg2"], True)],
)
def test_install_project_callback(mocker, context_mock, micropy_obj, packages, path_in_params):
    if context_mock.resilient_parsing:
        assert main_app.install_local_callback(context_mock, packages) is None
        return
    context_mock.params = dict()
    if path_in_params:
        context_mock.params["path"] = "some_path"
    context_mock.params["dev"] = False

    if path_in_params:
        result = main_app.install_project_callback(context_mock, packages)
        assert result is None
        return

    if packages is None and not path_in_params:
        with pytest.raises(typer.Exit):
            main_app.install_project_callback(context_mock, packages)
            micropy_obj.project.add_from_file.assert_called_once()
        return

    result = main_app.install_project_callback(context_mock, packages)
    assert result == packages


@pytest.mark.parametrize("dev_flag", [True, False])
def test_main_install(mocker, micropy_obj, runner, dev_flag):
    packages = ["package1", "package2"]
    result = runner.invoke(
        app,
        ["install", *packages, "--dev"] if dev_flag else ["install", *packages],
        obj=micropy_obj,
    )
    print(result.stdout)

    assert result.exit_code == 0
    assert "Installing Packages" in result.stdout

    for pkg in packages:
        micropy_obj.project.add_package.assert_any_call(pkg, dev=dev_flag)
