import pytest
from micropy.stubs import RepositoryInfo, StubPackage, StubRepository, StubsManifest


class ManifestStub(StubsManifest[StubPackage]):
    def resolve_package_url(self, package: StubPackage) -> str:
        return f"https://test-manifest/{package.name}"


Test1Manifest = ManifestStub(
    repository=RepositoryInfo(
        name="Test", display_name="Test Display", source="https://test-manifest.com"
    ),
    packages=frozenset(
        [
            StubPackage(name="stub1-foo", version="1.0.0"),
            StubPackage(name="stub1-foo", version="1.1.0"),
            StubPackage(name="stub1-foo", version="2.0.0"),
            StubPackage(name="stub2-bar", version="2.0.0"),
        ]
    ),
)

Test2Manifest = ManifestStub(
    repository=RepositoryInfo(
        name="Test2", display_name="Test Display2", source="https://test2-manifest.com"
    ),
    packages=frozenset(
        [
            StubPackage(name="stub3-thing", version="3.0.0"),
            StubPackage(name="stub3-thing", version="3.1.0"),
            StubPackage(name="stub4-device", version="4.0.0"),
        ]
    ),
)


@pytest.fixture
def stub_repo():
    repo = StubRepository(manifests=[Test1Manifest, Test2Manifest])
    return repo


def test_repo_inits(stub_repo):
    assert len(stub_repo.manifests) == 2
    assert len(list(stub_repo.packages)) == 7


@pytest.mark.parametrize(
    "query,expect_name,include_versions",
    [
        ("stub1", ["Test/stub1-foo-2.0.0"], False),
        ("DEvICE", ["Test2/stub4-device-4.0.0"], False),
        (
            "stub",
            [
                "Test/stub1-foo-2.0.0",
                "Test/stub2-bar-2.0.0",
                "Test2/stub3-thing-3.1.0",
                "Test2/stub4-device-4.0.0",
            ],
            False,
        ),
        (
            "stub",
            [
                "Test/stub1-foo-1.0.0",
                "Test/stub1-foo-1.1.0",
                "Test/stub1-foo-2.0.0",
                "Test/stub2-bar-2.0.0",
                "Test2/stub3-thing-3.0.0",
                "Test2/stub3-thing-3.1.0",
                "Test2/stub4-device-4.0.0",
            ],
            True,
        ),
    ],
)
def test_repo_search(stub_repo, query, expect_name, include_versions):
    results = stub_repo.search(query, include_versions=include_versions)
    names = [i.absolute_versioned_name for i in results]
    print(names)
    assert sorted(names) == sorted(expect_name)
