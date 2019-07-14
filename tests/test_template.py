# -*- coding: utf-8 -*-

import json
from pathlib import Path

import pylint.lint
import pytest

from micropy.project.template import Template, TemplateProvider


@pytest.fixture
def stub_context(mock_mp_stubs):
    stubs = list(mock_mp_stubs.STUBS)[:3]
    stub_paths = [stub.stubs for stub in stubs]
    frozen_paths = [stub.frozen for stub in stubs]
    fware_paths = [stub.firmware.frozen for stub in stubs]
    ctx_paths = [*stub_paths, *frozen_paths, *fware_paths]
    return (stubs, (stub_paths, frozen_paths, fware_paths), ctx_paths)


def test_vscode_template(stub_context, shared_datadir, tmp_path):
    stubs, paths, ctx_paths = stub_context
    prov = TemplateProvider()
    ctx_datadir = tmp_path / 'ctx_cata'
    ctx_datadir.mkdir(exist_ok=True)
    prov.render_to('vscode', tmp_path, stubs=stubs,
                   paths=ctx_paths, datadir=ctx_datadir)
    expected_path = tmp_path / '.vscode' / 'settings.json'
    out_content = expected_path.read_text()
    print(out_content)
    # Get rid of comments
    with expected_path.open() as f:
        lines = [l.strip() for l in f.readlines() if l]
        valid = [l for l in lines if "//" not in l[:2]]
    # Valid JSON?
    root = Path("${workspaceRoot}")
    expect_paths = [str((root / p.relative_to(tmp_path)))
                    for p in ctx_paths]
    content = json.loads("\n".join(valid))
    assert sorted(expect_paths) == sorted(
        content["python.autoComplete.extraPaths"])
    assert expected_path.exists()


def test_pylint_template(stub_context, tmp_path):
    stubs, paths, ctx_paths = stub_context
    ctx_datadir = tmp_path / 'ctx_cata'
    ctx_datadir.mkdir(exist_ok=True)
    prov = TemplateProvider()
    prov.render_to("pylint", tmp_path, stubs=stubs,
                   paths=ctx_paths, datadir=ctx_datadir)
    expected_path = tmp_path / '.pylintrc'
    assert expected_path.exists()
    # Will Pylint load it?
    try:
        lint_args = ["--rcfile", str(expected_path.absolute())]
        pylint.lint.Run(lint_args)
    except SyntaxError:
        pytest.fail(str(SyntaxError))  # noqa
    except:  # noqa
        pass


def test_generic_template(mock_mp_stubs, tmp_path):
    prov = TemplateProvider()
    prov.render_to('boot', tmp_path)
    expected_path = tmp_path / 'src' / 'boot.py'
    assert expected_path.exists()
    expected_content = (prov.TEMPLATE_DIR / 'src' / 'boot.py').read_text()
    out_content = expected_path.read_text()
    print(out_content)
    assert expected_content.strip() == out_content.strip()


def test_no_context():
    class BadTemplate(Template):
        def __init__(self, template, **kwargs):
            return super().__init__(template, **kwargs)

    with pytest.raises(NotImplementedError):
        x = BadTemplate('abc')
        print(x.context)
