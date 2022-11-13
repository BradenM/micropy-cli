import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest
from micropy import project


@pytest.fixture
def mock_requests(mocker, requests_mock, test_archive):
    mock_source = {
        "name": "Micropy Stubs",
        "location": "https://codeload.github.com/BradenM/micropy-stubs",
        "source": "https://raw.githubusercontent.com/bradenm/micropy-stubs/source.json",
        "path": "legacy.tar.gz/pkg/",
        "packages": [
            {
                "name": "micropython",
                "type": "firmware",
                "sha256sum": "7ff2cce0237268cd52164b77b6c2df6be6249a67ee285edc122960af869b8ed2",
            },
        ],
    }
    requests_mock.get(
        "https://raw.githubusercontent.com/BradenM/micropy-stubs/master/source.json",
        json=mock_source,
    )
    requests_mock.get(
        "https://codeload.github.com/BradenM/micropy-stubs/legacy.tar.gz/pkg/micropython",
        content=test_archive,
    )


@pytest.mark.skip(reason="Tests need some serious cleanup before something like this could work.")
@pytest.mark.usefixtures("mock_requests")
class TestCreateProject:
    mp = None

    expect_mp_data = staticmethod(
        lambda name: {
            "name": "NewProject",
            "stubs": {name: "1.2.0"},
            "packages": {},
            "dev-packages": {"micropy-cli": "*"},
            "config": {"vscode": True, "pylint": True},
        }
    )

    expect_vsc_data = staticmethod(
        lambda name: [
            str(Path(f".micropy/{name}/frozen")),
            str(Path(".micropy/fware_test_stub/frozen")),
            str(Path(f".micropy/{name}/stubs")),
            str(Path(".micropy/NewProject")),
        ]
    )

    def build_project(self, mpy, path):
        proj_path = path / "highlevel_new_project"
        if proj_path.exists():
            shutil.rmtree(proj_path, ignore_errors=True)
        proj = project.Project(proj_path)
        proj_stub = list(mpy.stubs)[0]
        proj.add(project.modules.StubsModule, mpy.stubs, stubs=[proj_stub])
        proj.add(project.modules.PackagesModule, "requirements.txt")
        proj.add(project.modules.DevPackagesModule, "dev-requirements.txt")
        proj.add(project.modules.TemplatesModule, ("vscode", "pylint"))
        return (proj, mpy, proj_stub)

    def check_mp_data(self, path, utils, name="esp32", expect=None):
        expect_data = expect or self.expect_mp_data(name)
        micropy_file = path
        assert micropy_file.exists()
        mp_data = json.loads(micropy_file.read_text())
        assert utils.dict_equal(mp_data, expect_data)

    def check_vscode(self, path, name="esp32", expect=None):
        vsc_path = path / ".vscode" / "settings.json"
        assert vsc_path.exists()
        with vsc_path.open() as f:
            lines = [l.strip() for l in f.readlines() if l]
            valid = [l for l in lines if "//" not in l[:2]]
        vsc_data = json.loads("\n".join(valid))
        expect_data = expect or self.expect_vsc_data(name)
        assert vsc_data["python.analysis.typeshedPaths"] == expect_data

    def test_setup_stubs(self, mock_micropy, get_stub_paths, shared_datadir):
        mpy = mock_micropy
        stub_path = shared_datadir / "esp32_test_stub"
        mpy.stubs.add(stub_path)

    def test_create_project(self, micropy_stubs, tmp_path, utils):
        proj, mpy, proj_stub = self.build_project(micropy_stubs(), tmp_path)
        proj.create()
        self.check_mp_data(proj.info_path, utils, name=proj_stub.path.name)
        self.check_vscode(proj.path, name=proj_stub.path.name)

    def test_add_package(self, mock_pkg, micropy_stubs, tmp_path, utils):
        proj, mpy, proj_stub = self.build_project(micropy_stubs(), tmp_path)
        proj.create()
        proj.add_package("newpackage")
        expect_data = deepcopy(self.expect_mp_data(proj_stub.path.name))
        expect_data["packages"]["newpackage"] = "*"
        self.check_mp_data(proj.info_path, utils, expect=expect_data)

    @pytest.mark.parametrize("local_pkg", ["src/lib/coolpackage", "/tmp/absolute/package"])
    def test_add_local_package(self, tmp_path, local_pkg, micropy_stubs, utils):
        proj, mpy, proj_stub = self.build_project(micropy_stubs(), tmp_path)
        proj.create()
        local_package = Path(local_pkg)
        if not local_package.is_absolute():
            local_package = proj.path / Path(local_pkg)
        local_package.mkdir(parents=True, exist_ok=True)
        (local_package / "__init__.py").touch()
        local_path = utils.str_path(local_pkg)
        proj.add_package(f"-e {local_path}")
        # check micropy.json
        expect_data = deepcopy(self.expect_mp_data(proj_stub.path.name))
        expect_data["packages"][local_package.name] = f"-e {local_path}"
        self.check_mp_data(proj.info_path, utils, expect=expect_data)
        # check vscode settings
        expect_vscode = deepcopy(self.expect_vsc_data(proj_stub.path.name))
        expect_vscode.append(local_path)
        self.check_vscode(proj.path, expect=expect_vscode)
        shutil.rmtree(proj.path)
