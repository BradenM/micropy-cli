from micropy.stubs import source

from tests.test_stubs_repo import stub_repo  # noqa


def test_stub_info_spec_locator(shared_datadir):
    test_path = shared_datadir / "esp8266_test_stub"
    assert source.StubInfoSpecLocator().prepare(test_path) == test_path.absolute()


def test_stub_info_spec_locator__returns_location_on_fail(tmp_path):
    assert source.StubInfoSpecLocator().prepare(tmp_path) == tmp_path


def test_source_ready(shared_datadir, test_urls, tmp_path, mocker, test_archive):
    """should prepare and resolve stub"""
    # Test LocalStub ready
    test_path = shared_datadir / "esp8266_test_stub"
    local_stub = source.get_source(test_path)
    expected_path = local_stub.location.resolve()
    with local_stub.ready() as source_path:
        assert source_path == expected_path

    # Setup RemoteStub
    test_parent = tmp_path / "tmpdir"
    test_parent.mkdir()
    expected_path = (test_parent / "archive_test_stub").resolve()
    mocker.patch.object(source.tempfile, "mkdtemp", return_value=test_parent)
    mocker.patch.object(source.utils, "stream_download", return_value=test_archive)
    # Test Remote Stub
    remote_stub = source.get_source(test_urls["download"])
    with remote_stub.ready() as source_path:
        print(list(source_path.parent.iterdir()))
        assert (source_path / "info.json").exists()
        assert len(list(source_path.iterdir())) == 3


def test_stub_repo_locator(stub_repo):
    locator = source.RepoStubLocator(stub_repo)
    assert locator.prepare("stub1-foo") == "https://test-manifest/stub1-foo"
