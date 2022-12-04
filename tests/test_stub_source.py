from micropy.stubs import source


def test_get_source(shared_datadir, test_urls, test_repo):
    """should return correct subclass"""
    test_path = shared_datadir / "esp8266_test_stub"
    local_stub = source.get_source(test_path)
    assert isinstance(local_stub, source.LocalStubSource)
    remote_stub = source.get_source("esp8266-test-stub")
    assert isinstance(remote_stub, source.RemoteStubSource)
    stub_source = source.get_source(test_urls["valid"])
    print(str(stub_source))
    assert str(stub_source) == f"<RemoteStubSource@{stub_source.location}>"


def test_source_ready(shared_datadir, test_urls, tmp_path, mocker, test_archive, test_repo):
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
