# -*- coding: utf-8 -*-

import pytest
import pyfakefs
import micropy
from pathlib import Path
import io
import sys
import questionary
import os


@pytest.fixture
def with_stubs(fs_micropy):
    """New Project with Stubs"""
    pyfakefs.fake_filesystem.set_uid(0)
    tmp_dir = Path(os.getenv('HOME'))
    fs_micropy.create_dir(tmp_dir)
    mp = micropy.micropy.MicroPy()
    fs_micropy.add_real_directory(mp.TEMPLATE)
    stubs = [Path(i) for i in ['/foo/stub', '/foo/stub2', '/foo/stub3']]
    [fs_micropy.create_dir(i) for i in stubs]
    [mp.add_stub(i) for i in stubs]
    project = micropy.project.Project("NewProject")
    return project


@pytest.fixture
def mock_prompt(monkeypatch):
    def mock_prompt(*args, **kwargs):
        class prompt_mock:
            def __init__(self, *args, **kwargs):
                return None

            def ask(self):
                return ['stub']
        return prompt_mock(*args, **kwargs)
    monkeypatch.setattr(questionary, 'checkbox', mock_prompt)


def test_project_no_stubs(fs_micropy, mock_micropy):
    """Test New Project Init w/o Stubs"""
    exp_dir = Path.cwd() / "NewProject"
    with pytest.raises(Exception) as e:
        proj = micropy.project.Project("NewProject")
        proj.setup()
        assert "run micropy stubs get" in str(e.value)
    assert not exp_dir.exists()


def test_project_init(with_stubs, mock_prompt):
    """New Project Init with stubs"""
    exp_dir = Path.cwd() / "NewProject"
    with_stubs.setup()
    with_stubs.create()
    assert exp_dir.exists()
    vs_settings = exp_dir / '.vscode' / 'settings.json'
    pylint_settings = exp_dir / '.pylintrc'
    assert vs_settings.exists()
    assert pylint_settings.exists()
    stub_1 = next((i for i in with_stubs.STUBS if i.name == 'stub'))
    assert str(stub_1.path) in vs_settings.read_text()
    assert str(stub_1.path) in pylint_settings.read_text()
