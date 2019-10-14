# -*- coding: utf-8 -*-


import io

import pytest
import requests
from jsonschema import ValidationError
from requests.exceptions import ConnectionError, HTTPError, InvalidURL

from micropy import utils


@pytest.fixture
def schema(datadir):
    file = datadir / 'schema.json'
    pass_file = datadir / 'pass.json'
    fail_file = datadir / 'fail.json'
    return (file, pass_file, fail_file)


def test_validate(schema):
    """Test for successful validation"""
    schema, pass_file, _ = schema
    val = utils.Validator(schema_path=schema)
    val.validate(pass_file)


def test_fail_validate(schema):
    """Test for invalid file"""
    schema, _, fail_file = schema
    val = utils.Validator(schema_path=schema)
    with pytest.raises(ValidationError):
        val.validate(fail_file)


def test_is_url(test_urls):
    """should respond true/false for url"""
    u = test_urls
    assert utils.is_url(u['valid'])
    assert utils.is_url(u['valid_https'])
    assert not utils.is_url(u['invalid'])
    assert not utils.is_url(u['invalid_file'])


def test_ensure_valid_url(mocker, test_urls):
    """should ensure url is valid"""
    u = test_urls
    with pytest.raises(InvalidURL):
        utils.ensure_valid_url(test_urls['invalid'])
    with pytest.raises(ConnectionError):
        mocker.patch.object(utils, "is_url", return_value=True)
        mock_head = mocker.patch.object(requests, "head")
        mock_head.side_effect = [ConnectionError]
        utils.ensure_valid_url(u['valid'])
    mocker.stopall()
    with pytest.raises(HTTPError):
        utils.ensure_valid_url(u['bad_resp'])
    result = utils.ensure_valid_url(u['valid'])
    assert result == u['valid']


def test_ensure_existing_dir(tmp_path):
    """should ensure dir exists"""
    not_exist = tmp_path / 'i_dont_exist'
    file = tmp_path / 'file.txt'
    file.touch()
    with pytest.raises(NotADirectoryError):
        utils.ensure_existing_dir(not_exist)
    with pytest.raises(NotADirectoryError):
        utils.ensure_existing_dir(file)
    result = utils.ensure_existing_dir(str(tmp_path))
    assert result == tmp_path
    assert result.exists()
    assert result.is_dir()


def test_is_downloadable(mocker, test_urls):
    """should check if url can be downloaded from"""
    u = test_urls
    uheaders = u["headers"]
    mock_head = mocker.patch.object(requests, "head")
    head_mock_val = mocker.PropertyMock(
        side_effect=[uheaders["not_download"],
                     uheaders["can_download"]])
    type(mock_head.return_value).headers = head_mock_val
    assert not utils.is_downloadable(u["valid"])
    assert not utils.is_downloadable("not-a-real-url")
    assert utils.is_downloadable(u["valid"])


def test_get_url_filename(test_urls):
    """should return filename"""
    filename = "archive_test_stub.tar.gz"
    result = utils.get_url_filename(test_urls["download"])
    assert result == filename


def test_is_existing_dir(tmp_path):
    bad_path = tmp_path / 'not-real-path'
    is_file = tmp_path / 'file.txt'
    is_file.touch()
    assert not utils.is_existing_dir(bad_path)
    assert not utils.is_existing_dir(is_file)
    assert utils.is_existing_dir(tmp_path)


def test_search_xml(mocker, shared_datadir, test_urls):
    u = test_urls
    test_xml = shared_datadir / 'test_source.xml'
    mock_get = mocker.patch.object(requests, 'get')
    with test_xml.open('rb') as f:
        type(mock_get.return_value).content = f.read()
    results = utils.search_xml(u['valid'], "Key", ignore_cache=True)
    assert sorted(results) == sorted([
        "packages/esp32-micropython-1.10.0.tar.gz",
        "packages/esp32-micropython-1.11.0.tar.gz"
    ])


def test_generate_stub(shared_datadir, tmp_path, mocker):
    mock_stubber = mocker.patch.object(
        utils.helpers.stubgen, 'StandAloneMakeStubFile').return_value
    expect_path = tmp_path / 'foo.py'
    expect_path.touch()
    result = utils.generate_stub(expect_path)
    mock_stubber.run.assert_called_once()
    assert result == (expect_path, expect_path.with_suffix('.pyi'))
    # Test print monkeypatch
    print_mock = mocker.Mock(return_value=None)
    result = utils.generate_stub(expect_path, log_func=print_mock)
    utils.helpers.stubgen.print("hi")
    assert print_mock.call_count >= 1


def test_get_package_meta(mocker):
    """should get package meta"""
    mock_req = mocker.patch.object(utils.helpers, 'requests')
    mock_data = {
        "releases": {
            "0.0.0": [
                {
                    "url": "early-version.tar.gz"
                }
            ],
            "0.1.0":  [
                {
                    "url": "do-not-return-me",
                },
                {
                    "url": "return-me.tar.gz"
                }
            ],
        }
    }
    mock_req.get.return_value.json.return_value = mock_data
    result = utils.get_package_meta("foobar")
    assert result == {
        "url": "return-me.tar.gz"
    }
    mock_req.get.assert_called_once_with("https://pypi.org/pypi/foobar/json")
    result = utils.get_package_meta("foobar", spec="==0.0.0")
    assert result == {
        "url": "early-version.tar.gz"
    }


