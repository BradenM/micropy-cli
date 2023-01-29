<a name="unreleased"></a>
## [Unreleased]

### Bug Fixes
- **compat:** <=3.8 python typing compat issues.
- **deps:** pin dependencies
- **deps:** update dependency markupsafe to v2.1.2
- **deps:** update dependency requests to v2.28.2
- **deps:** update dependency pydantic to v1.10.3
- **deps:** update dependency python-minifier to v2.8.0
- **deps:** pin dependencies
- **deps:** update dependency attrs to v22.2.0
- **deps:** update dependency importlib-metadata to v5.2.0
- **deps:** update dependency requirements-parser to v0.5.0
- **deps:** update dependency gitpython to v3.1.30
- **deps:** update dependency pydantic to v1.10.4
- **deps:** update dependency boltons to v21
- **main:** add types to `MicroPy.stubs`
- **main:** StubRepository has faux immutability.
- **stubs:** utilize absolute names in stub search results.
- **stubs:** perform repo lookups prior to adding stub
- **stubs:** ensure src path is path type in log.
- **stubs:** use `typing.Type` for sub py3.7 compat.
- **stubs:** remove mutating subclass hook from `StubsManifest`.
- **utils:** use importlib metadata to check micropy version in utils.
- **utils:** remove PathLike GenericAlias subscript for py <3.8
- **utils:** add annotations future in type utils.

### Code Refactoring
- **stubs:** remove search remote from stub manager.
- **stubs:** utilize locator strategies over stub source factory method.
- **stubs:** remove old `StubRepo` class.
- **stubs:** update repository impls to retain immutability.

### Features
- **cli:** utilize stub source locators during add.
- **cli:** improve stub search output.
- **cli:** add flag to show outdated stub packages in search + group output by repo.
- **cli:** format repo as title in stubs search output.
- **data:** add micropython-stubs source
- **data:** add display names for current stub sources.
- **deps:** add distlib.
- **deps:** add importlib_metadata as dep.
- **deps:** add pytest-clarity+better-exceptions to dev deps.
- **deps:** add attrs/pydantic
- **main:** init `StubRepository` as attr.
- **main:** drop in new StubRepository impl in place of StubRepo.
- **stubs:** rename `StubRepositoryPackage.repository` -> `manifest`.
- **stubs:** build progressive package indexes in `StubRepository`, utilize in search/resolve.
- **stubs:** make `StubPackage` immutable.
- **stubs:** make `StubsManifest` immutable.
- **stubs:** make `StubRepositoryPackage` immutable, iterate matchers.
- **stubs:** validate RepoInfo source, add method for fetching contents.
- **stubs:** add RepositoryInfo model.
- **stubs:** assume latest version by default, optionally show latest only in search, general improvements in stub repo.
- **stubs:** accept generic package type in stub manifest
- **stubs:** implement dirty metadata adapter for dist-based stubs until proper refactorings.
- **stubs:** make `StubSource` proper abstract, add prepare abstractmethod + impls.
- **stubs:** utilize `StubRepositoryPackage.match_exact`
- **stubs:** expose `repo_name`,`versioned_name`,`absolute_versioned_name` on `StubRepositoryPackage`
- **stubs:** make micropython stubs package sortable.
- **stubs:** add `resolve_package_(absolute,)_versioned_name` to manifest.
- **stubs:** impl `resolve_package_url` for micropython-stubs repo.
- **stubs:** add StubRepositoryPackage model.
- **stubs:** add StubPackage model.
- **stubs:** make `StubRepository.resolve_package` return `StubRepositoryPackage`
- **stubs:** enforce faux immutability in StubRepository.
- **stubs:** check absolute name for stub resolve matching.
- **stubs:** expose name/version/absolute_name fields from stub repo package.
- **stubs:** add method for resolving absolute stub package name from manifest.
- **stubs:** support reuse of `StubSource` instances, improvements.
- **stubs:** add `display_name` field to stub repository.
- **stubs:** `RepoStubLocator` locate strategy.
- **stubs:** impl resolve package method in StubRepository.
- **stubs:** expose url via StubRepositoryPackage descriptor.
- **stubs:** micropy-stubs resolve package url impl, stub micropython for now.
- **stubs:** add resolve package url abstract meth to stubs manifest
- **stubs:** add StubRepository for managing stub manifests.
- **stubs:** add Micropython stubs package/manifest models.
- **stubs:** utilize locators in `StubManager`, resolve requirements from metadata.
- **stubs:** add StubsManifest model.
- **stubs:** add MicropyStubs package/manifest models.
- **utils:** add types to `ensure_existing_dir`
- **utils:** defer updating stale cache with `utils.get_cached_data`
- **utils:** add SupportsLessThan protocol to types util.
- **utils:** add utils.types, PathStr alias.


