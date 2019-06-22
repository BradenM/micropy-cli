# -*- coding: utf-8 -*-

import pytest
from micropy.utils import Validator
from jsonschema import ValidationError


@pytest.fixture
def schema(datadir):
    file = datadir / 'schema.json'
    pass_file = datadir / 'pass.json'
    fail_file = datadir / 'fail.json'
    return (file, pass_file, fail_file)


@pytest.mark.validator
def test_validate(schema):
    """Test for successful validation"""
    schema, pass_file, _ = schema
    val = Validator(schema_path=schema)
    val.validate(pass_file)


@pytest.mark.validator
def test_fail_validate(schema):
    """Test for invalid file"""
    schema, _, fail_file = schema
    val = Validator(schema_path=schema)
    with pytest.raises(ValidationError):
        val.validate(fail_file)
