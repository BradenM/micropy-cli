# -*- coding: utf-8 -*-

from micropy.project import Project
from micropy.project.template import TemplateProvider


def test_project_init(mock_micropy, mock_cwd):
    """Test project setup"""
    proj_stubs = list(mock_micropy.STUBS)[:2]
    proj = Project("ProjName", proj_stubs)
    assert proj.path == mock_cwd / 'ProjName'
    assert proj.name == 'ProjName'


def test_project_structure(mock_micropy, mock_cwd):
    """Test if project creates files"""
    proj_stubs = list(mock_micropy.STUBS)[:2]
    proj = Project("ProjName", proj_stubs)
    proj.create()
    templ_files = sorted([i.name for i in (
        TemplateProvider.TEMPLATE_DIR).glob("**/*")])
    proj_files = sorted([i.name for i in proj.path.glob("**/*")])
    print("Project Files:", proj_files)
    assert templ_files == proj_files