<a name="v4.0.0"></a>
## [v4.0.0] - 2022-11-13
### Bug Fixes
- **deps:** update dependency python-minifier to v2.7.0
- **deps:** update dependency markupsafe to v2.1.1
- **deps:** update dependency jinja2 to v3.1.2
- **deps:** update dependency gitpython to v3.1.29
- **deps:** update dependency colorama to v0.4.6
- **deps:** pin dependencies

### Code Refactoring
- **stubs:** utilize helper method during remote stub unpack.
- **utils:** extract helper methods, add types.

### Features
- **deps:** update python constraint to include v3.11, update lockfile.
- **deps:** upgrade to click v8
- **deps:** update all deps in-range


<a name="v4.0.0-rc.2"></a>
## [v4.0.0-rc.2] - 2022-04-17
### Bug Fixes
- **pyd:** remove dict union operator till py3.9 min support
- **pyd:** only type-cast rshell if type checking is enabled
- **pyd:** capture module not found error during rshell import attempt
- **pyd:** upydevice connect proper attr error if before established
- **pyd:** use host path suffix check only as fallback in copy_to
- **pyd:** consumer handler protocol methods should not be writable

### Features
- **deps:** add upydevice+deps, missing type-stubs to dev, update mypy config
- **deps:** upgrade upydevice and remove prev missing deps
- **exc:** add PyDeviceError, PyDeviceConnectionError exceptions
- **main:** update to utilize new pyd module
- **pkg:** add pypi-test source to pyproject
- **pkg:** regenerate changelog
- **pkg:** add poetry+local pre-commit hook for docs export
- **pkg:** export pyd from pkg root
- **pkg:** add git-chlog config
- **pyb:** add abcs for PyDevice, MetaPyDevice, Consumer/StreamConsumer
- **pyd:** establish should return pyd instance, update consumer types
- **pyd:** use/pass consumer handlers via delegate, expose connect/dc
- **pyd:** add ConsumerDelegate, StreamHandlers, MessageHandlers
- **pyd:** update rshell backend to implement MetaPyDeviceBackend
- **pyd:** add PyDeviceConsumer protocol
- **pyd:** add PyDevice implementation
- **pyd:** update upyd backend to interfaces + cleanup
- **pyd:** move tqdm-progress consumer to pyd.consumers
- **pyd:** add Stream/Message consumer protocols+handler protos, Split MetaPyDevice/MetaPyDeviceBackend
- **pyd:** add upydevice-based pyd backend
- **pyd:** add rshell-based pydevice backend
- **pyd:** rename pyb module -> pyd
- **pyd:** add pyd module explicit exports
- **pyd:** allow delegate_cls to be injected to pydevice via init
- **scripts:** add script for exporting docs requirements
- **utils:** remove pybwrapper


<a name="v4.0.0.rc.1"></a>
## [v4.0.0.rc.1] - 2022-03-14
### Bug Fixes
- **dev-deps:** update pytest to ^7.0 to resolve py10+win pyreadline crash
- **pkg:** rshell markers for win32
- **pkg:** fix mistake in rshell marker
- **pkg:** do not install rshell when py>=3.10 and on windows due to pyreadline.
- **pkg:** win32 rshell python marker
- **pkg:** upgrade too and pin jinja2 @ 3.0.3
- **project:** report exception on install failure to stdout
- **stubber:** replace pyminifer with python-minifer
- **utils:** capture attribue err that occurs on py310 win32 rshell import
- **utils:** utilize mp-stubbers new logic for generating stubs

