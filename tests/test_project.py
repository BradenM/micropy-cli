import shutil

import pytest
from boltons import setutils
from micropy import config, packages, project
from micropy.exceptions import RequirementException
from micropy.project import modules
from requests import RequestException


@pytest.fixture
def get_module(tmp_path):
    def _get_module(names, mp, **kwargs):
        _templates = list(modules.TemplatesModule.TEMPLATES.keys())
        mods = {
            "stubs": (
                (
                    modules.StubsModule,
                    mp.stubs,
                ),
                {"stubs": list(mp.stubs)[:2]},
            ),
            "template": ((modules.TemplatesModule, _templates), {}),
            "reqs": ((modules.PackagesModule, "requirements.txt"), {}),
            "dev-reqs": ((modules.DevPackagesModule, "dev-requirements.txt"), {}),
        }
        if names == "all":
            names = ",".join(list(mods.keys()))
        _mods = [mods[n.strip()] for n in names.split(",") if n]
        yield from _mods

    return _get_module


@pytest.fixture
def get_config():
    def _get_config(request, name="NewProject", stubs=None, templates=None, packages={}):
        templates = templates or ["vscode", "pylint"]
        stubs = stubs or []
        _mods = {
            "base": {
                "name": name,
            },
            "stubs": {"stubs": {s.name: s.stub_version for s in stubs}},
            "template": {"config": {t: (t in templates) for t in templates}},
            "reqs": {"packages": packages.get("reqs", {})},
            "dev-reqs": {"dev-packages": packages.get("dev-reqs", {"micropy-cli": "*"})},
        }
        if request == "all":
            request = ",".join(list(_mods.keys()))
        mods = request.split(",")
        test_config = _mods["base"].copy()
        for m in mods:
            test_config = {**test_config, **_mods[m or "base"]}
        return test_config

    return _get_config


@pytest.fixture
def get_context():
    def _get_context(request, stubs=None, pkg_path=None, data_dir=None):
        stubs = stubs or []
        _frozen = [s.frozen for s in stubs]
        _fware = [s.firmware.frozen for s in stubs if s.firmware is not None]
        _stub_paths = [s.stubs for s in stubs]
        _paths = setutils.IndexedSet([*_frozen, *_fware, *_stub_paths])
        _context = {
            "base": {},
            "stubs": {
                "stubs": set(stubs),
                "paths": _paths,
                "datadir": data_dir,
            },
            "reqs": {"paths": setutils.IndexedSet([pkg_path]), "local_paths": set()},
        }
        if request == "all":
            request = ",".join(list(_context.keys()))
        mods = request.split(",")
        if "reqs" in mods and "stubs" in mods:
            _ctx = _context["stubs"].copy()
            _ctx["paths"].update(_context["reqs"]["paths"])
            _ctx["local_paths"] = _context["reqs"]["local_paths"]
            return _ctx
        context = {}
        for m in mods:
            context = {**context, **_context.get(m, {})}
        return context

    return _get_context


@pytest.fixture
def test_project(micropy_stubs, tmp_path, get_module):
    def _test_project(mods="", path=None):
        mp = micropy_stubs()
        proj_path = path if path else tmp_path / "NewProject"
        proj = project.Project(proj_path)
        mods = get_module(mods, mp)
        for m in mods:
            proj.add(*m[0], **m[1])
        yield proj, mp

    return _test_project


@pytest.fixture
def tmp_project(tmp_path, shared_datadir):
    path = shared_datadir / "project_test"
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


def test_project_queue(tmp_path, mock_cwd, mocker):
    mocker.patch("micropy.project.project.Config")
    path = tmp_path / "project_path"
    proj = project.Project(path)
    # should create/load projects based on <MODULES>.PRIORITY,
    # not based on order added
    mock_parent = mocker.Mock()
    mock_parent.m1.return_value = mocker.Mock(PRIORITY=8)
    mock_parent.m2.return_value = mocker.Mock(PRIORITY=0)
    mock_parent.m3.return_value = mocker.Mock(PRIORITY=9)
    proj.add(mock_parent.m1)
    proj.add(mock_parent.m2)
    proj.add(mock_parent.m3)
    proj.create()
    # should be called in order of priority (9 being highest)
    mock_parent.assert_has_calls(
        [
            # adding them doesnt matter
            mocker.call.m1(log=mocker.ANY, parent=mocker.ANY),
            mocker.call.m2(log=mocker.ANY, parent=mocker.ANY),
            mocker.call.m3(log=mocker.ANY, parent=mocker.ANY),
            # create order should differ
            mocker.call.m3().create(),
            mocker.call.m1().create(),
            mocker.call.m2().create(),
        ]
    )


