# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

from micropy import project
from micropy.project.template import TemplateProvider


def test_project_init(mock_mp_stubs, mock_cwd):
    """Test project setup"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.STUBS)[:2]
    proj_path = mock_cwd / "ProjName"
    proj = project.Project(proj_path, stubs=proj_stubs)
    assert proj.path == mock_cwd / 'ProjName'
    assert proj.name == 'ProjName'


def test_project_structure(mock_mp_stubs, mock_cwd):
    """Test if project creates files"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.STUBS)[:2]
    proj_path = mock_cwd / "ProjName"
    templates = ['vscode', 'pylint', 'bootstrap', 'pymakr']
    proj = project.Project(proj_path, templates=templates, stubs=proj_stubs,
                           stub_manager=mp.STUBS)
    proj.create()
    templ_files = [i.name for i in (
        TemplateProvider.TEMPLATE_DIR).glob("**/*")]
    proj_files = sorted(
        [i.name for i in proj.path.glob("**/*")])
    expect_files = sorted([*templ_files, *[s.path.name for s in proj.stubs],
                           *set([s.firmware.path.name for s in proj.stubs]),
                           '.micropy', 'micropy.json'])
    print("Project Files:", proj_files)
    print("Expect:", expect_files)
    assert expect_files == proj_files


def test_project_load(mocker, shared_datadir):
    mock_mp = mocker.patch.object(project.project, 'MicroPy').return_value
    mock_utils = mocker.patch.object(project.project, 'utils')
    mock_shutil = mocker.patch.object(project.project, 'shutil')
    mock_utils.extract_tarbytes.return_value.rglob.return_value = (
        Path("foobar.py"), Path("setup.py"))
    mock_utils.generate_stub.return_value = (Path(
        "foobar.py"), Path("foobar.pyi"))
    proj_path = shared_datadir / 'project_test'
    proj = project.Project.resolve(proj_path)
    expect_custom = proj.path / '../esp32_test_stub'
    mock_mp.STUBS.add.assert_any_call("esp32-micropython-1.11.0")
    mock_mp.STUBS.add.assert_any_call("esp8266-micropython-1.11.0")
    mock_mp.STUBS.add.assert_any_call(expect_custom)
    assert mock_mp.STUBS.add.call_count == 3
    mock_mp.STUBS.resolve_subresource.assert_called_once_with(
        mocker.ANY, proj.data)
    assert proj.data.exists()
    assert mock_shutil.copy2.call_count == 2
    mock_shutil.copy2.assert_called_with(
        Path("foobar.pyi"), (proj.pkg_data / "foobar.pyi"))


def test_project_add_stub(mocker, shared_datadir, tmp_path):
    """should add stub to project"""
    mock_mp = mocker.patch.object(project.project, 'MicroPy').return_value
    mocker.patch.object(project.project, 'utils')
    proj_path = tmp_path / 'tmp_project'
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    # Test Loaded
    proj = project.Project.resolve(proj_path)
    proj.add_stub("mock_stub")
    mock_mp.STUBS.resolve_subresource.assert_called_with(
        [mocker.ANY, mocker.ANY, mocker.ANY, "mock_stub"], proj.data)
    shutil.rmtree(proj_path)
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    # Test Not loaded
    proj = project.Project(proj_path, stub_manager=mock_mp.STUBS)
    proj.add_stub("mock_stub")
    mock_mp.STUBS.resolve_subresource.assert_called_with(
        [mocker.ANY, mocker.ANY, mocker.ANY, "mock_stub"], proj.data)
    assert mock_mp.STUBS.resolve_subresource.call_count == 3


def test_project_add_pkg(mocker, shared_datadir, tmp_path):
    """should add package to requirements"""
    mock_mp = mocker.patch.object(project.project, "MicroPy").return_value
    mocker.patch.object(project.project, 'utils')
    proj_path = tmp_path / 'tmp_project'
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    proj = project.Project.resolve(proj_path)
    proj.add_package('mock_pkg')
    assert proj.packages['mock_pkg'] == "*"
    assert proj.add_package('mock_pkg') is None
    # Test dev
    proj.add_package('another_pkg==1.0.0', dev=True)
    assert proj.dev_packages['another_pkg'] == '==1.0.0'
    # Test Context
    expect_proj_stubs = proj_path / '.micropy' / "NewProject"
    mock_manager = mock_mp.STUBS
    mock_manager.resolve_subresource.return_value = [mocker.MagicMock()]
    mock_update = mocker.patch.object(
        project.project.TemplateProvider, 'update')
    proj = project.Project(
        proj_path, stub_manager=mock_manager, name="NewProject")
    proj.load()
    assert expect_proj_stubs in proj.context['paths']
    mock_update.assert_called_with('vscode', proj.path, **proj.context)
