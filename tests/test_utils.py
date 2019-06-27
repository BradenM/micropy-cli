# -*- coding: utf-8 -*-

import pytest
import requests
from jsonschema import ValidationError
from requests.exceptions import ConnectionError, HTTPError, InvalidURL

from micropy import utils

test_urls = {
    "valid": "http://www.google.com",
    "valid_https": "https://www.google.com",
    "invalid": "/foobar/bar/foo",
    "invalid_file": "file:///foobar/bar/foo",
    "bad_resp": "http://www.google.com/XYZ/ABC/BADRESP"
}


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


def test_is_url():
    """should respond true/false for url"""
    u = test_urls
    assert utils.is_url(u['valid'])
    assert utils.is_url(u['valid_https'])
    assert not utils.is_url(u['invalid'])
    assert not utils.is_url(u['invalid_file'])


def test_ensure_valid_url(mocker):
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
