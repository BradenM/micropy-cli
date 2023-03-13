import json
from pathlib import Path

import pylint.lint
import pytest
from micropy.project.template import Template, TemplateProvider


@pytest.fixture
def stub_context(mock_mp_stubs):
    stubs = list(mock_mp_stubs.stubs)[:3]
    stub_paths = [stub.stubs for stub in stubs]
    frozen_paths = [stub.frozen for stub in stubs]
    fware_paths = [stub.firmware.frozen for stub in stubs]
    ctx_paths = [*stub_paths, *frozen_paths, *fware_paths]
    return (stubs, (stub_paths, frozen_paths, fware_paths), ctx_paths)


def test_vscode_template(stub_context, shared_datadir, tmp_path, mock_checks):
    stubs, paths, ctx_paths = stub_context
    prov = TemplateProvider(["vscode"])
    ctx_datadir = tmp_path / "ctx_cata"
    ctx_datadir.mkdir(exist_ok=True)
    # Add test local path
    ctx_local = ctx_datadir / "src" / "lib" / "somelib"
    ctx_local.mkdir(parents=True)
    ctx_absolute = Path("/fakedir/notinprojectdir/somelib")
    ctx_local_paths = [ctx_local, ctx_absolute]
    prov.render_to(
        "vscode",
        tmp_path,
        stubs=stubs,
        paths=ctx_paths,
        datadir=ctx_datadir,
        local_paths=ctx_local_paths,
    )
    expected_path = tmp_path / ".vscode" / "settings.json"
    out_content = expected_path.read_text()
    print(out_content)
    # Get rid of comments
    with expected_path.open() as f:
        lines = [line.strip() for line in f.readlines() if line]
        valid = [line for line in lines if "//" not in line[:2]]
    # Valid JSON?
    expect_paths = [str(p.relative_to(tmp_path)) for p in ctx_paths]
    expect_paths.append(str(ctx_local.relative_to(tmp_path)))  # add local path (should be relative)
    # local path outside of project dir (must be absolute)
    expect_paths.append(str(ctx_absolute.absolute()))
    content = json.loads("\n".join(valid))
    assert sorted(expect_paths) == sorted(content["python.autoComplete.extraPaths"])
    assert expected_path.exists()
    # Test Update
    ctx_paths.append(tmp_path / "foobar" / "foo.py")
    prov.update(
        "vscode",
        tmp_path,
        stubs=stubs,
        paths=ctx_paths,
        datadir=ctx_datadir,
        local_paths=ctx_local_paths,
    )
    content = json.loads(expected_path.read_text())
    expect_paths.append(str((tmp_path / "foobar" / "foo.py").relative_to(tmp_path)))
    assert sorted(expect_paths) == sorted(content["python.autoComplete.extraPaths"])
    # Test update with missing file
    expected_path.unlink()  # delete file
    prov.update("vscode", tmp_path, stubs=stubs, paths=ctx_paths, datadir=ctx_datadir)
    assert expected_path.exists()


def test_pylint_template(stub_context, tmp_path):
    def test_pylint_load():
        try:
            lint_args = ["--rcfile", str(expected_path.absolute())]
            pylint.lint.Run(lint_args)
        except SyntaxError:
            pytest.fail(str(SyntaxError))
        except:  # noqa
            pass

    stubs, paths, ctx_paths = stub_context
    ctx_datadir = tmp_path / "ctx_cata"
    ctx_datadir.mkdir(exist_ok=True)
    prov = TemplateProvider(["pylint"])
    prov.render_to("pylint", tmp_path, stubs=stubs, paths=ctx_paths, datadir=ctx_datadir)
    expected_path = tmp_path / ".pylintrc"
    assert expected_path.exists()
    # Will Pylint load it?
    test_pylint_load()
    # Test Update
    new_path = tmp_path / ".micropy" / "foobar" / "foo"
    ctx_paths.append(new_path)
    prov.update("pylint", tmp_path, stubs=stubs, paths=ctx_paths, datadir=ctx_datadir)
    init_hook = expected_path.read_text().splitlines(True)[2]
    hook_imports = init_hook.split(",")
    hook_path = str(Path(".micropy/foobar/foo")).replace(
        "\\", "/"
    )  # no need to use \\ on pylint Windows
    assert f' "{hook_path}"' in hook_imports
    test_pylint_load()


def test_generic_template(mock_mp_stubs, tmp_path):
    prov = TemplateProvider(["bootstrap", "pymakr"])
    prov.render_to("boot", tmp_path)
    expected_path = tmp_path / "src" / "boot.py"
    assert expected_path.exists()
    expected_content = (prov.TEMPLATE_DIR / "src" / "boot.py").read_text()
    out_content = expected_path.read_text()
    print(out_content)
    assert expected_content.strip() == out_content.strip()
    templ = prov.get("boot")
    assert templ.update(tmp_path) is None


def test_no_context():
    class BadTemplate(Template):
        def __init__(self, template, **kwargs):
            return super().__init__(template, **kwargs)

    with pytest.raises(NotImplementedError):
        x = BadTemplate("abc")
        print(x.context)
