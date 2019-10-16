# -*- coding: utf-8 -*-

import pathlib
from functools import partial
from pathlib import Path

import pytest

from micropy import project
from micropy.project import modules


@pytest.fixture(autouse=True)
def mock_requests(mocker):
    mocker.patch('requests.session')


@pytest.fixture
def get_module(micropy_stubs):
    mp = micropy_stubs()
    mods = {
        'stubs': partial(modules.StubsModule, mp.stubs, stubs=list(mp.stubs)[:1]),
        'template': partial(modules.TemplatesModule,
                            templates=list(modules.TemplatesModule.TEMPLATES.keys())),
        'reqs': partial(modules.PackagesModule, 'requirements.txt'),
        'dev-reqs': partial(modules.PackagesModule, 'dev-requirements.txt', name='dev-packages')
    }

    def _get_module(name, **kwargs):
        if name == 'all':
            _mods = [mods[n] for n in list(mods.keys())]
            for m in _mods:
                yield m
        else:
            mod = mods[name]
            mod.keywords.update(**kwargs)
            yield mod
    return _get_module


@pytest.mark.parametrize('mods', ['stubs', 'template', 'reqs', 'dev-reqs', 'all'])
def test_create_project(mocker, mock_cwd, get_module, mods):
    mods = list(get_module(mods))
    proj_path = mock_cwd / 'NewProject'
    proj = project.Project(proj_path)
    for m in mods:
        print(mods)
        proj.add(m())
    resp = proj.create()
    assert str(resp) == "NewProject"
