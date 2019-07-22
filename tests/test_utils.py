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
    results = utils.search_xml(u['valid'], "Key")
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
    result = utils.get_package_meta("foobar", spec="0.0.0")
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
