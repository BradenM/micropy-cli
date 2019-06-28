# -*- coding: utf-8 -*-

import pytest

from micropy.stubs import source


@pytest.yield_fixture
def test_archive(shared_datadir):
    archive = shared_datadir / 'archive_test_stub.tar.gz'
    file_obj = archive.open('rb')
    file_bytes = file_obj.read()
    yield file_bytes
    file_obj.close()


def test_get_source(shared_datadir, test_urls):
    """should return correct subclass"""
    test_path = shared_datadir / 'esp8266_test_stub'
    local_stub = source.get_source(test_path)
    assert isinstance(local_stub, source.LocalStubSource)
    remote_stub = source.get_source(test_urls['valid'])
    assert isinstance(remote_stub, source.RemoteStubSource)


def test_source_ready(shared_datadir, test_urls, tmp_path, mocker,
                      test_archive):
    """should prepare and resolve stub"""
    # Test LocalStub ready
    test_path = shared_datadir / 'esp8266_test_stub'
    local_stub = source.get_source(test_path)
    expected_path = local_stub.location.resolve()
    with local_stub.ready() as source_path:
        assert source_path == expected_path

    # Setup RemoteStub
    test_parent = tmp_path / 'tmpdir'
    test_parent.mkdir()
    expected_path = (test_parent / 'archive_test_stub').resolve()
    mocker.patch.object(source.utils, "ensure_valid_url",
                        return_value=test_urls['download'])
    mocker.patch.object(source.tempfile, "mkdtemp", return_value=test_parent)
    get_mock = mocker.patch.object(source.requests, "get")
    content_mock_val = mocker.PropertyMock(return_value=test_archive)
    type(get_mock.return_value).content = content_mock_val
    # Test Remote Stub
    remote_stub = source.get_source(test_urls['download'])
    with remote_stub.ready() as source_path:
        print(list(source_path.parent.iterdir()))
        assert source_path.exists()
        assert str(source_path) == str(expected_path)
