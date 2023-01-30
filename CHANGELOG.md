<a name="v4.0.0"></a>

## [4.1.0-beta](https://github.com/BradenM/micropy-cli/compare/v4.0.0...v4.1.0-beta) (2023-01-30)


### Features

* **cli:** Add flag to show outdated stub packages in search + group output by repo. ([e2cdff7](https://github.com/BradenM/micropy-cli/commit/e2cdff7b0642e461182704835a6c826693c0deca))
* **cli:** Format repo as title in stubs search output. ([eaf0543](https://github.com/BradenM/micropy-cli/commit/eaf054307f4669ab1578b8bc090fbd9c1b42ab7a))
* **cli:** Improve stub search output. ([4c127ac](https://github.com/BradenM/micropy-cli/commit/4c127ac5dab299e91a56fa2d675b771b45a79cdd))
* **cli:** Utilize stub source locators during add. ([d24b409](https://github.com/BradenM/micropy-cli/commit/d24b4095c168184025be5736aee4fbc69427c6df))
* **data:** Add display names for current stub sources. ([7f6b2cd](https://github.com/BradenM/micropy-cli/commit/7f6b2cd4afe9bcea1b76029a2f94d96bc3d18de8))
* **data:** Add micropython-stubs source ([de9c2e2](https://github.com/BradenM/micropy-cli/commit/de9c2e2c987422d4871b60ab0cd7ade624c387d8))
* **deps:** Add attrs/pydantic ([06660f0](https://github.com/BradenM/micropy-cli/commit/06660f0bdaf6c06e3787dd170e7d47bd036c3722))
* **deps:** Add distlib. ([fab22ba](https://github.com/BradenM/micropy-cli/commit/fab22ba2e2fbccf791e64f825dc3545ef2c5606d))
* **deps:** Add importlib_metadata as dep. ([6acf3ca](https://github.com/BradenM/micropy-cli/commit/6acf3ca11f9dd7444aa2e39fd0a17fe52cb3226c))
* **deps:** Add pytest-clarity+better-exceptions to dev deps. ([dc9d958](https://github.com/BradenM/micropy-cli/commit/dc9d9587c5acab63fe5d6deb6b1e9e29716ee9e0))
* **main:** Drop in new StubRepository impl in place of StubRepo. ([25f0402](https://github.com/BradenM/micropy-cli/commit/25f0402fe65420337d9dffcc1a7abdc3962f2f1f))
* **main:** Init `StubRepository` as attr. ([c17be65](https://github.com/BradenM/micropy-cli/commit/c17be65e532c04bbaddd00f1d38c01abb8f1e2ff))
* **pkg:** Add __main__ module entry. ([2388858](https://github.com/BradenM/micropy-cli/commit/238885848cf47d4dadab907130a3c715341bb9d9))
* **pkg:** Cleanup package entry, dynamically resolve version. ([72ea665](https://github.com/BradenM/micropy-cli/commit/72ea66584387bc3f0db85d9042d14b9ad676884e))
* **project:** Add pylance settings to vscode template. ([bbdc936](https://github.com/BradenM/micropy-cli/commit/bbdc936c5885dfe80fde7676344ce97cada6807f))
* **project:** Assume pylance until proper refactorings can be done. ([2610c2a](https://github.com/BradenM/micropy-cli/commit/2610c2a38b83c0d525e3a31c4ff0d40fc88a7ea7))
* **stubs:** `RepoStubLocator` locate strategy. ([08f8f86](https://github.com/BradenM/micropy-cli/commit/08f8f863b2fe8b5eb75aa88374935299d03ba6c5))
* **stubs:** Accept generic package type in stub manifest ([9d17331](https://github.com/BradenM/micropy-cli/commit/9d173316f0dc7da5479523b82159d461ee990b46))
* **stubs:** Add `display_name` field to stub repository. ([a3ef03f](https://github.com/BradenM/micropy-cli/commit/a3ef03f50b79cb0139c4b0423c86f32d3c1acd30))
* **stubs:** Add `resolve_package_(absolute,)_versioned_name` to manifest. ([37bbfa6](https://github.com/BradenM/micropy-cli/commit/37bbfa678bb29cc86f1a202ec994f9e40fb6e0fa))
* **stubs:** Add method for resolving absolute stub package name from manifest. ([ad55507](https://github.com/BradenM/micropy-cli/commit/ad55507a6b19b5273ef0f9c44d1112faa7b151c9))
* **stubs:** Add MicropyStubs package/manifest models. ([021c279](https://github.com/BradenM/micropy-cli/commit/021c279fdc2b50a55a641761ecfc32bf54398b9b))
* **stubs:** Add Micropython stubs package/manifest models. ([a9297dc](https://github.com/BradenM/micropy-cli/commit/a9297dcfacbd5a31e7207b43300cd4376d9ce089))
* **stubs:** Add RepositoryInfo model. ([109aed3](https://github.com/BradenM/micropy-cli/commit/109aed30e7e588dcbeae405ead174c6b1c26d745))
* **stubs:** Add resolve package url abstract meth to stubs manifest ([8737f52](https://github.com/BradenM/micropy-cli/commit/8737f529365f556a0d3d1e4ccde1da2e2beae7aa))
* **stubs:** Add StubPackage model. ([9664111](https://github.com/BradenM/micropy-cli/commit/9664111e9304fa3149da992adbf247ec97587f1b))
* **stubs:** Add StubRepository for managing stub manifests. ([781f7cd](https://github.com/BradenM/micropy-cli/commit/781f7cddcf3912c8da89e790b717b34f04366737))
* **stubs:** Add StubRepositoryPackage model. ([e0dda9f](https://github.com/BradenM/micropy-cli/commit/e0dda9f193eca1499f3d42e0df8fb8f2e8ecc0f8))
* **stubs:** Add StubsManifest model. ([3ae9456](https://github.com/BradenM/micropy-cli/commit/3ae9456a3277e16161f0c8f29616377338afce4c))
* **stubs:** Assume latest version by default, optionally show latest only in search, general improvements in stub repo. ([b55b483](https://github.com/BradenM/micropy-cli/commit/b55b483d591990f6cdf264e2ad1fcc9f190dddb0))
* **stubs:** Build progressive package indexes in `StubRepository`, utilize in search/resolve. ([318ec13](https://github.com/BradenM/micropy-cli/commit/318ec13e1fb35e6f757ec426c1f32c712de00f9b))
* **stubs:** Check absolute name for stub resolve matching. ([142648d](https://github.com/BradenM/micropy-cli/commit/142648d4e2edabd6956723e781f6d7608a5f6030))
* **stubs:** Enforce faux immutability in StubRepository. ([a17cc5e](https://github.com/BradenM/micropy-cli/commit/a17cc5e66e938edd093ba1e4c7c283ab6d64d074))
* **stubs:** Expose `repo_name`,`versioned_name`,`absolute_versioned_name` on `StubRepositoryPackage` ([e257aa5](https://github.com/BradenM/micropy-cli/commit/e257aa56d14a98e3b81ef26c5e8fc80615036d93))
* **stubs:** Expose name/version/absolute_name fields from stub repo package. ([d88dcae](https://github.com/BradenM/micropy-cli/commit/d88dcaea98c30b41ccacd18ae7f4c1b474fa9730))
* **stubs:** Expose url via StubRepositoryPackage descriptor. ([4fd1b12](https://github.com/BradenM/micropy-cli/commit/4fd1b1202503bed22a34e861df8ff815e5a5363e))
* **stubs:** Impl `resolve_package_url` for micropython-stubs repo. ([4bd70aa](https://github.com/BradenM/micropy-cli/commit/4bd70aaea7c78ef2ae81bf432f53cef8971d5870))
* **stubs:** Impl resolve package method in StubRepository. ([c28d988](https://github.com/BradenM/micropy-cli/commit/c28d98815a31cb0c790ea4fdcaa7371f202545b0))
* **stubs:** Implement dirty metadata adapter for dist-based stubs until proper refactorings. ([a60138f](https://github.com/BradenM/micropy-cli/commit/a60138f73863b3b93e8465a38b3805aec99f88fe))
* **stubs:** Make `StubPackage` immutable. ([2fab17d](https://github.com/BradenM/micropy-cli/commit/2fab17d46445448c93bce1ca532f112507480f40))
* **stubs:** Make `StubRepository.resolve_package` return `StubRepositoryPackage` ([24ef2fa](https://github.com/BradenM/micropy-cli/commit/24ef2fa51eafcfc25b7f468288908fef736c4830))
* **stubs:** Make `StubRepositoryPackage` immutable, iterate matchers. ([ae71f91](https://github.com/BradenM/micropy-cli/commit/ae71f9136aeae81e37f03cfe7d8ea564e64f85cf))
* **stubs:** Make `StubsManifest` immutable. ([2a6ffa3](https://github.com/BradenM/micropy-cli/commit/2a6ffa3fb57e304cda88cc22c742b454a800db7a))
* **stubs:** Make `StubSource` proper abstract, add prepare abstractmethod + impls. ([d690e71](https://github.com/BradenM/micropy-cli/commit/d690e71c6c1e9d90dc4414323c6488f7fbd7d540))
* **stubs:** Make micropython stubs package sortable. ([49b6df0](https://github.com/BradenM/micropy-cli/commit/49b6df03d4b0aeb2ef124a3f2150bb3417019e80))
* **stubs:** Micropy-stubs resolve package url impl, stub micropython for now. ([c832cb0](https://github.com/BradenM/micropy-cli/commit/c832cb0c82ce3533ae18e90ada0359e375de2e1e))
* **stubs:** Rename `StubRepositoryPackage.repository` -&gt; `manifest`. ([a8b3ec8](https://github.com/BradenM/micropy-cli/commit/a8b3ec8b72094654cf665bc330e75a55bdf96b72))
* **stubs:** Support reuse of `StubSource` instances, improvements. ([b873a62](https://github.com/BradenM/micropy-cli/commit/b873a62970264928d772575c84e6c8ead305c6dc))
* **stubs:** Utilize `StubRepositoryPackage.match_exact` ([3ec08dd](https://github.com/BradenM/micropy-cli/commit/3ec08ddc5aad0bfbd8b98da6388989368d674790))
* **stubs:** Utilize locators in `StubManager`, resolve requirements from metadata. ([5c19624](https://github.com/BradenM/micropy-cli/commit/5c196249704a14d95ebfc99aa75ae77054cd8c48))
* **stubs:** Validate RepoInfo source, add method for fetching contents. ([0f7487f](https://github.com/BradenM/micropy-cli/commit/0f7487fa45beb62d149539967b6671c78cc41c60))
* **utils:** Add SupportsLessThan protocol to types util. ([489a9b0](https://github.com/BradenM/micropy-cli/commit/489a9b041082af18adf929471d7cc8f1f0bd39d5))
* **utils:** Add types to `ensure_existing_dir` ([e8e6ea8](https://github.com/BradenM/micropy-cli/commit/e8e6ea886098bd7bfceaf084e1d67673b5290177))
* **utils:** Add utils._compat module, add importlib metadata ([5722504](https://github.com/BradenM/micropy-cli/commit/572250447091e721623e562420c80295da999525))
* **utils:** Add utils.types, PathStr alias. ([63f65b9](https://github.com/BradenM/micropy-cli/commit/63f65b9b649f8de7b3d244c01a5fe17c201c4ca6))
* **utils:** Defer updating stale cache with `utils.get_cached_data` ([afd2ba5](https://github.com/BradenM/micropy-cli/commit/afd2ba5932d375a89401d1c314a3d6447a56e53f))


### Bug Fixes

* **cli:** Click fails to resolve package version. ([65ef13b](https://github.com/BradenM/micropy-cli/commit/65ef13b3939ffa65beca8eb74fd580cfd31d3382))
* **compat:** &lt;=3.8 python typing compat issues. ([e7600b4](https://github.com/BradenM/micropy-cli/commit/e7600b42a9f08035187b8644eecc66315619c753))
* **deps:** Only install import-metadata when py version &lt;3.10 ([ac1356d](https://github.com/BradenM/micropy-cli/commit/ac1356da308cfae94d16cd9935b9733ed0fad67a))
* **deps:** Pin dependencies ([84aa3c3](https://github.com/BradenM/micropy-cli/commit/84aa3c32db009121fbdd868b9664b648087186d3))
* **deps:** Pin dependencies ([1b6a46a](https://github.com/BradenM/micropy-cli/commit/1b6a46a828081d31153428e467780216737723a9))
* **deps:** Update dependency attrs to v22.2.0 ([9435223](https://github.com/BradenM/micropy-cli/commit/9435223ebe70554b6fc8d45ad68a798809ce55e2))
* **deps:** Update dependency boltons to v21 ([52bd39c](https://github.com/BradenM/micropy-cli/commit/52bd39c989dbbd1c7130ab8702d1c8caa0b50133))
* **deps:** Update dependency gitpython to v3.1.30 ([f5bb503](https://github.com/BradenM/micropy-cli/commit/f5bb5037aa1965be85198269b2ab8166f660f228))
* **deps:** Update dependency importlib-metadata to v5.2.0 ([42ab466](https://github.com/BradenM/micropy-cli/commit/42ab46681b5597eeb77d78573adcdabcd6a10bd0))
* **deps:** Update dependency markupsafe to v2.1.2 ([4239f9b](https://github.com/BradenM/micropy-cli/commit/4239f9bee88681f357b01f09b55b032ce3a5d39c))
* **deps:** Update dependency pydantic to v1.10.3 ([8d4d64d](https://github.com/BradenM/micropy-cli/commit/8d4d64ddc4ffcb64b578bd04f3f91092f6fc73a4))
* **deps:** Update dependency pydantic to v1.10.4 ([22dfef1](https://github.com/BradenM/micropy-cli/commit/22dfef18fc60db43564ee7379b319a6bb3a200e4))
* **deps:** Update dependency python-minifier to v2.8.0 ([9b0b2ef](https://github.com/BradenM/micropy-cli/commit/9b0b2efcfd2f3bc3c3ff6a8ee596329471733bd9))
* **deps:** Update dependency requests to v2.28.2 ([8e8d259](https://github.com/BradenM/micropy-cli/commit/8e8d259065b3d226aeee7be4ee0ed81cc9c7643d))
* **deps:** Update dependency requirements-parser to v0.5.0 ([26a8931](https://github.com/BradenM/micropy-cli/commit/26a8931d76121416b06fd8da90ee93e040963594))
* **main:** Add types to `MicroPy.stubs` ([2340184](https://github.com/BradenM/micropy-cli/commit/2340184db4a6e811377eab8f86f99333b8c16ab6))
* **main:** StubRepository has faux immutability. ([71feed2](https://github.com/BradenM/micropy-cli/commit/71feed28fa9a94108629784e0ba5f0de3e42ce70))
* **project:** Bad type union. ([3d32e5c](https://github.com/BradenM/micropy-cli/commit/3d32e5cb3f7802d867a7a9ac7788d33ea7c6f2cd))
* **stubs:** Ensure src path is path type in log. ([881a6a6](https://github.com/BradenM/micropy-cli/commit/881a6a6401166b621bd5eef0e76cf0b905d0b1dc))
* **stubs:** Perform repo lookups prior to adding stub ([5410a13](https://github.com/BradenM/micropy-cli/commit/5410a1369d6f693b69e36fc42b25f4a9a23c222a))
* **stubs:** Remove mutating subclass hook from `StubsManifest`. ([d3fcd7e](https://github.com/BradenM/micropy-cli/commit/d3fcd7eaef30da7e1621a507ba179a52d80ee1cf))
* **stubs:** Use `typing.Type` for sub py3.7 compat. ([1350263](https://github.com/BradenM/micropy-cli/commit/1350263bcd8b73368d99e849ead50d61b9e479b8))
* **stubs:** Utilize absolute names in stub search results. ([6c81a93](https://github.com/BradenM/micropy-cli/commit/6c81a93e8596836d13cbf5a8c0554495d5873b6b))
* **utils:** Add annotations future in type utils. ([d2d0ed8](https://github.com/BradenM/micropy-cli/commit/d2d0ed815cb46c2d7fbca6d9c1408813aa3c8565))
* **utils:** Remove PathLike GenericAlias subscript for py &lt;3.8 ([e22343a](https://github.com/BradenM/micropy-cli/commit/e22343af79972c90c68de51249f4bd48c43372b1))
* **utils:** Use importlib metadata to check micropy version in utils. ([dbeb0a9](https://github.com/BradenM/micropy-cli/commit/dbeb0a90ebe3fbe1168968198d799514382682c3))


### Documentation

* **chglog:** Remove unreleased for release-please. ([22d7be0](https://github.com/BradenM/micropy-cli/commit/22d7be04ac806653962187aa5e67f28fd07726b9))
* **conf:** Dynamically determine docs release version ([fc8ab96](https://github.com/BradenM/micropy-cli/commit/fc8ab966f8f4a44031eba42145afc244c521c896))


### Code Refactoring

* **stubs:** Remove old `StubRepo` class. ([b9de35a](https://github.com/BradenM/micropy-cli/commit/b9de35ab082b9c2e69d5b130e9e11dc45f843320))
* **stubs:** Remove search remote from stub manager. ([95d42f0](https://github.com/BradenM/micropy-cli/commit/95d42f0f643e030f4f6e3f3e6770260a445e2014))
* **stubs:** Update repository impls to retain immutability. ([b44b335](https://github.com/BradenM/micropy-cli/commit/b44b335d1a70421058fdb715fc9d95cf2bd84fae))
* **stubs:** Utilize locator strategies over stub source factory method. ([e81ac84](https://github.com/BradenM/micropy-cli/commit/e81ac8467c744f8d4462d6dd18d877c906d97773))
* **utils:** Update usage of importlib metadata. ([a09aaf9](https://github.com/BradenM/micropy-cli/commit/a09aaf9d7e15c61ad58b2a500514e58bedbb8741))

## [v4.0.0] - 2022-11-13

### Bug Fixes

-   **deps:** update dependency python-minifier to v2.7.0
-   **deps:** update dependency markupsafe to v2.1.1
-   **deps:** update dependency jinja2 to v3.1.2
-   **deps:** update dependency gitpython to v3.1.29
-   **deps:** update dependency colorama to v0.4.6
-   **deps:** pin dependencies

### Code Refactoring

-   **stubs:** utilize helper method during remote stub unpack.
-   **utils:** extract helper methods, add types.

### Features

-   **deps:** update python constraint to include v3.11, update lockfile.
-   **deps:** upgrade to click v8
-   **deps:** update all deps in-range

<a name="v4.0.0-rc.2"></a>

## [v4.0.0-rc.2] - 2022-04-17

### Bug Fixes

-   **pyd:** remove dict union operator till py3.9 min support
-   **pyd:** only type-cast rshell if type checking is enabled
-   **pyd:** capture module not found error during rshell import attempt
-   **pyd:** upydevice connect proper attr error if before established
-   **pyd:** use host path suffix check only as fallback in copy_to
-   **pyd:** consumer handler protocol methods should not be writable

### Features

-   **deps:** add upydevice+deps, missing type-stubs to dev, update mypy config
-   **deps:** upgrade upydevice and remove prev missing deps
-   **exc:** add PyDeviceError, PyDeviceConnectionError exceptions
-   **main:** update to utilize new pyd module
-   **pkg:** add pypi-test source to pyproject
-   **pkg:** regenerate changelog
-   **pkg:** add poetry+local pre-commit hook for docs export
-   **pkg:** export pyd from pkg root
-   **pkg:** add git-chlog config
-   **pyb:** add abcs for PyDevice, MetaPyDevice, Consumer/StreamConsumer
-   **pyd:** establish should return pyd instance, update consumer types
-   **pyd:** use/pass consumer handlers via delegate, expose connect/dc
-   **pyd:** add ConsumerDelegate, StreamHandlers, MessageHandlers
-   **pyd:** update rshell backend to implement MetaPyDeviceBackend
-   **pyd:** add PyDeviceConsumer protocol
-   **pyd:** add PyDevice implementation
-   **pyd:** update upyd backend to interfaces + cleanup
-   **pyd:** move tqdm-progress consumer to pyd.consumers
-   **pyd:** add Stream/Message consumer protocols+handler protos, Split MetaPyDevice/MetaPyDeviceBackend
-   **pyd:** add upydevice-based pyd backend
-   **pyd:** add rshell-based pydevice backend
-   **pyd:** rename pyb module -> pyd
-   **pyd:** add pyd module explicit exports
-   **pyd:** allow delegate_cls to be injected to pydevice via init
-   **scripts:** add script for exporting docs requirements
-   **utils:** remove pybwrapper

<a name="v4.0.0.rc.1"></a>

## [v4.0.0.rc.1] - 2022-03-14

### Bug Fixes

-   **dev-deps:** update pytest to ^7.0 to resolve py10+win pyreadline crash
-   **pkg:** rshell markers for win32
-   **pkg:** fix mistake in rshell marker
-   **pkg:** do not install rshell when py>=3.10 and on windows due to pyreadline.
-   **pkg:** win32 rshell python marker
-   **pkg:** upgrade too and pin jinja2 @ 3.0.3
-   **project:** report exception on install failure to stdout
-   **stubber:** replace pyminifer with python-minifer
-   **utils:** capture attribue err that occurs on py310 win32 rshell import
-   **utils:** utilize mp-stubbers new logic for generating stubs

### Features

-   **deps:** update dependencies scoped
-   **deps:** update micropython-stubber to latest master commit
-   **pkg:** move pytest+coverage cfg to pyproject
-   **pkg:** add missing packaging dep
-   **pkg:** update includes to be more strict
-   **pkg:** restructure and cleanup pyproject with dependency groups
-   **pkg:** merge create_stubs group into default

<a name="v3.6.0"></a>

## [v3.6.0] - 2021-05-17

### Bug Fixes

-   **data:** update stubs schema for compat with latest stubber

### Features

-   **deps:** update rshell dependency
-   **deps:** update deps, add micropy-cli w/ extras as dev-dep
-   **deps:** setup black, pre-commit
-   **pkg:** update setup file
-   **pre-commit:** add pre-commit config
-   **stubber:** update micropython-stubber submodule to latest
-   **utils:** remove dynamic
-   **utils:** refactor stub-gen to stubs, dynamically create stubber module for import

<a name="v3.5.0"></a>

## [v3.5.0] - 2020-11-17

<a name="v3.5.0.rc.1"></a>

## [v3.5.0.rc.1] - 2020-11-17

### Bug Fixes

-   full name case mismatch for pypi packages
-   package installation failures were silent
-   **pkg:** constrain questionary version to <1.8.0
-   **pkg:** setuptools editable installation issues

### Features

-   **package:** detect and return VCSDependencySource when needed in create dep source factory
-   **package:** add VCSDependencySource class for supporting VCS requirements
-   **package:** add attributes and logic for VCS packages
-   **pkg:** bump questionary dependency to ^1.8.1
-   **pkg:** add GitPython dependency

### Reverts

-   chore(deps): update setup.py

<a name="v3.4.0"></a>

## [v3.4.0] - 2020-07-25

### Bug Fixes

-   **deps:** update dpath constraint to >=1.4,<2.0

<a name="v3.3.0"></a>

## [v3.3.0] - 2019-12-23

### Bug Fixes

-   ensure any values to be extended in config are of type list ([#94](https://github.com/BradenM/micropy-cli/issues/94))
-   **utils:** ignore candidate releases when checking for update

### Features

-   **project:** generate recommended extensions with vscode integration ([#95](https://github.com/BradenM/micropy-cli/issues/95))

<a name="v3.2.0"></a>

## [v3.2.0] - 2019-12-14

<a name="v3.2.0.rc.2"></a>

## [v3.2.0.rc.2] - 2019-12-13

### Bug Fixes

-   Handle Invalid Requirements
-   **cli:** Handle errors when reading requirements from path
-   **cli:** Handle and Report Invalid Package Name Error
-   **deps:** Fix loading requirements from path
-   **utils:** Follow redirects when testing for valid url

### Code Refactoring

-   **deps:** Remove Exception handling from Packages Module

### Features

-   Add Base and Requirement Exceptions
-   **poetry:** Update Poetry to Stable

<a name="v3.2.0.rc.1"></a>

## [v3.2.0.rc.1] - 2019-12-09

### Bug Fixes

-   Make rshell and pyminifier requirements optional ([#82](https://github.com/BradenM/micropy-cli/issues/82))
-   Colorama Version Constraint
-   Colorama Broken Release, Style
-   VSCode Settings failed to populate on reload ([#81](https://github.com/BradenM/micropy-cli/issues/81))
-   **config:** Remove concrete path from ConfigSource
-   **config:** Remove cache method for better implementation later
-   **deps:** Temporary Directory would be removed before it was ready
-   **logger:** Exception formatting
-   **project:** Context not being updated when needed
-   **project:** Add empty dict to config on create

### Code Refactoring

-   Cleanup Stubs Module Context Handling
-   **packages:** Use new Dependency Api in Packages Module

### Features

-   **cli:** Basic install from path option implementation
-   **config:** Manage sync via callback
-   **config:** New Interface with file/memory autosync and dot notation
-   **config:** Dictionary Config Source
-   **config:** Cache and Root Key Context Manager for Config Items
-   **config:** Use dpath to handle Config paths and merging
-   **config:** Improved handling of collection data types
-   **config:** Add pop method to config
-   **config:** New and Improved Config File Interface
-   **context:** Use DictConfig for Project Context
-   **deps:** Package Class for representing a requirement
-   **deps:** Address Package Source Uniformly
-   **deps:** Allow local deps to be sourced from anywhere
-   **project:** Add local-lib-path config option.
-   **project:** Load Project Modules by individual Priority
-   **project:** Update Projects to use Priority Queue
-   **project:** Implement Dependencies in Project Module
-   **project:** Render Local Deps in Project Settings
-   **project:** Update Config/Context automatically
-   **project:** Update modules to use new, more flexible config
-   **project:** Use new Config Interface in Projects
-   **project:** Try to add local deps as relative to project, fallback...
-   **project:** Replace Project Cache with Config Instance
-   **template:** Update TemplateModule

### Performance Improvements

-   **size:** Slimmed Package Size

<a name="v3.1.1"></a>

## [v3.1.1] - 2019-12-03

### Bug Fixes

-   HookProxy failed to resolve with kwargs
-   **checks:** VSCode check failing on py36
-   **logger:** Exception formatting
-   **package:** Add metadata to pyproject.toml
-   **package:** Update Makefile and bump2version to use pyproject
-   **package:** Use Dephell to generate setup.py, Remove Manifiest.in
-   **project:** Exception Raised if no Templates are used in Project
-   **project:** VSCode check always failed silently

### Features

-   Cleanup Log File Formatting
-   Use Poetry for Dependency Management

### Performance Improvements

-   **size:** Slimmed Package Size

<a name="v3.1.0"></a>

## [v3.1.0] - 2019-11-12

### Bug Fixes

-   Handle Errors when adding Packages
-   Project Context Stub Path Ordering
-   HookProxy failed to work with descriptors.
-   PackagesModule Dev, Project Context
-   Move Template Check flag to TemplatesModule
-   Active Project Resolve, Cli Templates List

### Code Refactoring

-   Add Packages from File
-   Import MicroPy and Modules to Package Root
-   Restructure Project Module

### Features

-   Report Ready on Project Load, Code Cleanup
-   Write .gitignore file in generated .micropy folder
-   Proxy Project Hooks to allow hooks with the same name, Split De...
-   Resolve Project Hooks via attrs, Fix Stub List
-   **project:** Project Method Hook Decorator

### Performance Improvements

-   Lazy Load Project Stubs

<a name="v3.0.1"></a>

## [v3.0.1] - 2019-10-13

### Bug Fixes

-   Auto Update Check's Cache not expiring after update
-   VSCode Template Check always Fails on Linux ([#65](https://github.com/BradenM/micropy-cli/issues/65))
-   **upstream:** Fails to Generate Stub Files

<a name="v3.0.0"></a>

## [v3.0.0] - 2019-10-13

### Bug Fixes

-   Project Fails to Init due to Checks on Windows
-   Stub Package Url fails to resolve on Windows
-   Handle Chunked Content Length on Package Download
-   Package urls not resolving correctly
-   Fails to load Project if Template Files are Missing ([#55](https://github.com/BradenM/micropy-cli/issues/55))

### Code Refactoring

-   **data:** Move all Data Paths to Data Module

### Features

-   Add Flag for Skipping Template Checks
-   Search/Retrieve Stubs Directly from micropy-stubs
-   Update MicropyCli Stub Sources
-   Refactor MicroPy Class for Better State Management

### Performance Improvements

-   Lazy Load Stubs when Needed
-   **project:** Lazy Load Current Active Project

### BREAKING CHANGE

micropy.STUBS renamed to micropy.stubs

<a name="v2.2.0"></a>

## [v2.2.0] - 2019-09-28

### Features

-   Template Checks, MS-Python Check ([#52](https://github.com/BradenM/micropy-cli/issues/52))
-   **cli:** Automatic Update Checks ([#54](https://github.com/BradenM/micropy-cli/issues/54))
-   **vscode:** Ensure Jedi is Disabled in VSCode Template

### Performance Improvements

-   **stubs:** Cache Available Stubs for Searching

<a name="v2.1.1"></a>

## [v2.1.1] - 2019-09-22

### Bug Fixes

-   **hotfix:** Remove workspaceRoot var from VSCode Settings ([#51](https://github.com/BradenM/micropy-cli/issues/51))

### Features

-   Relicensed under MIT

### BREAKING CHANGE

No longer compatible with <=ms-python.python[@2019](https://github.com/2019).8.30787 VSCode Extension

<a name="v2.1.0"></a>

## [v2.1.0] - 2019-09-01

### Bug Fixes

-   **project:** Requirement Files skipped on First Init
-   **windows:** Support User Level Directory Linking ([#45](https://github.com/BradenM/micropy-cli/issues/45))

### Features

-   **log:** Cap Log File at 2MB
-   **project:** Init Project with Micropy Dev Dependency
-   **project:** Git Ignore Template Option

<a name="v2.0.2"></a>

## [v2.0.2] - 2019-08-21

### Bug Fixes

-   **dep:** Require appropriate Click version
-   **windows:** Warn User if MicroPy Lacks Admin Privs

<a name="v2.0.1"></a>

## [v2.0.1] - 2019-07-26

### Bug Fixes

-   **stubs:** Reduce Schema Strictness

<a name="v2.0.0"></a>

## [v2.0.0] - 2019-07-25

### Bug Fixes

-   **dep:** Broken Docutils Dependency
-   **project:** Only modules install correctly

### Features

-   Add Optional Pyminifier Dep for Stub Creation
-   **cli:** Install Python Packages for Project
-   **cli:** Verbosity Flag for Stub Creation
-   **dep:** Update Tox to latest
-   **dep:** Packaging Module Requirement
-   **lib:** Update Stubber to Process Branch
-   **project:** Update requirements.txt Files on Install
-   **project:** Template Update Functionality
-   **project:** Install from Requirements.txt
-   **project:** Retrieve and Stub Project Requirements
-   **project:** Project Config in Info File
-   **project:** Make Templates Optional via CLI ([#30](https://github.com/BradenM/micropy-cli/issues/30))
-   **pyb:** Handle Pyboard Output and Errors
-   **stubs:** Minify Stubber Before Executing
-   **util:** Generate Stub from File Utility

<a name="v1.1.3"></a>

## [v1.1.3] - 2019-07-20

### Bug Fixes

-   ValueError raised after Creating Project in Windows ([#33](https://github.com/BradenM/micropy-cli/issues/33))
-   Unicode Error raised when logging on Windows ([#32](https://github.com/BradenM/micropy-cli/issues/32))

<a name="v1.1.2"></a>

## [v1.1.2] - 2019-07-19

### Bug Fixes

-   **stubs:** Ensure Firmware Stubs Load First

<a name="v1.1.1"></a>

## [v1.1.1] - 2019-07-17

### Bug Fixes

-   Temp Hotfix for False Stub Duplication

<a name="v1.1.0"></a>

## [v1.1.0] - 2019-07-16

### Bug Fixes

-   **cli:** Stub List always prints Unknown
-   **cli:** Made Stub Search Case Insensitive
-   **stubs:** FileExistsError when adding existing Stub

### Features

-   **cli:** List Project Stubs if in Project Directory
-   **cli:** Stubs now list by Firmware
-   **cli:** Create Formatted Strings from Logger
-   **cli:** Added --force flag when adding stubs
-   **project:** Micropy Project Info File ([#29](https://github.com/BradenM/micropy-cli/issues/29))
-   **project:** Micropy Project Folder ([#28](https://github.com/BradenM/micropy-cli/issues/28))

<a name="v1.0.0"></a>

## [v1.0.0] - 2019-07-11

### Bug Fixes

-   **cli:** Init Crashes if no Stubs are Loaded
-   **cli:** Create Stubs Help Formatting
-   **log:** Output Highlight Bug, Cleanup
-   **stub:** Stub Name without Firmware
-   **stubs:** Firmware not showing as Installed in Stub Search
-   **stubs:** Fix Existing Firmware Reinstall

### Features

-   Implemented Local and Remote Stub Sources ([#18](https://github.com/BradenM/micropy-cli/issues/18))
-   **cli:** Minified Cli Output Style
-   **cli:** Search Available Stubs ([#27](https://github.com/BradenM/micropy-cli/issues/27))
-   **cli:** Stream Downloads with Progress Bar
-   **stub:** Update Stubs to Use New Stubber Schema ([#23](https://github.com/BradenM/micropy-cli/issues/23))
-   **stubs:** Updated micropython-stubber to latest
-   **stubs:** Add Firmware Frozen Modules to Templates
-   **stubs:** Device Stubs Firmware Resolution ([#25](https://github.com/BradenM/micropy-cli/issues/25))
-   **stubs:** Add Device Frozen Modules to Templates ([#24](https://github.com/BradenM/micropy-cli/issues/24))
-   **stubs:** Added Stub Stdout Verbosity
-   **stubs:** Add Stubs from Repositories ([#21](https://github.com/BradenM/micropy-cli/issues/21))
-   **stubs:** Replaced Stubs with Stub "Packages"
-   **stubs:** Stub Repositories ([#20](https://github.com/BradenM/micropy-cli/issues/20))
-   **stubs:** Update Stub Creation ([#26](https://github.com/BradenM/micropy-cli/issues/26))
-   **util:** Generic Utility Functions and Module Cleanup

### Performance Improvements

-   **cli:** Only Instantiate MicroPy when needed

<a name="v0.3.0"></a>

## [v0.3.0] - 2019-06-25

### Code Refactoring

-   MicroPy to use new Stub and Utility Features ([#14](https://github.com/BradenM/micropy-cli/issues/14))

### Features

-   **cli:** Version Flag
-   **log:** New Cli Output Style, Log Class Methods
-   **pyb:** PyboardWrapper Utility ([#13](https://github.com/BradenM/micropy-cli/issues/13))
-   **stubs:** Stub Manager ([#5](https://github.com/BradenM/micropy-cli/issues/5))
-   **utils:** Utils Module and Validator Utility ([#4](https://github.com/BradenM/micropy-cli/issues/4))

<a name="v0.2.0"></a>

## [v0.2.0] - 2019-06-14

### Features

-   **log:** Added Proper Log Formatting, cleaned messages before write.
-   **log:** Added Logging to Template Module
-   **project:** Drop Cookiecutter for Purely Jinja2 ([#3](https://github.com/BradenM/micropy-cli/issues/3))

<a name="v0.1.1"></a>

## [v0.1.1] - 2019-06-10

### Bug Fixes

-   **setup:** Fixed missing cookiecutter package requirement
-   **setup:** Fixed Pypi misinformation, cleaned up dist-management files
-   **setup:** Fix Missing .vscode Template Files

<a name="v0.1.0"></a>

## v0.1.0 - 2019-06-09

### Bug Fixes

-   Fails First Time Setup Failed to init on first run if the stubs folder didnt exist
-   Removed old command
-   Fix Project Init
-   Added rshell to setup.py
-   Quick Fix before Project Class Restructure
-   Packaging Fixes
-   **package:** Allow multiple versions of python, Update Reqs
-   **setup:** Included Template in Manifest
-   **stub:** Fixed Refresh Stubs
-   **stubs:** Cleaned Stub Names before Adding
-   **stubs:** Removed Old Stub Command
-   **stubs:** Fixed missing logging.py
-   **template:** Fixed src template

### Code Refactoring

-   Setup as proper package

### Features

-   Project Init and Template Serialization
-   Finished Package Setup and Structure
-   Let Stub class handle validation and files
-   Setup Template Files
-   Initial commit
-   Add Josverl Stubs on First Setup, Restructured MicroPy
-   Added MicroPy Parent Class
-   Added stubber as submodule over pulling files with requests
-   **log:** Added Silet Stdout Context Manager to Logger
-   **log:** Setup ServiceLog to work as a single parent Logger with ch...
-   **log:** Added Logging
-   **log:** Setup Logger as Borg for easy access
-   **log:** Added file logging to ServiceLog, Added docs
-   **project:** Project Module Rewrite to use Cookiecutter and JSON
-   **pylint:** Added checkbox to choose stubs for pylint
-   **stub:** Pass Multiple Stubs to .pylintrc
-   **stub:** Added stub add, refresh commands
-   **stub:** Added createstub.py download
-   **stub:** Added Stub Class, Moved Stub logic to MicroPy/Stub
-   **stubs:** Added Automated Stub Creation on PyBoard
-   **stubs:** Added Stub Validation, Stub Class Restructure
-   **stubs:** Added Basic Stub Exceptions
-   **template:** Setup Template in Cookiecutter Fashion

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