### Features
- **deps:** update dependencies scoped
- **deps:** update micropython-stubber to latest master commit
- **pkg:** move pytest+coverage cfg to pyproject
- **pkg:** add missing packaging dep
- **pkg:** update includes to be more strict
- **pkg:** restructure and cleanup pyproject with dependency groups
- **pkg:** merge create_stubs group into default


<a name="v3.6.0"></a>
## [v3.6.0] - 2021-05-17
### Bug Fixes
- **data:** update stubs schema for compat with latest stubber

### Features
- **deps:** update rshell dependency
- **deps:** update deps, add micropy-cli w/ extras as dev-dep
- **deps:** setup black, pre-commit
- **pkg:** update setup file
- **pre-commit:** add pre-commit config
- **stubber:** update micropython-stubber submodule to latest
- **utils:** remove dynamic
- **utils:** refactor stub-gen to stubs, dynamically create stubber module for import


<a name="v3.5.0"></a>
## [v3.5.0] - 2020-11-17

<a name="v3.5.0.rc.1"></a>
## [v3.5.0.rc.1] - 2020-11-17
### Bug Fixes
- full name case mismatch for pypi packages
- package installation failures were silent
- **pkg:** constrain questionary version to <1.8.0
- **pkg:** setuptools editable installation issues

### Features
- **package:** detect and return VCSDependencySource when needed in create dep source factory
- **package:** add VCSDependencySource class for supporting VCS requirements
- **package:** add attributes and logic for VCS packages
- **pkg:** bump questionary dependency to ^1.8.1
- **pkg:** add GitPython dependency

### Reverts
- chore(deps): update setup.py


<a name="v3.4.0"></a>
## [v3.4.0] - 2020-07-25
### Bug Fixes
- **deps:** update dpath constraint to >=1.4,<2.0