@pytest.mark.parametrize("mods", ["", "stubs", "template", "reqs", "dev-reqs", "all"])
class TestProject:
    def test_create(self, test_project, mock_checks, mods, utils):
        test_proj, _ = next(test_project(mods))
        assert test_proj.config.get("name") == "NewProject"
        resp = test_proj.create()
        assert str(resp) == utils.str_path(test_proj.path)
        assert test_proj.exists
        assert test_proj.info_path.exists()
        if test_proj._children:
            test_proj.remove(type(test_proj._children[-1]))

    def test_config(self, test_project, get_config, mods, utils):
        test_proj, mp = next(test_project(mods))
        expect_config = get_config(mods, stubs=list(mp.stubs)[:2])
        assert test_proj.config._config == {"name": "NewProject"}
        test_proj.create()
        assert utils.dict_equal(test_proj.config.raw(), expect_config)
        # should be the same post-load
        test_proj.load()
        assert utils.dict_equal(test_proj.config.raw(), expect_config)

    def test_context(self, test_project, get_context, mods, tmp_path, utils):
        proj_path = tmp_path / "tmpprojpath"
        test_proj, mp = next(test_project(mods, path=proj_path))
        test_proj.create()
        pkg_path = test_proj.data_path / test_proj.name
        expect_context = get_context(
            mods, stubs=mp.stubs, pkg_path=pkg_path, data_dir=test_proj.data_path
        )
        assert utils.dict_equal(test_proj.context.raw(), expect_context)
        test_proj.load()  # should be the same post load
        assert utils.dict_equal(test_proj.context.raw(), expect_context)

    def test_load(self, mock_pkg, tmp_project, mock_checks, test_project, mods, utils):
        proj, mp = next(test_project(mods, path=tmp_project))
        proj.load(run_checks=mp.RUN_CHECKS)

    def test_update(self, mock_pkg, tmp_project, mock_checks, test_project, mods, utils):
        proj, mp = next(test_project(mods, path=tmp_project))
        proj.update()


class TestStubsModule:
    @pytest.fixture()
    def stub_module(self, mocker, tmp_path, micropy_stubs):
        mp = micropy_stubs()
        parent_mock = mocker.MagicMock()
        parent_mock.data_path = tmp_path / ".micropy"
        stub_item = list(mp.stubs)[0]
        stub_mod = modules.StubsModule(
            mp.stubs, stubs=[stub_item], parent=parent_mock, log=mocker.Mock()
        )
        return stub_mod, mp

    def test_load(self, tmp_project, stub_module, get_stub_paths):
        custom_stub = next(get_stub_paths())
        stub_mod, mp = stub_module
        stub_data = {
            "esp32-micropython-1.11.0": "1.2.0",
            "esp8266-micropython-1.11.0": "1.2.0",
            "custom-stub": str(custom_stub),
        }
        stub_mod.parent.config.get.return_value = stub_data
        stub_mod.stub_manager.add.return_value = mp.stubs
        assert stub_mod.load(stub_data=stub_data)

    def test_add_stub(self, test_project, get_stub_paths, mocker):
        proj, mp = next(test_project("stubs"))
        proj.create()
        mocker.patch.object(config.config.dpath, "merge")
        stub_path = next(get_stub_paths())
        stub = mocker.MagicMock()
        stub.path = stub_path
        stub.frozen = stub_path / "frozen"
        stub.stubs = stub_path / "stubs"
        stub.firmware = stub
        proj.add_stub(stub)
        print(proj.stubs)


class TestPackagesModule:
    @pytest.fixture
    def test_package(self, mocker, tmp_path, mock_pkg, test_project):
        new_path = tmp_path / "somepath"
        proj, mp = next(test_project("reqs", path=new_path))
        proj.create()
        return proj

    @pytest.mark.flaky
    def test_add_package(self, test_project, mock_pkg, tmp_path):
        proj, mp = next(test_project("reqs"))
        proj.create()
        proj.add_package("somepkg==7")
        # Shouldnt allow duplicate pkgs
        res = proj.add_package("somepkg")
        assert res is None

    @pytest.mark.flaky()
    def test_add_local_package(self, test_project, tmp_path, utils):
        proj, mp = next(test_project("reqs"))
        pkg = tmp_path / "custompkg"
        pkg.mkdir(parents=True)
        # Add from path
        proj.add_package(f"-e {pkg}")

    def test_package_error(self, test_project, mock_pkg, mocker, tmp_path, caplog):
        packages.source_package.utils.ensure_valid_url.side_effect = [RequestException]
        path = tmp_path / "newdir"
        proj, mp = next(test_project("reqs", path=path))
        proj.create()
        with pytest.raises(RequirementException):
            pkgs = proj.add_package("newpackage")
            assert proj.config.get("packages/newpackage", None) is None
            assert "newpackage" not in pkgs.keys()

    def test_add_dev_package(self, mocker, mock_pkg, test_project):
        proj, mp = next(test_project("reqs,dev-reqs"))
        proj.create()
        proj.add_package("somepkg")
        proj.add_package("anotha_pkg", dev=True)
