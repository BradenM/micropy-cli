""" Common Pytest Fixtures"""

import importlib
import shutil
from pathlib import Path
from pprint import PrettyPrinter

import micropy
import pytest
import questionary
from boltons import iterutils

# Mock values for Template VSCode ext checks
mock_vscode_exts = [
    "mock.ext@0.0.0",
    # meets req
    "ms-python.python@2019.9.34474",
]


def pytest_collection_modifyitems(items):
    items.reverse()


@pytest.fixture(autouse=True)
def cleanup_data(mocker):
    mocker.resetall()
    try:
        micropy.utils.ensure_valid_url.clear_cache()
    except Exception:
        importlib.reload(micropy)


@pytest.fixture
def mock_prompt(monkeypatch):
    def mock_prompt(*args, **kwargs):
        class prompt_mock:
            def __init__(self, *args, **kwargs):
                return None

            def ask(self):
                return ["stub"]

        return prompt_mock(*args, **kwargs)

    monkeypatch.setattr(questionary, "checkbox", mock_prompt)


@pytest.fixture
def mock_micropy_path(mocker, tmp_path):
    path = tmp_path / ".micropy"
    stub_path = path / "stubs"
    log_path = path / "micropy.log"
    mocker.patch("micropy.data.FILES", path)
    mocker.patch("micropy.data.STUB_DIR", stub_path)
    mocker.patch("micropy.data.LOG_FILE", log_path)
    return path


@pytest.fixture
def mock_micropy(mock_micropy_path):
    mp = micropy.main.MicroPy()
    return mp


@pytest.fixture
def mock_cwd(request, tmp_path, mocker):
    print(request)
    import pathlib

    mocker.patch("pathlib.Path.cwd")
    pathlib.Path.cwd.return_value = tmp_path
    yield (tmp_path)


@pytest.fixture(scope="session")
def test_urls():
    def test_headers(type):
        return {"content-type": type}

    return {
        "valid": "http://www.google.com",
        "valid_https": "https://www.google.com",
        "invalid": "/foobar/bar/foo",
        "invalid_file": "file:///foobar/bar/foo",
        "bad_resp": "http://www.google.com/XYZ/ABC/BADRESP",
        "download": "https://www.somewebsite.com/archive_test_stub.tar.gz",
        "headers": {
            "can_download": test_headers("application/gzip"),
            "not_download": test_headers("text/plain"),
        },
    }


@pytest.fixture
def get_stub_paths(shared_datadir, tmp_path):
    def _get_stub_paths(count=1, valid=True, firm=False, dest=tmp_path):
        _stubs = ["fware"] if firm else ["esp8266", "esp32"]
        stubs = iter(_stubs)
        _count = 0
        while _count < count:
            s = next(stubs)
            path = (
                (shared_datadir / f"{s}_test_stub")
                if valid
                else (shared_datadir / f"{s}_invalid_stub")
            )
            if path.exists():
                dest = dest / path.name
                if not dest.exists():
                    shutil.copytree(path, (dest / path.name))
                yield dest
                _count += 1

    return _get_stub_paths


@pytest.fixture
def mock_mp_stubs(mock_micropy, mocker, shared_datadir):
    mock_micropy.stubs.add(shared_datadir / "fware_test_stub")
    mock_micropy.stubs.add(shared_datadir / "esp8266_test_stub")
    mock_micropy.stubs.add(shared_datadir / "esp32_test_stub")
    return mock_micropy


@pytest.fixture
def get_stubs(get_stub_paths, mocker, tmp_path):
    def _get_stubs(path=tmp_path, **kwargs):
        def stubbify(m, path, firm=None):
            m.path = path
            m.frozen = path / "frozen"
            m.stubs = path / "stubs"
            m.name = m.path.name
            m.stub_version = "0.0.0"
            m.firmware = firm
            return m

        paths = get_stub_paths(dest=path, **kwargs)
        firm = next(get_stub_paths(firm=True, dest=path))
        firm_mock = stubbify(mocker.MagicMock(), firm)
        for p in paths:
            yield stubbify(mocker.MagicMock(), p, firm=firm_mock)

    return _get_stubs


@pytest.fixture
def micropy_stubs(mocker, get_stubs):
    def _micropy_stubs(count=3):
        def _mock_resolve_subresource(stubs, data_path):
            return get_stubs(path=data_path)

        mock_mp = mocker.patch.object(micropy, "MicroPy").return_value
        stubs = list(get_stubs())
        mock_mp.stubs.__iter__.return_value = stubs
        mock_mp.stubs.resolve_subresource = _mock_resolve_subresource
        mock_mp.stubs.add.return_value = stubs[0]
        return mock_mp

    return _micropy_stubs