def test_extract_tarbytes(mocker):
    """should extract tar file from memory"""
    test_bytes = bytearray("foobar", "utf-8")
    mock_io = mocker.patch.object(utils.helpers.io, "BytesIO")
    mock_io.return_value = io.BytesIO(test_bytes)
    mock_tarfile = mocker.patch.object(utils.helpers, 'tarfile')
    mock_tar = mock_tarfile.open.return_value.__enter__.return_value
    utils.extract_tarbytes(test_bytes, "foobar")
    mock_tarfile.open.assert_called_once_with(
        fileobj=io.BytesIO(test_bytes), mode="r:gz")
    mock_tar.extractall.assert_called_once_with("foobar")


def test_iter_requirements(mocker, tmp_path):
    """should iter requirements"""
    tmp_file = tmp_path / 'tmp_reqs.txt'
    tmp_file.touch()
    tmp_file.write_text("micropy-cli==1.0.0")
    result = next(utils.iter_requirements(tmp_file))
    assert result.name == "micropy-cli"
    assert result.specs == [('==', "1.0.0")]


def test_create_dir_link(mocker, tmp_path):
    """Should create a symlink or directory junction if needed"""
    targ_path = tmp_path / 'target_dir'
    targ_path.mkdir()
    link_path = tmp_path / 'link_path'
    mock_sys = mocker.patch.object(utils.helpers, 'sys')
    mock_platform = type(mock_sys).platform = mocker.PropertyMock()
    mock_subproc = mocker.patch.object(utils.helpers, 'subproc')
    mock_path = mocker.patch.object(utils.helpers, 'Path').return_value
    mock_path.symlink_to.side_effect = [mocker.ANY, OSError, OSError, OSError]

    mock_platform.return_value = 'linux'
    # Test POSIX (should not raise exception)
    utils.create_dir_link(link_path, targ_path)
    mock_path.symlink_to.assert_called_once()
    assert mock_subproc.call_count == 0
    # Test POSIX failed for unknown reason
    with pytest.raises(OSError):
        utils.create_dir_link(link_path, targ_path)
    # Test Windows (should try to make symlink, fallback on DJ)
    mock_platform.return_value = 'win32'
    mock_subproc.call.return_value = 0
    utils.create_dir_link(link_path, targ_path)
    assert mock_subproc.call.call_count == 1
    # Test Windows fails for some reason
    mock_subproc.call.return_value = 1
    with pytest.raises(OSError):
        utils.create_dir_link(link_path, targ_path)


def test_is_dir_link(mocker, tmp_path):
    """Should test if a path is a symlink or directory junction"""
    link_path = tmp_path / 'link'
    targ_path = tmp_path / 'target'
    mock_sys = mocker.patch.object(utils.helpers, 'sys')
    mock_platform = type(mock_sys).platform = mocker.PropertyMock()
    mock_path = mocker.patch.object(utils.helpers, 'Path').return_value
    mock_path.is_symlink.side_effect = [True, False, False, False]
    # Test Symlink (POSIX)
    mock_platform.return_value = 'linux'
    assert utils.is_dir_link(link_path)
    assert not utils.is_dir_link(link_path)
    # Test Directory Junction (Windows)
    mock_platform.return_value = 'win32'
    # From what I can tell, while Path.is_symlink always returns false for DJs.
    # However, on a DJ, Path.absolute will return the absolute path to the DJ,
    # while Path.resolve will return the absolute path to the source directory.
    # With this in mind, this check SHOULD work.
    mock_path.resolve.return_value = targ_path
    mock_path.absolute.return_value = link_path
    assert utils.is_dir_link(link_path)
    mock_path.absolute.return_value = targ_path
    assert not utils.is_dir_link(link_path)


def test_is_update_available(mocker):
    """Test self-update check method"""
    mock_req = mocker.patch.object(utils.helpers, 'requests')
    mocker.patch('micropy.__version__', '0.0.0')
    mock_req.get.return_value.json.return_value = {'releases': {'1.0.0': []}}
    utils.helpers.get_cached_data.clear_cache()
    assert utils.helpers.is_update_available() == '1.0.0'
    mocker.patch('micropy.__version__', '2.0.0')
    utils.helpers.get_cached_data.clear_cache()
    assert not utils.helpers.is_update_available()


def test_stream_download(mocker):
    """Test stream download"""
    mock_req = mocker.patch.object(utils.helpers, 'requests')
    mock_stream = mocker.MagicMock()
    mock_stream.headers = {
        'content-length': '1000'
    }
    mock_req.get.return_value = mock_stream
    tqdm_mock = mocker.patch.object(utils.helpers, 'tqdm')
    utils.stream_download("https://someurl.com/file.ext")
    expect_args = {
        'unit_scale': True,
        'unit_divisor': 1024,
        'smoothing': 0.1,
        'bar_format': mocker.ANY
    }
    tqdm_mock.assert_called_once_with(total=1000, unit='B', **expect_args)
