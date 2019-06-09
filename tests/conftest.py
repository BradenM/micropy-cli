# -*- coding: utf-8 -*-
""" Common Pytest Fixtures"""

import pytest
import micropy
import questionary


@pytest.fixture
def mock_prompt(monkeypatch):
    def mock_prompt(*args, **kwargs):
        class prompt_mock:
            def __init__(self, *args, **kwargs):
                return None

            def ask(self):
                return ['stub']
        return prompt_mock(*args, **kwargs)
    monkeypatch.setattr(questionary, 'checkbox', mock_prompt)


@pytest.fixture
def mock_micropy_path(monkeypatch, tmp_path):
    path = tmp_path / '.micropy'
    stub_path = path / 'stubs'
    log_path = path / 'micropy.log'
    monkeypatch.setattr(micropy.logger.ServiceLog, 'LOG_FILE', log_path)
    monkeypatch.setattr(micropy.main.MicroPy, 'FILES', path)
    monkeypatch.setattr(micropy.main.MicroPy, 'STUB_DIR', stub_path)
    return path


@pytest.fixture
def mock_micropy(mock_micropy_path):
    mp = micropy.main.MicroPy()
    return mp
