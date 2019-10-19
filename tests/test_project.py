# -*- coding: utf-8 -*-

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
def mock_pkg(mocker, tmp_path):
    """return mock package"""
    tmp_pkg = tmp_path / 'tmp_pkg'
    tmp_pkg.mkdir()
    (tmp_pkg / 'module.py').touch()
    mock_tarbytes = mocker.patch.object(
        modules.packages.utils, 'extract_tarbytes')
    mocker.patch.object(
        modules.packages.utils, 'get_package_meta')
    mocker.patch.object(
        modules.packages.utils, 'get_url_filename')
    mocker.patch.object(
        modules.packages.utils, 'stream_download')
    mock_tarbytes.return_value = tmp_pkg
    return tmp_pkg


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
    def _test_project(mods="", path=None):
        mp = micropy_stubs()
        proj_path = path if path else tmp_path / "NewProject"
        proj = project.Project(proj_path)
        mods = get_module(mods, mp)
        for m in mods:
            proj.add(m())
        yield proj, mp
        shutil.rmtree(proj_path)
    return _test_project


@pytest.fixture
def tmp_project(tmp_path, shared_datadir):
    path = shared_datadir / 'project_test'
    proj_path = tmp_path / "NewProject"
    shutil.copytree(path, proj_path)
    return proj_path


def test_implementation(mocker):
    """Test Abstract Base Class"""
    mocker.patch.object(modules.ProjectModule, "__abstractmethods__", new_callable=set)
    inst = modules.ProjectModule()
    inst.config
    inst.load()
    inst.create()
    inst.update()
    inst.add([])
    inst.remove([])


@pytest.mark.parametrize(
    'mods',
    ['', 'stubs', 'template', 'reqs', 'dev-reqs', 'all']
)
class TestProject:

    def test_create(self, test_project, mock_checks, mods):
        test_proj, _ = next(test_project(mods))
        assert test_proj.data == {}
        resp = test_proj.create()
        assert str(resp) == "NewProject"
        assert test_proj.exists
        assert test_proj.data is not {}
        assert test_proj.info_path.exists()
        if test_proj._children:
            test_proj.remove(test_proj._children[-1])

    def test_config(self, test_project, get_config,  mods):
        test_proj, mp = next(test_project(mods))
        expect_config = get_config(mods, stubs=list(mp.stubs)[:2])
        assert test_proj.config == expect_config

    def test_context(self, test_project, get_context, mods):
        test_proj, mp = next(test_project(mods))
        pkg_path = test_proj.data_path / test_proj.name
        expect_context = get_context(mods, stubs=mp.stubs, pkg_path=pkg_path,
                                     data_dir=test_proj.data_path)
        for k in expect_context.keys():
            print("Context Key:", k)
            try:
                assert sorted(test_proj.context.get(k, [])) == sorted(
                    expect_context.get(k, []))
            except TypeError:
                assert test_proj.context.get(k, []) == expect_context[k]
            except AssertionError:
                assert len(test_proj.context.get(k, [])) == len(expect_context[k])

    def test_load(self, mock_pkg, tmp_project, mock_checks, test_project, mods):
        proj, mp = next(test_project(mods, path=tmp_project))
        proj.load(run_checks=mp.RUN_CHECKS)

    def test_update(self, mock_pkg, tmp_project, mock_checks, test_project, mods):
        proj, mp = next(test_project(mods, path=tmp_project))
        proj.update()


class TestStubsModule:

    @pytest.fixture
    def stub_module(self, get_module, micropy_stubs, mocker):
        mp = micropy_stubs()
        mock_parent = mocker.patch.object(modules.StubsModule, 'parent')
        stub_mod = next(get_module('stubs', mp))()
        stub_mod.log = mock_parent.log
        return stub_mod, mp

    def test_resolve_stubs(self, stub_module, mocker):
        stub_module, mp = stub_module
        assert len(stub_module.stubs) == 1
        mocker.resetall()
        stub_module.stub_manager.resolve_subresource = mocker.MagicMock()
        stub_module.stub_manager.resolve_subresource.side_effect = [OSError]
        assert stub_module._resolve_subresource([]) == stub_module._stubs
        stub_module._parent = mocker.MagicMock()
        with pytest.raises(SystemExit):
            stub_module._resolve_subresource([])

    def test_load(self, tmp_project, stub_module, get_stub_paths):
        custom_stub = next(get_stub_paths())
        stub_mod, mp = stub_module
        stub_data = {
            "esp32-micropython-1.11.0": "1.2.0",
            "esp8266-micropython-1.11.0": "1.2.0",
            "custom-stub": str(custom_stub)
        }
        stub_mod.stub_manager.add.return_value = mp.stubs
        assert stub_mod.load(stub_data=stub_data)

    def test_add_stub(self, test_project, get_stub_paths, mocker):
        proj, mp = next(test_project('stubs'))
        proj.create()
        stub_path = next(get_stub_paths())
        stub = mocker.MagicMock()
        stub.path = stub_path
        stub.frozen = stub_path / 'frozen'
        stub.stubs = stub_path / 'stubs'
        stub.firmware = stub
        proj.add_stub(stub)
        print(proj.stubs)


class TestPackagesModule:

    def test_add_package(self, mocker, mock_pkg, test_project):
        proj, mp = next(test_project('reqs'))
        proj.create()
        proj.add_package('somepkg')
        res = proj.add_package('somepkg')
        # Shouldnt allow duplicate pkgs
        assert res is None
        mock_shutil = mocker.patch.object(modules.packages, "shutil")
        # Tests for modules
        mocker.patch.object(modules.packages.utils, 'generate_stub',
                            return_value=(Path("mod.py"), Path("mod.pyi")))
        proj.add_package('some_module')
        mock_shutil.copy2.assert_called()
        # Tests for packages
        mock_rglob = mocker.patch.object(modules.packages.Path, "rglob")
        mock_rglob.return_value = iter([Path("SomePkg/__init__.py")])
        res = proj.add_package('anotha_pkg')
        mock_shutil.copytree.assert_called_once()
