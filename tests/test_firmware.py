# -*- coding: utf-8 -*-

import pytest
from micropy.stubs import Stub, firmware


def test_firmware_by_name(mock_micropy):
    """Test Firmware by name"""
    fware = firmware.Firmware("micropython", tag="1.11.0", port="esp32")
    assert fware.name == "MicroPython Official"
    assert fware.repo == "micropython/micropython"
    assert fware.tag == "1.11.0"
    assert fware.port == "esp32"
    assert fware.module_path == "ports/esp32/modules"


def test_known_firmware_from_stub(mock_micropy, shared_datadir):
    """Tests retrieving firmware from stub"""
    stub_path = shared_datadir / 'esp8266_firmknown_stub'
    stub = Stub(stub_path)
    fware = firmware.Firmware.from_stub(stub, name="micropython")
    assert fware.name == "MicroPython Official"
    assert fware.repo == "micropython/micropython"
    assert fware.tag == "1.9.4"
    assert fware.port == "esp8266"
    assert fware.module_path == "ports/esp8266/modules"


def test_retrieve_modules(mock_micropy, tmp_path):
    """Test module retrieval"""
    fware = firmware.Firmware("micropython", port="esp32", tag="1.9.4")
    modules = fware.retrieve_modules(tmp_path),
    assert len(modules) >= 0
    expected_files = [
        "umqtt/robust.py",
        "umqtt/simple.py",
        "apa106.py",
        "dht.py",
        "neopixel.py"
    ]
    excluded_files = [
        "_boot.py",
        "inisetup.py"
    ]
    paths = [str(i) for i in modules.iterdir()]
    assert len(paths) == len(modules)
    assert expected_files in paths
    assert excluded_files not in paths