<a name="v3.3.0"></a>
## [v3.3.0] - 2019-12-23
### Bug Fixes
- ensure any values to be extended in config are of type list ([#94](https://github.com/BradenM/micropy-cli/issues/94))
- **utils:** ignore candidate releases when checking for update

### Features
- **project:** generate recommended extensions with vscode integration ([#95](https://github.com/BradenM/micropy-cli/issues/95))


<a name="v3.2.0"></a>
## [v3.2.0] - 2019-12-14

<a name="v3.2.0.rc.2"></a>
## [v3.2.0.rc.2] - 2019-12-13
### Bug Fixes
- Handle Invalid Requirements
- **cli:** Handle errors when reading requirements from path
- **cli:** Handle and Report Invalid Package Name Error
- **deps:** Fix loading requirements from path
- **utils:** Follow redirects when testing for valid url

### Code Refactoring
- **deps:** Remove Exception handling from Packages Module

### Features
- Add Base and Requirement Exceptions
- **poetry:** Update Poetry to Stable


<a name="v3.2.0.rc.1"></a>
## [v3.2.0.rc.1] - 2019-12-09
### Bug Fixes
- Make rshell and pyminifier requirements optional ([#82](https://github.com/BradenM/micropy-cli/issues/82))
- Colorama Version Constraint
- Colorama Broken Release, Style
- VSCode Settings failed to populate on reload ([#81](https://github.com/BradenM/micropy-cli/issues/81))
- **config:** Remove concrete path from ConfigSource
- **config:** Remove cache method for better implementation later
- **deps:** Temporary Directory would be removed before it was ready
- **logger:** Exception formatting
- **project:** Context not being updated when needed
- **project:** Add empty dict to config on create

### Code Refactoring
- Cleanup Stubs Module Context Handling
- **packages:** Use new Dependency Api in Packages Module

### Features
- **cli:** Basic install from path option implementation
- **config:** Manage sync via callback
- **config:** New Interface with file/memory autosync and dot notation
- **config:** Dictionary Config Source
- **config:** Cache and Root Key Context Manager for Config Items
- **config:** Use dpath to handle Config paths and merging
- **config:** Improved handling of collection data types
- **config:** Add pop method to config
- **config:** New and Improved Config File Interface
- **context:** Use DictConfig for Project Context
- **deps:** Package Class for representing a requirement
- **deps:** Address Package Source Uniformly
- **deps:** Allow local deps to be sourced from anywhere
- **project:** Add local-lib-path config option.
- **project:** Load Project Modules by individual Priority
- **project:** Update Projects to use Priority Queue
- **project:** Implement Dependencies in Project Module
- **project:** Render Local Deps in Project Settings
- **project:** Update Config/Context automatically
- **project:** Update modules to use new, more flexible config
- **project:** Use new Config Interface in Projects
- **project:** Try to add local deps as relative to project, fallback...
- **project:** Replace Project Cache with Config Instance
- **template:** Update TemplateModule

### Performance Improvements
- **size:** Slimmed Package Size


<a name="v3.1.1"></a>
## [v3.1.1] - 2019-12-03
### Bug Fixes
- HookProxy failed to resolve with kwargs
- **checks:** VSCode check failing on py36
- **logger:** Exception formatting
- **package:** Add metadata to pyproject.toml
- **package:** Update Makefile and bump2version to use pyproject
- **package:** Use Dephell to generate setup.py, Remove Manifiest.in
- **project:** Exception Raised if no Templates are used in Project
- **project:** VSCode check always failed silently

### Features
- Cleanup Log File Formatting
- Use Poetry for Dependency Management

### Performance Improvements
- **size:** Slimmed Package Size


<a name="v3.1.0"></a>
## [v3.1.0] - 2019-11-12
### Bug Fixes
- Handle Errors when adding Packages
- Project Context Stub Path Ordering
- HookProxy failed to work with descriptors.
- PackagesModule Dev, Project Context
- Move Template Check flag to TemplatesModule
- Active Project Resolve, Cli Templates List

### Code Refactoring
- Add Packages from File
- Import MicroPy and Modules to Package Root
- Restructure Project Module

### Features
- Report Ready on Project Load, Code Cleanup
- Write .gitignore file in generated .micropy folder
- Proxy Project Hooks to allow hooks with the same name, Split De...
- Resolve Project Hooks via attrs, Fix Stub List
- **project:** Project Method Hook Decorator

### Performance Improvements
- Lazy Load Project Stubs


<a name="v3.0.1"></a>
## [v3.0.1] - 2019-10-13
### Bug Fixes
- Auto Update Check's Cache not expiring after update
- VSCode Template Check always Fails on Linux ([#65](https://github.com/BradenM/micropy-cli/issues/65))
- **upstream:** Fails to Generate Stub Files


<a name="v3.0.0"></a>
## [v3.0.0] - 2019-10-13
### Bug Fixes
- Project Fails to Init due to Checks on Windows
- Stub Package Url fails to resolve on Windows
- Handle Chunked Content Length on Package Download
- Package urls not resolving correctly
- Fails to load Project if Template Files are Missing ([#55](https://github.com/BradenM/micropy-cli/issues/55))

### Code Refactoring
- **data:** Move all Data Paths to Data Module

### Features
- Add Flag for Skipping Template Checks
- Search/Retrieve Stubs Directly from micropy-stubs
- Update MicropyCli Stub Sources
- Refactor MicroPy Class for Better State Management

### Performance Improvements
- Lazy Load Stubs when Needed
- **project:** Lazy Load Current Active Project

### BREAKING CHANGE

micropy.STUBS renamed to micropy.stubs


<a name="v2.2.0"></a>
## [v2.2.0] - 2019-09-28
### Features
- Template Checks, MS-Python Check ([#52](https://github.com/BradenM/micropy-cli/issues/52))
- **cli:** Automatic Update Checks ([#54](https://github.com/BradenM/micropy-cli/issues/54))
- **vscode:** Ensure Jedi is Disabled in VSCode Template

### Performance Improvements
- **stubs:** Cache Available Stubs for Searching


<a name="v2.1.1"></a>
## [v2.1.1] - 2019-09-22
### Bug Fixes
- **hotfix:** Remove workspaceRoot var from VSCode Settings ([#51](https://github.com/BradenM/micropy-cli/issues/51))

### Features
- Relicensed under MIT

### BREAKING CHANGE

No longer compatible with <=ms-python.python[@2019](https://github.com/2019).8.30787 VSCode Extension


<a name="v2.1.0"></a>
## [v2.1.0] - 2019-09-01
### Bug Fixes
- **project:** Requirement Files skipped on First Init
- **windows:** Support User Level Directory Linking ([#45](https://github.com/BradenM/micropy-cli/issues/45))

### Features
- **log:** Cap Log File at 2MB
- **project:** Init Project with Micropy Dev Dependency
- **project:** Git Ignore Template Option


<a name="v2.0.2"></a>
## [v2.0.2] - 2019-08-21
### Bug Fixes
- **dep:** Require appropriate Click version
- **windows:** Warn User if MicroPy Lacks Admin Privs


<a name="v2.0.1"></a>
## [v2.0.1] - 2019-07-26
### Bug Fixes
- **stubs:** Reduce Schema Strictness


<a name="v2.0.0"></a>
## [v2.0.0] - 2019-07-25
### Bug Fixes
- **dep:** Broken Docutils Dependency
- **project:** Only modules install correctly

### Features
- Add Optional Pyminifier Dep for Stub Creation
- **cli:** Install Python Packages for Project
- **cli:** Verbosity Flag for Stub Creation
- **dep:** Update Tox to latest
- **dep:** Packaging Module Requirement
- **lib:** Update Stubber to Process Branch
- **project:** Update requirements.txt Files on Install
- **project:** Template Update Functionality
- **project:** Install from Requirements.txt
- **project:** Retrieve and Stub Project Requirements
- **project:** Project Config in Info File
- **project:** Make Templates Optional via CLI ([#30](https://github.com/BradenM/micropy-cli/issues/30))
- **pyb:** Handle Pyboard Output and Errors
- **stubs:** Minify Stubber Before Executing
- **util:** Generate Stub from File Utility


<a name="v1.1.3"></a>
## [v1.1.3] - 2019-07-20
### Bug Fixes
- ValueError raised after Creating Project in Windows ([#33](https://github.com/BradenM/micropy-cli/issues/33))
- Unicode Error raised when logging on Windows ([#32](https://github.com/BradenM/micropy-cli/issues/32))


<a name="v1.1.2"></a>
## [v1.1.2] - 2019-07-19
### Bug Fixes
- **stubs:** Ensure Firmware Stubs Load First


<a name="v1.1.1"></a>
## [v1.1.1] - 2019-07-17
### Bug Fixes
- Temp Hotfix for False Stub Duplication


<a name="v1.1.0"></a>
## [v1.1.0] - 2019-07-16
### Bug Fixes
- **cli:** Stub List always prints Unknown
- **cli:** Made Stub Search Case Insensitive
- **stubs:** FileExistsError when adding existing Stub

### Features
- **cli:** List Project Stubs if in Project Directory
- **cli:** Stubs now list by Firmware
- **cli:** Create Formatted Strings from Logger
- **cli:** Added --force flag when adding stubs
- **project:** Micropy Project Info File ([#29](https://github.com/BradenM/micropy-cli/issues/29))
- **project:** Micropy Project Folder ([#28](https://github.com/BradenM/micropy-cli/issues/28))


<a name="v1.0.0"></a>
## [v1.0.0] - 2019-07-11
### Bug Fixes
- **cli:** Init Crashes if no Stubs are Loaded
- **cli:** Create Stubs Help Formatting
- **log:** Output Highlight Bug, Cleanup
- **stub:** Stub Name without Firmware
- **stubs:** Firmware not showing as Installed in Stub Search
- **stubs:** Fix Existing Firmware Reinstall

### Features
- Implemented Local and Remote Stub Sources ([#18](https://github.com/BradenM/micropy-cli/issues/18))
- **cli:** Minified Cli Output Style
- **cli:** Search Available Stubs ([#27](https://github.com/BradenM/micropy-cli/issues/27))
- **cli:** Stream Downloads with Progress Bar
- **stub:** Update Stubs to Use New Stubber Schema ([#23](https://github.com/BradenM/micropy-cli/issues/23))
- **stubs:** Updated micropython-stubber to latest
- **stubs:** Add Firmware Frozen Modules to Templates
- **stubs:** Device Stubs Firmware Resolution ([#25](https://github.com/BradenM/micropy-cli/issues/25))
- **stubs:** Add Device Frozen Modules to Templates ([#24](https://github.com/BradenM/micropy-cli/issues/24))
- **stubs:** Added Stub Stdout Verbosity
- **stubs:** Add Stubs from Repositories ([#21](https://github.com/BradenM/micropy-cli/issues/21))
- **stubs:** Replaced Stubs with Stub "Packages"
- **stubs:** Stub Repositories ([#20](https://github.com/BradenM/micropy-cli/issues/20))
- **stubs:** Update Stub Creation ([#26](https://github.com/BradenM/micropy-cli/issues/26))
- **util:** Generic Utility Functions and Module Cleanup

### Performance Improvements
- **cli:** Only Instantiate MicroPy when needed


<a name="v0.3.0"></a>
## [v0.3.0] - 2019-06-25
### Code Refactoring
- MicroPy to use new Stub and Utility Features ([#14](https://github.com/BradenM/micropy-cli/issues/14))

### Features
- **cli:** Version Flag
- **log:** New Cli Output Style, Log Class Methods
- **pyb:** PyboardWrapper Utility ([#13](https://github.com/BradenM/micropy-cli/issues/13))
- **stubs:** Stub Manager ([#5](https://github.com/BradenM/micropy-cli/issues/5))
- **utils:** Utils Module and Validator Utility  ([#4](https://github.com/BradenM/micropy-cli/issues/4))


<a name="v0.2.0"></a>
## [v0.2.0] - 2019-06-14
### Features
- **log:** Added Proper Log Formatting, cleaned messages before write.
- **log:** Added Logging to Template Module
- **project:** Drop Cookiecutter for Purely Jinja2 ([#3](https://github.com/BradenM/micropy-cli/issues/3))


<a name="v0.1.1"></a>
## [v0.1.1] - 2019-06-10
### Bug Fixes
- **setup:** Fixed missing cookiecutter package requirement
- **setup:** Fixed Pypi misinformation, cleaned up dist-management files
- **setup:** Fix Missing .vscode Template Files


<a name="v0.1.0"></a>
## v0.1.0 - 2019-06-09
### Bug Fixes
- Fails First Time Setup Failed to init on first run if the stubs folder didnt exist
- Removed old command
- Fix Project Init
- Added rshell to setup.py
- Quick Fix before Project Class Restructure
- Packaging Fixes
- **package:** Allow multiple versions of python, Update Reqs
- **setup:** Included Template in Manifest
- **stub:** Fixed Refresh Stubs
- **stubs:** Cleaned Stub Names before Adding
- **stubs:** Removed Old Stub Command
- **stubs:** Fixed missing logging.py
- **template:** Fixed src template

### Code Refactoring
- Setup as proper package

### Features
- Project Init and Template Serialization
- Finished Package Setup and Structure
- Let Stub class handle validation and files
- Setup Template Files
- Initial commit
- Add Josverl Stubs on First Setup, Restructured MicroPy
- Added MicroPy Parent Class
- Added stubber as submodule over pulling files with requests
- **log:** Added Silet Stdout Context Manager to Logger
- **log:** Setup ServiceLog to work as a single parent Logger with ch...
- **log:** Added Logging
- **log:** Setup Logger as Borg for easy access
- **log:** Added file logging to ServiceLog, Added docs
- **project:** Project Module Rewrite to use Cookiecutter and JSON
- **pylint:** Added checkbox to choose stubs for pylint
- **stub:** Pass Multiple Stubs to .pylintrc
- **stub:** Added stub add, refresh commands
- **stub:** Added createstub.py download
- **stub:** Added Stub Class, Moved Stub logic to MicroPy/Stub
- **stubs:** Added Automated Stub Creation on PyBoard
- **stubs:** Added Stub Validation, Stub Class Restructure
- **stubs:** Added Basic Stub Exceptions
- **template:** Setup Template in Cookiecutter Fashion


[Unreleased]: https://github.com/BradenM/micropy-cli/compare/v4.0.0...HEAD
[v4.0.0]: https://github.com/BradenM/micropy-cli/compare/v4.0.0-rc.2...v4.0.0
[v4.0.0-rc.2]: https://github.com/BradenM/micropy-cli/compare/v4.0.0.rc.1...v4.0.0-rc.2
[v4.0.0.rc.1]: https://github.com/BradenM/micropy-cli/compare/v3.6.0...v4.0.0.rc.1
[v3.6.0]: https://github.com/BradenM/micropy-cli/compare/v3.5.0...v3.6.0
[v3.5.0]: https://github.com/BradenM/micropy-cli/compare/v3.5.0.rc.1...v3.5.0
[v3.5.0.rc.1]: https://github.com/BradenM/micropy-cli/compare/v3.4.0...v3.5.0.rc.1
[v3.4.0]: https://github.com/BradenM/micropy-cli/compare/v3.3.0...v3.4.0
[v3.3.0]: https://github.com/BradenM/micropy-cli/compare/v3.2.0...v3.3.0
[v3.2.0]: https://github.com/BradenM/micropy-cli/compare/v3.2.0.rc.2...v3.2.0
[v3.2.0.rc.2]: https://github.com/BradenM/micropy-cli/compare/v3.2.0.rc.1...v3.2.0.rc.2
[v3.2.0.rc.1]: https://github.com/BradenM/micropy-cli/compare/v3.1.1...v3.2.0.rc.1
[v3.1.1]: https://github.com/BradenM/micropy-cli/compare/v3.1.0...v3.1.1
[v3.1.0]: https://github.com/BradenM/micropy-cli/compare/v3.0.1...v3.1.0
[v3.0.1]: https://github.com/BradenM/micropy-cli/compare/v3.0.0...v3.0.1
[v3.0.0]: https://github.com/BradenM/micropy-cli/compare/v2.2.0...v3.0.0
[v2.2.0]: https://github.com/BradenM/micropy-cli/compare/v2.1.1...v2.2.0
[v2.1.1]: https://github.com/BradenM/micropy-cli/compare/v2.1.0...v2.1.1
[v2.1.0]: https://github.com/BradenM/micropy-cli/compare/v2.0.2...v2.1.0
[v2.0.2]: https://github.com/BradenM/micropy-cli/compare/v2.0.1...v2.0.2
[v2.0.1]: https://github.com/BradenM/micropy-cli/compare/v2.0.0...v2.0.1
[v2.0.0]: https://github.com/BradenM/micropy-cli/compare/v1.1.3...v2.0.0
[v1.1.3]: https://github.com/BradenM/micropy-cli/compare/v1.1.2...v1.1.3
[v1.1.2]: https://github.com/BradenM/micropy-cli/compare/v1.1.1...v1.1.2
[v1.1.1]: https://github.com/BradenM/micropy-cli/compare/v1.1.0...v1.1.1
[v1.1.0]: https://github.com/BradenM/micropy-cli/compare/v1.0.0...v1.1.0
[v1.0.0]: https://github.com/BradenM/micropy-cli/compare/v0.3.0...v1.0.0
[v0.3.0]: https://github.com/BradenM/micropy-cli/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/BradenM/micropy-cli/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/BradenM/micropy-cli/compare/v0.1.0...v0.1.1
