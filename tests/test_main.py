# -*- coding: utf-8 -*-

from micropy import main


def test_setup(mock_micropy_path):
    """Tests MicroPy Initial Setup"""
    expect_mp_dir = mock_micropy_path
    expect_stubs_dir = mock_micropy_path / 'stubs'
    mp = main.MicroPy()
    print("MP FILES:", mp.FILES)
    print("MP Content:", list(mp.FILES.iterdir()))
    assert expect_mp_dir.exists()
    assert expect_stubs_dir.exists()


def test_initial_stubs(mock_micropy_path):
    """Tests if initial stubs are added"""
    mp = main.MicroPy()
    stub_dir = mock_micropy_path / 'stubs'
    print(mp.STUBS)
    assert len(mp.STUBS) >= 0
    for stub in mp.STUBS:
        stub_dirs = stub_dir.iterdir()
        assert stub.path.exists()
        assert stub.path in stub_dirs
    assert len(mp.STUBS) == len(list(stub_dir.iterdir()))


def test_add_stub(mock_micropy, shared_datadir):
    """Test Adding Valid Stub"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stub = mock_micropy.add_stub(stub_path)
    assert stub in mock_micropy.STUBS
    assert stub.path in mock_micropy.STUB_DIR.iterdir()
    assert stub.path.exists()
