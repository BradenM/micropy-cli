import pytest
from micropy import stubs

micropy_source = stubs.repository_info.RepositoryInfo(
    name="BradenM/micropy-stubs",
    display_name="micropy-stubs",
    source="https://raw.githubusercontent.com/BradenM/micropy-stubs/master/source.json",
)

micropython_source = stubs.repository_info.RepositoryInfo(
    name="Josverl/micropython-stubs",
    display_name="micropython-stubs",
    source="https://raw.githubusercontent.com/Josverl/micropython-stubs/main/publish/package_data.jsondb",
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
def repo(mock_manifests):
    repo = stubs.repo.StubRepository()
    repo = repo.add_repository(micropy_source)
    repo = repo.add_repository(micropython_source)
    return repo


def test_repo_inits(repo):
    assert len(repo.manifests) == 2
    assert len(repo.packages) == 3


@pytest.mark.parametrize(
    "query,expect_name",
    [
        ("esp32", ["micropython-esp32-stubs@1.18.post1"]),
        ("EsP32", ["micropython-esp32-stubs@1.18.post1"]),
        ("8266", ["esp8266-micropython-1.15.0"]),
        (
            "micropython",
            ["micropython-esp32-stubs@1.18.post1", "micropython", "esp8266-micropython-1.15.0"],
        ),
    ],
)
def test_repo_search(repo, query, expect_name):
    results = repo.search(query)
    names = [i.package.package_name for i in results]
    assert sorted(names) == sorted(expect_name)
