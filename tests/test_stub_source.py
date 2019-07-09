# -*- coding: utf-8 -*-

import pytest

from micropy.exceptions import StubError
from micropy.stubs import source


@pytest.fixture
def test_repo(test_urls, mocker):
    mocker.patch.object(source.utils, "is_downloadable",
                        return_value=True)
    repo = source.StubRepo("TestRepo", test_urls['valid'], "/packages")
    return repo


def test_get_source(shared_datadir, test_urls, test_repo):
    """should return correct subclass"""
    test_path = shared_datadir / 'esp8266_test_stub'
    local_stub = source.get_source(test_path)
    assert isinstance(local_stub, source.LocalStubSource)
    remote_stub = source.get_source('esp8266-test-stub')
    assert isinstance(remote_stub, source.RemoteStubSource)
    stub_source = source.get_source(test_urls['valid'])
    print(str(stub_source))
    assert str(stub_source) == f"<RemoteStubSource@{stub_source.location}>"


def test_source_ready(shared_datadir, test_urls, tmp_path, mocker,
                      test_archive, test_repo):
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
        assert str(source_path) == str(expected_path)


def test_repo_from_json(shared_datadir, mocker):
    mocker.patch.object(source.utils, "ensure_valid_url",
                        return_value="https://testsource.com")
    test_sources = shared_datadir / 'test_sources.json'
    content = test_sources.read_text()
    repos = source.StubRepo.from_json(content)
    assert repos[0].name == "Test Repo"
    assert len(repos) == 1


def test_repo_resolve_pkg(mocker, test_urls):
    url = test_urls['valid']
    mocker.patch.object(source.utils, "ensure_valid_url",
                        return_value=url)
    mocker.patch.object(source.utils, "is_downloadable",
                        return_value=False)
    source.StubRepo("TestRepo", url, "packages")
    with pytest.raises(StubError):
        source.StubRepo.resolve_package("not-valid")
