# -*- coding: utf-8 -*-

import pathlib
import shutil
from functools import partial
from pathlib import Path

import pytest

from micropy import project
from micropy.project import modules


@pytest.fixture(autouse=True)
def mock_requests(mocker):
    mocker.patch('requests.session')


@pytest.fixture
def get_module():
    def _get_module(names, mp, **kwargs):
        _templates = list(modules.TemplatesModule.TEMPLATES.keys())
        mods = {
            'stubs': partial(modules.StubsModule, mp.stubs, stubs=list(mp.stubs)[:2]),
            'template': partial(modules.TemplatesModule,
                                templates=_templates),
            'reqs': partial(modules.PackagesModule, 'requirements.txt'),
            'dev-reqs': partial(modules.PackagesModule, 'dev-requirements.txt', dev=True)
        }
        if names == 'all':
            names = ",".join(list(mods.keys()))
        _mods = [mods[n.strip()] for n in names.split(',') if n]
        for m in _mods:
            yield m
    return _get_module


@pytest.fixture
def get_config():
    def _get_config(request, name="NewProject", stubs=None, templates=None, packages={}):
        templates = templates or ['vscode', 'pylint']
        stubs = stubs or []
        _mods = {
            'base': {
                'name': name
            },
            'stubs': {
                'stubs': {s.name: s.stub_version for s in stubs}
            },
            'template': {
                'config': {t: (t in templates) for t in templates}
            },
            'reqs': {
                'packages': packages.get('reqs', {})
            },
            'dev-reqs': {
                'dev-packages': packages.get('dev-reqs', {'micropy-cli': '*'})
            }
        }
        if request == 'all':
            request = ",".join(list(_mods.keys()))
        mods = request.split(',')
        test_config = _mods['base'].copy()
        for m in mods:
            test_config = {**test_config, **_mods[m or 'base']}
        return test_config
    return _get_config


@pytest.fixture
def get_context():
    def _get_context(request, stubs=None, pkg_path=None, data_dir=None):
        stubs = stubs or []
        _frozen = [s.frozen for s in stubs]
        _fware = [s.firmware.frozen for s in stubs if s.firmware is not None]
        _stub_paths = [s.stubs for s in stubs]
        _paths = set([*_frozen, *_fware, *_stub_paths])
        _context = {
            'base': {},
            'stubs': {
                'stubs': set(stubs),
                'paths': list(_paths),
                'datadir': data_dir
            },
            'reqs': {
                'paths': [pkg_path]
            }
        }
        if request == 'all':
            request = ",".join(list(_context.keys()))
        mods = request.split(',')
        if 'reqs' in mods and 'stubs' in mods:
            _ctx = _context['stubs'].copy()
            _ctx['paths'].extend(_context['reqs']['paths'])
            return _ctx
        context = {}
        for m in mods:
            context = {**context, **_context.get(m, {})}
        return context
    return _get_context


@pytest.yield_fixture
def test_project(micropy_stubs, mock_cwd, tmp_path, get_module):
    def _test_project(mods=""):
        mp = micropy_stubs()
        proj_path = tmp_path / "NewProject"
        proj = project.Project(proj_path)
        mods = get_module(mods, mp)
        for m in mods:
            proj.add(m())
        yield proj, mp
        shutil.rmtree(proj_path)
    return _test_project


@pytest.mark.parametrize('mods', ['', 'stubs', 'template', 'reqs', 'dev-reqs', 'all'])
class TestProject:

    def test_create(self, test_project, mods):
        test_proj, _ = next(test_project(mods))
        resp = test_proj.create()
        assert str(resp) == "NewProject"
        assert test_proj.exists

    def test_config(self, test_project, get_config,  mods):
        test_proj, mp = next(test_project(mods))
        expect_config = get_config(mods, stubs=list(mp.stubs)[:2])
        assert test_proj.config == expect_config

    def test_context(self, test_project, get_context, mods):
        test_proj, mp = next(test_project(mods))
        pkg_path = test_proj.data_path / test_proj.name
        stubs = mp.stubs.resolve_subresource(list(mp.stubs), test_proj.data_path)
        expect_context = get_context(mods, stubs=stubs, pkg_path=pkg_path,
                                     data_dir=test_proj.data_path)
        for k in expect_context.keys():
            print("Context Key:", k)
            try:
                assert sorted(test_proj.context.get(k, [])) == sorted(
                    expect_context.get(k, []))
            except TypeError:
                assert test_proj.context.get(k, []) == expect_context[k]
