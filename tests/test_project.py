# -*- coding: utf-8 -*-

import shutil
from pathlib import Path

import pytest

from micropy import main, project
from micropy.project.template import TemplateProvider


@pytest.fixture
def mock_pkg(mocker, tmp_path):
    """return mock package"""
    tmp_pkg = tmp_path / 'tmp_pkg'
    tmp_pkg.mkdir()
    mock_tarbytes = mocker.patch.object(
        project.project.utils, 'extract_tarbytes')
    mocker.patch.object(
        project.project.utils, 'get_package_meta')
    mocker.patch.object(
        project.project.utils, 'get_url_filename')
    mocker.patch.object(
        project.project.utils, 'stream_download')
    mock_tarbytes.return_value = tmp_pkg
    return tmp_pkg


@pytest.fixture
def mock_proj_dir(mocker, tmp_path, shared_datadir):
    proj_path = tmp_path / 'tmp_project'
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    return proj_path


def test_project_init(mock_mp_stubs, mock_cwd):
    """Test project setup"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.stubs)[:2]
    proj_path = mock_cwd / "ProjName"
    proj = project.Project(proj_path, stubs=proj_stubs)
    assert proj.path == mock_cwd / 'ProjName'
    assert proj.name == 'ProjName'


def test_project_structure(mock_mp_stubs, mock_cwd, mock_checks):
    """Test if project creates files"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.stubs)[:2]
    proj_path = mock_cwd / "ProjName"
    templates = ['vscode', 'pylint', 'bootstrap', 'pymakr', 'gitignore']
    proj = project.Project(proj_path, templates=templates, stubs=proj_stubs,
                           stub_manager=mp.stubs)
    proj.create()
    templ_files = [i.name for i in (
        TemplateProvider.TEMPLATE_DIR).glob("**/*")]
    proj_files = sorted(
        [i.name for i in proj.path.glob("**/*")])
    expect_files = sorted([*templ_files, *[s.path.name for s in proj.stubs],
                           *set([s.firmware.path.name for s in proj.stubs]),
                           '.micropy', 'micropy.json', 'requirements.txt',
                           'dev-requirements.txt'])
    print("Project Files:", proj_files)
    print("Expect:", expect_files)
    assert expect_files == proj_files


def test_project_load(mocker, shared_datadir, mock_pkg):
    mock_mp = mocker.patch.object(main, 'MicroPy').return_value
    mock_utils = mocker.patch.object(project.project, 'utils')
    mock_shutil = mocker.patch.object(project.project, 'shutil')
    mock_utils.extract_tarbytes.return_value.rglob.side_effect = [
        iter([]),
        iter([
            Path("foobar.py"), Path("setup.py")]),
        iter([
            Path("pkg/__init__.py")]),
        iter([
            Path("foobar.py"), Path("setup.py")]),
    ]
    mock_utils.generate_stub.return_value = (Path(
        "foobar.py"), Path("foobar.pyi"))
    proj_path = shared_datadir / 'project_test'
    proj = project.Project(proj_path, stub_manager=mock_mp.stubs)
    proj.load()
    expect_custom = proj.path / '../esp32_test_stub'
    mock_mp.stubs.add.assert_any_call("esp32-micropython-1.11.0")
    mock_mp.stubs.add.assert_any_call("esp8266-micropython-1.11.0")
    mock_mp.stubs.add.assert_any_call(expect_custom)
    assert mock_mp.stubs.add.call_count == 3
    mock_mp.stubs.resolve_subresource.assert_called_once_with(
        mocker.ANY, proj.data)
    assert proj.data.exists()
    assert mock_shutil.copy2.call_count == 2
    mock_shutil.copy2.assert_called_with(
        Path("foobar.pyi"), (proj.pkg_data / "foobar.pyi"))
    # Test package
    proj.add_package('pkg')
    mock_shutil.copytree.assert_called_once_with(
        Path('pkg'), (proj.pkg_data / 'pkg'))
    # Test Win Priv Fail
    mock_mp.stubs.resolve_subresource.side_effect = [OSError]
    with pytest.raises(SystemExit):
        proj = project.Project(proj_path, stub_manager=mock_mp.stubs)
        proj.load()


def test_project_add_stub(mocker, shared_datadir, tmp_path, mock_pkg):
    """should add stub to project"""
    m_stubman = mocker.MagicMock()
    proj_path = tmp_path / 'tmp_project'
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    # Test Loaded
    proj = project.Project(proj_path, stub_manager=m_stubman)
    proj.load()
    proj.add_stub("mock_stub")
    m_stubman.resolve_subresource.assert_called_with(
        [mocker.ANY, mocker.ANY, mocker.ANY, "mock_stub"], proj.data)
    shutil.rmtree(proj_path)
    shutil.copytree((shared_datadir / 'project_test'), proj_path)
    # Test Not loaded
    proj = project.Project(proj_path, stub_manager=m_stubman)
    proj.add_stub("mock_stub")
    m_stubman.resolve_subresource.assert_called_with(
        [mocker.ANY, mocker.ANY, mocker.ANY, "mock_stub"], proj.data)
    assert m_stubman.resolve_subresource.call_count == 3


def test_project_add_pkg(mocker, mock_proj_dir, shared_datadir, tmp_path,
                         mock_pkg):
    """should add package to requirements"""
    m_stubman = mocker.MagicMock()
    proj = project.Project(mock_proj_dir, stub_manager=m_stubman)
    proj.load()
    proj.add_package('mock_pkg')
    assert proj.packages['mock_pkg'] == "*"
    assert proj.add_package('mock_pkg') is None
    # Test dev
    proj.add_package('another_pkg==1.0.0', dev=True)
    assert proj.dev_packages['another_pkg'] == '==1.0.0'
    # Test requirements.txt
    lines = proj.requirements.read_text().splitlines()
    assert "mock_pkg" in lines
    # Test Context
    expect_proj_stubs = mock_proj_dir / '.micropy' / "NewProject"
    m_stubman.resolve_subresource.return_value = [mocker.MagicMock()]
    mock_update = mocker.patch.object(
        project.project.TemplateProvider, 'update')
    proj = project.Project(
        mock_proj_dir, stub_manager=m_stubman, name="NewProject")
    proj.load()
    assert expect_proj_stubs in proj.context['paths']
    mock_update.assert_called_with('vscode', proj.path, **proj.context)


def test_project_add_requirements(mocker, mock_proj_dir, mock_pkg):
    """should add from requirements.txt"""
    mocker.patch.object(main, "MicroPy").return_value
    proj = project.Project(mock_proj_dir, stub_manager=mocker.MagicMock())
    proj.load()
    # Assert no reqs file
    _reqspath = (proj.requirements, proj.dev_requirements)
    proj.requirements = Path('foobar')
    proj.dev_requirements = Path('foobar')
    added = proj.add_from_requirements()
    assert added is None
    proj.requirements, proj.dev_requirements = _reqspath
    tmp_reqs = proj.path / 'requirements.txt'
    tmp_reqs.touch()
    tmp_reqs.write_text("micropy-cli==1.0.0")
    assert next(iter(proj.add_from_requirements())).name == 'micropy-cli'
