# -*- coding: utf-8 -*-

from micropy.project import Project


def test_project_init(mock_micropy, mock_cwd):
    """Test project setup"""
    proj_stubs = mock_micropy.STUBS[:2]
    proj = Project("ProjName", proj_stubs)
    assert proj.path == mock_cwd / 'ProjName'
    assert proj.name == 'ProjName'


def test_project_ctx(mock_micropy, tmp_path):
    """Test Project Context"""
    proj_stubs = mock_micropy.STUBS[:2]
    proj = Project("ProjName", proj_stubs)
    test_stub = proj_stubs[0]
    exp_pylint_0 = {
        "path": str(test_stub.path)
    }
    exp_vscode = [str(i.path) for i in proj_stubs]
    assert exp_pylint_0 == proj.context['pylint'].pop(str(test_stub))
    assert len(proj_stubs) == len(proj.context['pylint'].keys())
    assert exp_vscode == proj.context["vscode"]


def test_project_structure(mock_micropy, mock_cwd):
    """Test if project creates files"""
    proj_stubs = mock_micropy.STUBS[:2]
    proj = Project("ProjName", proj_stubs)
    proj.create()
    templ_files = sorted([i.name for i in (
        mock_micropy.TEMPLATE / '{{ cookiecutter.project }}').glob("**/*")])
    proj_files = sorted([i.name for i in proj.path.glob("**/*")])
    print("Project Files:", proj_files)
    assert templ_files == proj_files
