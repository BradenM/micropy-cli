# -*- coding: utf-8 -*-

from micropy.project.template import TemplateProvider
import json


def test_vscode_template(mock_micropy, tmp_path):
    stubs = mock_micropy.STUBS[:3]
    prov = TemplateProvider()
    prov.render_to('vscode', tmp_path, stubs=stubs)
    expected_path = tmp_path / '.vscode' / 'settings.json'
    out_content = expected_path.read_text()
    print(out_content)
    # Get rid of comments
    with expected_path.open() as f:
        lines = [l.strip() for l in f.readlines() if l]
        valid = [l for l in lines if "//" not in l[:2]]
    # Valid JSON?
    stub_paths = [str(stub.path) for stub in stubs]
    content = json.loads("\n".join(valid))
    assert sorted(stub_paths) == sorted(
        content["python.autoComplete.extraPaths"])
    assert expected_path.exists()


def test_generic_template(mock_micropy, tmp_path):
    prov = TemplateProvider()
    prov.render_to('boot', tmp_path)
    expected_path = tmp_path / 'src' / 'boot.py'
    assert expected_path.exists()
    expected_content = (prov.TEMPLATE_DIR / 'src' / 'boot.py').read_text()
    out_content = expected_path.read_text()
    print(out_content)
    assert expected_content.strip() == out_content.strip()
