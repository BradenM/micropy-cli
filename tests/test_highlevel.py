# -*- coding: utf-8 -*-

import json
from pathlib import Path

import pytest
import requests

from micropy import main, project


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
                "sha256sum": "7ff2cce0237268cd52164b77b6c2df6be6249a67ee285edc122960af869b8ed2"
            },
        ]
    }
    requests_mock.get(
        "https://raw.githubusercontent.com/BradenM/micropy-stubs/master/source.json",
        json=mock_source)
    requests_mock.get(
        "https://codeload.github.com/BradenM/micropy-stubs/legacy.tar.gz/pkg/micropython",
        content=test_archive)


@pytest.mark.usefixtures("mock_cwd", "mock_pkg", "mock_requests")
@pytest.mark.incremental
class TestCreateProject:
    mp = None

    expect_mp_data = {
        'name': 'NewProject',
        'stubs': {
            'esp32-1.11.0': '1.2.0'
        },
        'packages': {},
        'dev-packages': {
            'micropy-cli': '*'
        },
        'config': {
            'vscode': True,
            'pylint': True
        }
    }

    expect_vsc_data = [
        str(Path(".micropy/esp32_test_stub/frozen")),
        str(Path(".micropy/esp32_test_stub/stubs")),
        str(Path(".micropy/NewProject"))
    ]

    def check_mp_data(self, path):
        micropy_file = path
        assert micropy_file.exists()
        mp_data = json.loads(micropy_file.read_text())
        assert mp_data.items() == self.expect_mp_data.items()

    def check_vscode(self, path):
        vsc_path = path
        assert vsc_path.exists()
        with vsc_path.open() as f:
            lines = [l.strip() for l in f.readlines() if l]
            valid = [l for l in lines if "//" not in l[:2]]
        vsc_data = json.loads("\n".join(valid))
        assert vsc_data['python.analysis.typeshedPaths'] == self.expect_vsc_data

    def test_setup_stubs(self, mock_micropy, get_stub_paths, shared_datadir):
        mpy = mock_micropy
        stub_path = (shared_datadir / 'esp32_test_stub')
        mpy.stubs.add(stub_path)

    def test_create_project(self, mock_micropy, tmp_path, shared_datadir):
        mpy = mock_micropy
        stub_path = (shared_datadir / 'esp32_test_stub')
        mpy.stubs.add(stub_path)
        proj_path = (tmp_path / 'NewProject')
        self.proj = project.Project(proj_path)
        proj_stub = list(mpy.stubs)[0]
        self.proj.add(project.modules.StubsModule, mpy.stubs, stubs=[proj_stub])
        self.proj.add(project.modules.PackagesModule, 'requirements.txt')
        self.proj.add(project.modules.DevPackagesModule, 'dev-requirements.txt')
        self.proj.add(project.modules.TemplatesModule, ('vscode', 'pylint'))
        self.proj.create()
        self.check_mp_data(self.proj.info_path)
        self.check_vscode(self.proj.path / '.vscode' / 'settings.json')
        # Reload micropy project and check again
        self.proj = mpy.resolve_project(self.proj.path)
        self.check_mp_data(self.proj.info_path)
        self.check_vscode(self.proj.path / '.vscode' / 'settings.json')