@pytest.yield_fixture
def test_archive(shared_datadir):
    archive = shared_datadir / "archive_test_stub.tar.gz"
    file_obj = archive.open("rb")
    file_bytes = file_obj.read()
    yield file_bytes
    file_obj.close()


micropy_source = micropy.stubs.repository_info.RepositoryInfo(
    name="BradenM/micropy-stubs",
    display_name="micropy-stubs",
    source="https://my-mocked-source.com/bradenm",
)

micropython_source = micropy.stubs.repository_info.RepositoryInfo(
    name="Josverl/micropython-stubs",
    display_name="micropython-stubs",
    # source="https://raw.githubusercontent.com/Josverl/micropython-stubs/main/publish/package_data.jsondb",
    source="https://my-mocked-source.com/josverl",
)


@pytest.fixture
def mock_manifests(mocker, requests_mock):
    micropy_manifest = {
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
            {"name": "esp8266-micropython-1.15.0", "type": "device", "sha256sum": "abc123"},
        ],
    }
    micropython_manifest = {
        "version": 2,
        "keys": [
            "description",
            "hash",
            "mpy_version",
            "name",
            "path",
            "pkg_version",
            "publish",
            "stub_hash",
            "stub_sources",
        ],
        "data": {
            "160521968180811532": {
                "name": "micropython-esp32-stubs",
                "mpy_version": "1.18",
                "publish": True,
                "pkg_version": "1.18.post1",
                "path": "publish/micropython-v1_18-esp32-stubs",
                "stub_sources": [
                    ["Firmware stubs", "stubs/micropython-v1_18-esp32"],
                    ["Frozen stubs", "stubs/micropython-v1_18-frozen/esp32/GENERIC"],
                    ["Core Stubs", "stubs/cpython_core-pycopy"],
                ],
                "description": "MicroPython stubs",
                "hash": "712ebd85140b078ce6d9d3cbb9d7ffc18cf10aef",
                "stub_hash": "",
            }
        },
    }

    requests_mock.get(
        micropy_source.source,
        json=micropy_manifest,
    )
    requests_mock.get(
        micropython_source.source,
        json=micropython_manifest,
    )


@pytest.fixture
def mock_checks(mocker):
    """Mock VSCode Template Checks"""
    m_run = mocker.patch.object(micropy.project.checks.subproc, "run").return_value
    type(m_run).stdout = mocker.PropertyMock(return_value="\n".join(mock_vscode_exts))
    return m_run


@pytest.fixture
def mock_pkg(mocker, tmp_path):
    """return mock package"""
    from micropy import packages

    tmp_pkg = tmp_path / "tmp_pkg"
    tmp_pkg.mkdir()
    (tmp_pkg / "module.py").touch()
    (tmp_pkg / "file.py").touch()
    mocker.patch.object(packages.source_package.utils, "ensure_valid_url")
    mock_tarbytes = mocker.patch.object(packages.source_package.utils, "extract_tarbytes")
    mock_meta = mocker.patch.object(packages.source_package.utils, "get_package_meta")
    mocker.patch.object(packages.source_package.utils, "get_url_filename")
    mocker.patch.object(packages.source_package.utils, "stream_download")
    mock_tarbytes.return_value = tmp_pkg
    mock_meta.return_value = {"url": "http://realurl.com"}
    return tmp_pkg


# Pytest Incremental Marker
def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed ({})".format(previousfailed.name))


class AssertUtils:
    pp = PrettyPrinter(indent=4, width=20).pprint

    def dict_match_mocks(self, d1):
        from unittest.mock import Mock

        # Mocks
        remapped = iterutils.remap(
            d1, lambda p, k, v: (k, "MOCKED_VALUE") if isinstance(v, Mock) else True
        )
        return remapped

    def dict_equal(self, d1, d2):
        match_d1 = sorted(self.dict_match_mocks(d1).items())
        match_d2 = sorted(self.dict_match_mocks(d1).items())
        print("== IS DICT EQUAL ==")
        self.pp(match_d1)
        print("\n----------\n")
        self.pp(match_d2)
        print("==============")
        return match_d1 == match_d2

    def list_equal(self, l1, l2):
        list_one = sorted(l1)
        list_two = sorted(l2)
        return list_one == list_two

    def load_json(self, path):
        import json

        return json.loads(path.read_text())

    def json_equal_dict(self, path, d2):
        data = self.load_json(path)
        return self.dict_equal(data, d2)

    def str_path(self, path, absolute=False):
        """x-platform path strings helper"""
        path = Path(path)
        if absolute:
            path = path.absolute()
        return str(path)

    def get_rand_str(self, length=10):
        import random
        import string

        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))


@pytest.fixture
def utils():
    return AssertUtils()
