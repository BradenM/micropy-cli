# -*- coding: utf-8 -*-

from micropy import project
from micropy.project.template import TemplateProvider


def test_project_init(mock_mp_stubs, mock_cwd):
    """Test project setup"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.STUBS)[:2]
    proj = project.Project("ProjName", stubs=proj_stubs)
    assert proj.path == mock_cwd / 'ProjName'
    assert proj.name == 'ProjName'


def test_project_structure(mock_mp_stubs, mock_cwd):
    """Test if project creates files"""
    mp = mock_mp_stubs
    proj_stubs = list(mp.STUBS)[:2]
    proj = project.Project("ProjName", stubs=proj_stubs,
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
