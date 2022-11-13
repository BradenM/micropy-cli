from pathlib import Path

import pytest
from boltons.namedutils import namedlist
from micropy import packages

EXPPKG = namedlist("ExpectPackage", ["name", "specs", "full_name"])


class TestPackages:
    class MockSource:
        def __init__(self, pkg, has_init):
            self.pkg = pkg
            self.has_init = has_init

    @pytest.fixture(params=[True, False], ids=["package", "module"])
    def mock_source(self, request, mock_pkg):
        if request.param:
            # true packages vs file
            (mock_pkg / "__init__.py").touch()
        return self.MockSource(mock_pkg, request.param)

    @pytest.fixture(params=[True, False], ids=["package", "module"])
    def mock_source_path(self, request, tmp_path):
        path = tmp_path / "file.py"
        if request.param is True:
            pkg = tmp_path
            path = tmp_path / "__init__.py"
        else:
            pkg = tmp_path
        path.touch()
        return self.MockSource(pkg, request.param)

    @pytest.mark.parametrize(
        "package,expect",
        [
            (
                "git+https://github.com/jczic/MicroWebSrv2.git@master#egg=MicroWebSrv2",
                packages.VCSDependencySource,
            ),
            ("picoweb", packages.PackageDependencySource),
            ("-e /foobar/pkg", packages.LocalDependencySource),
        ],
    )
    def test_factory(self, package, expect):
        source = packages.create_dependency_source(package)
        assert isinstance(source, expect)

    @pytest.mark.parametrize(
        "requirement,expect",
        [
            (
                ["git+https://github.com/jczic/MicroWebSrv2.git@master#egg=MicroWebSrv2"],
                [
                    "microwebsrv2",
                    "git+https://github.com/jczic/MicroWebSrv2.git@master#egg=MicroWebSrv2",
                    "git+https://github.com/jczic/MicroWebSrv2.git@master#egg=MicroWebSrv2",
                ],
            ),
            (["picoweb"], ["picoweb", "*", "picoweb"]),
            (["picoweb==^7.1"], ["picoweb", "==^7.1", "picoweb==^7.1"]),
            (["BlynkLib==0.0.0"], ["blynklib", "==0.0.0", "blynklib==0.0.0"]),
            (
                ["-e /foobar/somepkg", "somepackage"],
                ["somepackage", "-e /foobar/somepkg", "-e /foobar/somepkg"],
            ),
            (["-e /foobar/somepkg"], ["somepkg", "-e /foobar/somepkg", "-e /foobar/somepkg"]),
        ],
    )
    def test_package(self, mock_pkg, requirement, expect):
        source = packages.create_dependency_source(*requirement)
        pkg = source.package
        assert pkg.name == expect[0]  # name
        assert pkg.pretty_specs == expect[1]  # specs
        assert str(pkg) == expect[2]  # full name ()

    def test_package_source(self, mock_source):
        def format_desc(x):
            return f"desc{x}"

        source = packages.create_dependency_source("blynklib", format_desc=format_desc)
        with source as files:
            if mock_source.has_init:
                assert isinstance(files, Path)
                assert mock_source.pkg.name == files.name
            else:
                assert isinstance(files, list)
                file_names = [(p.name, s.name) for p, s in files]
                file_names = list(sum(file_names, ()))
                assert sorted(["file.py", "file.pyi", "module.py", "module.pyi"]) == sorted(
                    file_names
                )

    def test_package_path(self, mock_source_path):
        source = packages.create_dependency_source(f"-e {mock_source_path.pkg}")
        with source as files:
            if mock_source_path.has_init:
                # is proper package
                assert files.is_dir()
            if mock_source_path.has_init is False:
                # is module
                assert files.is_dir()
                assert files == source.package.path

    @pytest.mark.parametrize(
        "pkg,expect",
        [
            (("micropy-cli", "*"), EXPPKG("micropy-cli", "*", "micropy-cli")),
            (("blynklib", "==0.0.0"), EXPPKG("blynklib", "==0.0.0", "blynklib==0.0.0")),
            (
                ("custompkg", "-e src/lib/custompackage"),
                EXPPKG("custompkg", "-e src/lib/custompackage", "-e src/lib/custompackage"),
            ),
        ],
    )
    def test_package_from_text(self, pkg, expect, utils):
        pkg = packages.Package.from_text(*pkg)
        assert pkg.name == expect.name
        assert pkg.full_name == pkg.full_name
        assert pkg.pretty_specs == expect.specs
        is_e = "-e" in pkg.full_name
        assert pkg.editable == is_e
        if pkg.editable:
            assert pkg.path == Path("src/lib/custompackage")
        else:
            assert pkg.path == None
