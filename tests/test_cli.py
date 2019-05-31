# -*- coding: utf-8 -*-

import pytest
from click.testing import CliRunner
from micropy import main as cli
from pathlib import Path


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_init(mock_micropy, mock_prompt,  runner):
    """Test micropy init"""
    result = runner.invoke(cli.init, ['NewProject'])
    assert result.exit_code == 0


def test_stub_add(fs_micropy, mock_micropy, runner):
    """Test micropy stub add"""
    stub_path = Path('/foo/bar/foobar_stub')
    fs_micropy.create_dir(stub_path)
    result = runner.invoke(cli.add, [str(stub_path)])
    assert result.exit_code == 0