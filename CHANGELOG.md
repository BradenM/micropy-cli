## [3.5.0](https://github.com/BradenM/micropy-cli/compare/v3.4.0...v3.5.0) (2020-11-17)


#### Features

* **project:**
  *  Update pylint template with better syntax and inclusions. Thanks @josverl! (#174)
  *  Track changes in src/lib. Thanks @askpatrickw! ([e8707cf0f](https://github.com/BradenM/micropy-cli/commit/e8707cf0f4a71aea6ca9b6bc4d035480bf212764)) (#137)
* **package:**
  *  detect and return VCSDependencySource when needed in create dep source factory ([7b0b40b0](https://github.com/BradenM/micropy-cli/commit/7b0b40b04f8059a3cc4476bccfcf9e6cec5b615f))
  *  add VCSDependencySource class for supporting VCS requirements ([e590ea6c](https://github.com/BradenM/micropy-cli/commit/e590ea6c1806d0405da739e23fea7ad8a534d15e))
  *  add attributes and logic for VCS packages ([e78d32c5](https://github.com/BradenM/micropy-cli/commit/e78d32c5d47d4809e9566b5e91fa3447142f8236))
* **pkg:**
  *  bump questionary dependency to ^1.8.1 ([585a5b95](https://github.com/BradenM/micropy-cli/commit/585a5b9559e0450f514439d47b63d5281f1d053d))
  *  add GitPython dependency ([263ae07a](https://github.com/BradenM/micropy-cli/commit/263ae07a2fec97c845fe385accbce98de4b8eb71))
  *  add VSCode debugging config. Thanks @josverl! (#174)
  

#### Bug Fixes

*   full name case mismatch for pypi packages ([7bb976d5](https://github.com/BradenM/micropy-cli/commit/7bb976d594e00ce2d1390c7fb371c068148eaee4))
*   package installation failures were silent ([d21bb2fc](https://github.com/BradenM/micropy-cli/commit/d21bb2fc7618504a93dbc38b0e6630a7fee9f54d))
* **pkg:**
  *  setuptools editable installation issues ([525b4b0f](https://github.com/BradenM/micropy-cli/commit/525b4b0f769163b88a1cb21d499f49ade3872fac))



## [3.4.0](https://github.com/BradenM/micropy-cli/compare/v3.3.0...v3.4.0) (2020-07-25)


### Bug Fixes

* **project:** OSError thrown on filesystems where neither symlinks/hardlinks are supported (such as exFAT). Thanks @lemariva! ([#105](https://github.com/BradenM/micropy-cli/issues/105)) ([b6f8efc](https://github.com/BradenM/micropy-cli/commit/b6f8efc2108006bf347b8360993e270713eb0c8d)), closes [#104](https://github.com/BradenM/micropy-cli/issues/104)
* **project:** Micropy overwrites pre-existing vscode settings when adding to workspace. Thanks @askpatrickw! ([#112](https://github.com/BradenM/micropy-cli/issues/112)) ([08f6d21](https://github.com/BradenM/micropy-cli/commit/08f6d216c4b343f5de302db36ce55488e5b9b988)), closes [#108](https://github.com/BradenM/micropy-cli/issues/108)
* **deps:** Fix dpath dependency constraint to >=1.4,<2.0. ([#153](https://github.com/BradenM/micropy-cli/issues/153)) ([3d0ac5d](https://github.com/BradenM/micropy-cli/commit/3d0ac5d8307278736348d220d009d0a4cc66a793))


### Features

* **package:** Officially support Python 3.8 and update minor versions. Thanks @askpatrickw! ([#113](https://github.com/BradenM/micropy-cli/issues/113)) ([4943326](https://github.com/BradenM/micropy-cli/commit/494332662da46a4f3005b0d8688f1dabfbbec3a9)), closes [#109](https://github.com/BradenM/micropy-cli/issues/109)
* **deps:** Update click, dpath, pytest-cov, cachier, tox, requests, and more.



## [3.3.0](https://github.com/BradenM/micropy-cli/compare/v3.2.0...v) (2019-12-23)


### Bug Fixes

* **config:** Ensure any values to be extended in config are of type list ([#94](https://github.com/BradenM/micropy-cli/issues/94)) ([0da09fa](https://github.com/BradenM/micropy-cli/commit/0da09fa)), closes [#92](https://github.com/BradenM/micropy-cli/issues/92)
* **utils:** Ignore candidate releases when checking for update ([8ce6686](https://github.com/BradenM/micropy-cli/commit/8ce6686))


### Features

* **project:** Generate recommended extensions with vscode integration ([#95](https://github.com/BradenM/micropy-cli/issues/95)) ([eff9c59](https://github.com/BradenM/micropy-cli/commit/eff9c59)), closes [#84](https://github.com/BradenM/micropy-cli/issues/84)



## [3.2.0](https://github.com/BradenM/micropy-cli/compare/v3.1.1...v) (2019-12-09)


### Bug Fixes

* **cli:** Handle and Report Invalid Package Name Error ([d8b2b06](https://github.com/BradenM/micropy-cli/commit/d8b2b06)), closes [#85](https://github.com/BradenM/micropy-cli/issues/85)
* **cli:** Handle errors when reading requirements from path ([dfb9390](https://github.com/BradenM/micropy-cli/commit/dfb9390)), closes [#86](https://github.com/BradenM/micropy-cli/issues/86)
* **deps:** Fix loading requirements from path ([850f37e](https://github.com/BradenM/micropy-cli/commit/850f37e))
* **utils:** Follow redirects when testing for valid url ([abf8dfc](https://github.com/BradenM/micropy-cli/commit/abf8dfc))
* Colorama Version Constraint ([f9269c8](https://github.com/BradenM/micropy-cli/commit/f9269c8))
* Make rshell and pyminifier requirements optional ([#82](https://github.com/BradenM/micropy-cli/issues/82)) ([c004dcb](https://github.com/BradenM/micropy-cli/commit/c004dcb))
* **config:** Remove cache method for better implementation later ([7e637e3](https://github.com/BradenM/micropy-cli/commit/7e637e3))
* **project:** Populate Config with Empty Values on creation ([9e93ff7](https://github.com/BradenM/micropy-cli/commit/9e93ff7))
* **project:** Context not being updated when needed ([0210034](https://github.com/BradenM/micropy-cli/commit/0210034))


### Features

* **poetry:** Update Poetry to Stable ([2a8b75e](https://github.com/BradenM/micropy-cli/commit/2a8b75e))
* **cli:** Add Local Project Requirements by path ([fb4b898](https://github.com/BradenM/micropy-cli/commit/fb4b898))
* **config:** New and Improved Config File Interface ([ee26641](https://github.com/BradenM/micropy-cli/commit/ee26641))
* **config:** Config file/memory autosync and dot notation ([88f30cc](https://github.com/BradenM/micropy-cli/commit/88f30cc))
* **context:** In-memory DictConfig for Project Context ([a83d5f7](https://github.com/BradenM/micropy-cli/commit/a83d5f7))
* **deps:** Address Package Source Uniformly ([ef95c85](https://github.com/BradenM/micropy-cli/commit/ef95c85))
* **deps:** Allow absolute or relative local requirements ([2d2c97f](https://github.com/BradenM/micropy-cli/commit/2d2c97f))
* **deps:** New Package API for requirement handling ([c77d56f](https://github.com/BradenM/micropy-cli/commit/c77d56f))
* **project:** Load Project Modules by Priority Queue ([462dd93](https://github.com/BradenM/micropy-cli/commit/462dd93))
* **project:** Render Local Deps in Project Settings ([7c38ee9](https://github.com/BradenM/micropy-cli/commit/7c38ee9))
* **project:** Update Config/Context automatically ([dbd4276](https://github.com/BradenM/micropy-cli/commit/dbd4276))

### Performance Improvements

* **project:** Replace Project Cache with Config Instance ([ff6f3db](https://github.com/BradenM/micropy-cli/commit/ff6f3db))



## [3.1.1](https://github.com/BradenM/micropy-cli/compare/v3.1.0...v3.1.1) (2019-12-03)


### Bug Fixes

* HookProxy failed to resolve with kwargs ([02f9462](https://github.com/BradenM/micropy-cli/commit/02f9462))
* **checks:** VSCode check failing on py36 ([31452bb](https://github.com/BradenM/micropy-cli/commit/31452bb))
* **logger:** Exception formatting ([1274ff8](https://github.com/BradenM/micropy-cli/commit/1274ff8))
* **package:** Add metadata to pyproject.toml ([bc06d90](https://github.com/BradenM/micropy-cli/commit/bc06d90))
* **package:** Update Makefile and bump2version to use pyproject ([359a42e](https://github.com/BradenM/micropy-cli/commit/359a42e))
* **package:** Use Dephell to generate setup.py, Remove Manifest.in ([02b5171](https://github.com/BradenM/micropy-cli/commit/02b5171))
* **project:** Exception Raised if no Templates are used in Project ([43a09eb](https://github.com/BradenM/micropy-cli/commit/43a09eb)), closes [#78](https://github.com/BradenM/micropy-cli/issues/78)
* **project:** VSCode check always failed silently ([e488519](https://github.com/BradenM/micropy-cli/commit/e488519))


### Features

* Cleanup Log File Formatting ([0a560f4](https://github.com/BradenM/micropy-cli/commit/0a560f4))
* Use Poetry for Dependency Management ([3cb06f9](https://github.com/BradenM/micropy-cli/commit/3cb06f9))


### Performance Improvements

* **size:** Slimmed Package Size ([2dc1a6e](https://github.com/BradenM/micropy-cli/commit/2dc1a6e))



# [3.1.0](https://github.com/BradenM/micropy-cli/compare/v3.0.1...v3.1.0) (2019-11-13)


### Bug Fixes

* Active Project Resolve, Cli Templates List ([7940e9c](https://github.com/BradenM/micropy-cli/commit/7940e9c))
* Handle Errors when adding Packages ([6a3272d](https://github.com/BradenM/micropy-cli/commit/6a3272d)), closes [#68](https://github.com/BradenM/micropy-cli/issues/68)
* HookProxy failed to work with descriptors. ([525b1ac](https://github.com/BradenM/micropy-cli/commit/525b1ac))
* Move Template Check flag to TemplatesModule ([49f37f5](https://github.com/BradenM/micropy-cli/commit/49f37f5))
* PackagesModule Dev, Project Context ([d98b99e](https://github.com/BradenM/micropy-cli/commit/d98b99e))
* Project Context Stub Path Ordering ([1cafa5a](https://github.com/BradenM/micropy-cli/commit/1cafa5a))


### Features

* Proxy Project Hooks to allow hooks with the same name, Split De... ([0993678](https://github.com/BradenM/micropy-cli/commit/0993678))
* Report Ready on Project Load, Code Cleanup ([e5769b0](https://github.com/BradenM/micropy-cli/commit/e5769b0))
* Resolve Project Hooks via attrs, Fix Stub List ([773d95c](https://github.com/BradenM/micropy-cli/commit/773d95c))
* Write .gitignore file in generated .micropy folder ([d2d0c5f](https://github.com/BradenM/micropy-cli/commit/d2d0c5f))
* **project:** Project Method Hook Decorator ([df85408](https://github.com/BradenM/micropy-cli/commit/df85408))


### Performance Improvements

* Lazy Load Project Stubs ([82d2a3c](https://github.com/BradenM/micropy-cli/commit/82d2a3c))



## [3.0.1](https://github.com/BradenM/micropy-cli/compare/v3.0.0...v3.0.1) (2019-10-14)


### Bug Fixes

* Auto Update Check's Cache not expiring after update ([db5daca](https://github.com/BradenM/micropy-cli/commit/db5daca))
* **upstream:** Fails to Generate Stub Files ([55a03eb](https://github.com/BradenM/micropy-cli/commit/55a03eb))
* VSCode Template Check always Fails on Linux ([#65](https://github.com/BradenM/micropy-cli/issues/65)) ([6e712da](https://github.com/BradenM/micropy-cli/commit/6e712da))



# [3.0.0](https://github.com/BradenM/micropy-cli/compare/v2.2.0...v3.0.0) (2019-10-13)


### Bug Fixes

* Fails to load Project if Template Files are Missing ([#55](https://github.com/BradenM/micropy-cli/issues/55)) ([f8c14c9](https://github.com/BradenM/micropy-cli/commit/f8c14c9))
* Handle Chunked Content Length on Package Download ([f1dfe5a](https://github.com/BradenM/micropy-cli/commit/f1dfe5a))
* Package urls not resolving correctly ([55f3d34](https://github.com/BradenM/micropy-cli/commit/55f3d34))
* Project Fails to Init due to Checks on Windows ([06b894f](https://github.com/BradenM/micropy-cli/commit/06b894f)), closes [#59](https://github.com/BradenM/micropy-cli/issues/59)
* Stub Package Url fails to resolve on Windows ([3397465](https://github.com/BradenM/micropy-cli/commit/3397465))


### Features

* Add Flag for Skipping Template Checks ([863c97c](https://github.com/BradenM/micropy-cli/commit/863c97c))
* Refactor MicroPy Class for Better State Management ([711244b](https://github.com/BradenM/micropy-cli/commit/711244b))
* Search/Retrieve Stubs Directly from micropy-stubs ([0717f37](https://github.com/BradenM/micropy-cli/commit/0717f37))
* Update MicropyCli Stub Sources ([437d32e](https://github.com/BradenM/micropy-cli/commit/437d32e))


### Performance Improvements

* Lazy Load Stubs when Needed ([bd24ada](https://github.com/BradenM/micropy-cli/commit/bd24ada))
* **project:** Lazy Load Current Active Project ([54b33d5](https://github.com/BradenM/micropy-cli/commit/54b33d5))


### BREAKING CHANGES

* micropy.STUBS renamed to micropy.stubs



# [2.2.0](https://github.com/BradenM/micropy-cli/compare/v2.1.1...v2.2.0) (2019-09-28)


### Features

* **cli:** Automatic Update Checks ([#54](https://github.com/BradenM/micropy-cli/issues/54)) ([1f33abe](https://github.com/BradenM/micropy-cli/commit/1f33abe))
* **vscode:** Ensure Jedi is Disabled in VSCode Template ([efce877](https://github.com/BradenM/micropy-cli/commit/efce877))
* Template Checks, MS-Python Check ([#52](https://github.com/BradenM/micropy-cli/issues/52)) ([fc151f6](https://github.com/BradenM/micropy-cli/commit/fc151f6))


### Performance Improvements

* **stubs:** Cache Available Stubs for Searching ([998b125](https://github.com/BradenM/micropy-cli/commit/998b125))



## [2.1.1](https://github.com/BradenM/micropy-cli/compare/v2.1.0...v2.1.1) (2019-09-22)


### Bug Fixes

* **hotfix:** Remove workspaceRoot var from VSCode Settings ([#51](https://github.com/BradenM/micropy-cli/issues/51)) ([d4ddf13](https://github.com/BradenM/micropy-cli/commit/d4ddf13)), closes [#50](https://github.com/BradenM/micropy-cli/issues/50)


### Features

* Relicensed under MIT ([f2f191b](https://github.com/BradenM/micropy-cli/commit/f2f191b))


### BREAKING CHANGES

* **hotfix:** No longer compatible with <=ms-python.python@2019.8.30787 VSCode Extension



# [2.1.0](https://github.com/BradenM/micropy-cli/compare/v2.0.2...v2.1.0) (2019-09-01)


### Bug Fixes

* **project:** Requirement Files skipped on First Init ([25decf8](https://github.com/BradenM/micropy-cli/commit/25decf8))
* **windows:** Support User Level Directory Linking ([#45](https://github.com/BradenM/micropy-cli/issues/45)) ([d67aea8](https://github.com/BradenM/micropy-cli/commit/d67aea8))


### Features

* **log:** Cap Log File at 2MB ([2d8ad6d](https://github.com/BradenM/micropy-cli/commit/2d8ad6d))
* **project:** Git Ignore Template Option ([12ce75c](https://github.com/BradenM/micropy-cli/commit/12ce75c))
* **project:** Init Project with Micropy Dev Dependency ([1d2fac8](https://github.com/BradenM/micropy-cli/commit/1d2fac8))



## [2.0.2](https://github.com/BradenM/micropy-cli/compare/v2.0.1...v2.0.2) (2019-08-21)


### Bug Fixes

* **dep:** Require appropriate Click version ([6f75e19](https://github.com/BradenM/micropy-cli/commit/6f75e19)), closes [#40](https://github.com/BradenM/micropy-cli/issues/40)
* **windows:** Warn User if MicroPy Lacks Admin Privs ([9e8f314](https://github.com/BradenM/micropy-cli/commit/9e8f314))



## [2.0.1](https://github.com/BradenM/micropy-cli/compare/v2.0.0...v2.0.1) (2019-07-26)


### Bug Fixes

* **stubs:** Reduce Schema Strictness ([9343ba1](https://github.com/BradenM/micropy-cli/commit/9343ba1))



# [2.0.0](https://github.com/BradenM/micropy-cli/compare/v1.1.3...v2.0.0) (2019-07-26)


### Bug Fixes

* **dep:** Broken Docutils Dependency ([ecfc741](https://github.com/BradenM/micropy-cli/commit/ecfc741))
* **project:** Only modules install correctly ([87fe8ef](https://github.com/BradenM/micropy-cli/commit/87fe8ef))


### Features

* **cli:** Verbosity Flag for Stub Creation ([f93c8b1](https://github.com/BradenM/micropy-cli/commit/f93c8b1))
* Add Optional Pyminifier Dep for Stub Creation ([befa440](https://github.com/BradenM/micropy-cli/commit/befa440))
* **cli:** Install Python Packages for Project ([16cd13c](https://github.com/BradenM/micropy-cli/commit/16cd13c))
* **dep:** Packaging Module Requirement ([36992f7](https://github.com/BradenM/micropy-cli/commit/36992f7))
* **dep:** Update Tox to latest ([177f759](https://github.com/BradenM/micropy-cli/commit/177f759))
* **lib:** Update Stubber to Process Branch ([da9fb6b](https://github.com/BradenM/micropy-cli/commit/da9fb6b))
* **project:** Install from Requirements.txt ([ac236c6](https://github.com/BradenM/micropy-cli/commit/ac236c6))
* **project:** Make Templates Optional via CLI ([#30](https://github.com/BradenM/micropy-cli/issues/30)) ([eb460d3](https://github.com/BradenM/micropy-cli/commit/eb460d3))
* **project:** Project Config in Info File ([2260015](https://github.com/BradenM/micropy-cli/commit/2260015))
* **project:** Retrieve and Stub Project Requirements ([0ecf6af](https://github.com/BradenM/micropy-cli/commit/0ecf6af))
* **project:** Template Update Functionality ([f4b91f7](https://github.com/BradenM/micropy-cli/commit/f4b91f7))
* **project:** Update requirements.txt Files on Install ([00f5a92](https://github.com/BradenM/micropy-cli/commit/00f5a92))
* **pyb:** Handle Pyboard Output and Errors ([26136c6](https://github.com/BradenM/micropy-cli/commit/26136c6))
* **stubs:** Minify Stubber Before Executing ([2b6cdd2](https://github.com/BradenM/micropy-cli/commit/2b6cdd2))
* **util:** Generate Stub from File Utility ([aac79e3](https://github.com/BradenM/micropy-cli/commit/aac79e3))



## [1.1.3](https://github.com/BradenM/micropy-cli/compare/v1.1.2...v1.1.3) (2019-07-20)


### Bug Fixes

* Unicode Error raised when logging on Windows ([#32](https://github.com/BradenM/micropy-cli/issues/32)) ([2eb5a45](https://github.com/BradenM/micropy-cli/commit/2eb5a45)), closes [#31](https://github.com/BradenM/micropy-cli/issues/31)
* ValueError raised after Creating Project in Windows ([#33](https://github.com/BradenM/micropy-cli/issues/33)) ([ac1c0f7](https://github.com/BradenM/micropy-cli/commit/ac1c0f7))



## [1.1.2](https://github.com/BradenM/micropy-cli/compare/v1.1.1...v1.1.2) (2019-07-19)


### Bug Fixes

* **stubs:** Ensure Firmware Stubs Load First ([0c50d9a](https://github.com/BradenM/micropy-cli/commit/0c50d9a))



## [1.1.1](https://github.com/BradenM/micropy-cli/compare/v1.1.0...v1.1.1) (2019-07-17)


### Bug Fixes

* Temp Hotfix for False Stub Duplication ([49e4ad2](https://github.com/BradenM/micropy-cli/commit/49e4ad2))



# [1.1.0](https://github.com/BradenM/micropy-cli/compare/v1.0.0...v1.1.0) (2019-07-17)


### Bug Fixes

* **cli:** Made Stub Search Case Insensitive ([f7144c7](https://github.com/BradenM/micropy-cli/commit/f7144c7))
* **cli:** Stub List always prints Unknown ([52d2045](https://github.com/BradenM/micropy-cli/commit/52d2045))
* **stubs:** FileExistsError when adding existing Stub ([f9858f9](https://github.com/BradenM/micropy-cli/commit/f9858f9))


### Features

* **cli:** Added --force flag when adding stubs ([618adbf](https://github.com/BradenM/micropy-cli/commit/618adbf))
* **cli:** Create Formatted Strings from Logger ([58ee3ec](https://github.com/BradenM/micropy-cli/commit/58ee3ec))
* **cli:** List Project Stubs if in Project Directory ([71eb0ce](https://github.com/BradenM/micropy-cli/commit/71eb0ce))
* **cli:** Stubs now list by Firmware ([34271b9](https://github.com/BradenM/micropy-cli/commit/34271b9))
* **project:** Micropy Project Folder ([#28](https://github.com/BradenM/micropy-cli/issues/28)) ([977ff1f](https://github.com/BradenM/micropy-cli/commit/977ff1f))
* **project:** Micropy Project Info File ([#29](https://github.com/BradenM/micropy-cli/issues/29)) ([49420ca](https://github.com/BradenM/micropy-cli/commit/49420ca)), closes [#9](https://github.com/BradenM/micropy-cli/issues/9)



# [1.0.0](https://github.com/BradenM/micropy-cli/compare/v0.3.0...v1.0.0) (2019-07-11)


### Bug Fixes

* **cli:** Create Stubs Help Formatting ([4439ebe](https://github.com/BradenM/micropy-cli/commit/4439ebe))
* **cli:** Init Crashes if no Stubs are Loaded ([b145733](https://github.com/BradenM/micropy-cli/commit/b145733))
* **log:** Output Highlight Bug, Cleanup ([fd6b243](https://github.com/BradenM/micropy-cli/commit/fd6b243))
* **stub:** Stub Name without Firmware ([94f5f78](https://github.com/BradenM/micropy-cli/commit/94f5f78))
* **stubs:** Firmware not showing as Installed in Stub Search ([db1f74a](https://github.com/BradenM/micropy-cli/commit/db1f74a))
* **stubs:** Fix Existing Firmware Reinstall ([5c8e026](https://github.com/BradenM/micropy-cli/commit/5c8e026))


### Features

* **cli:** Minified Cli Output Style ([2435097](https://github.com/BradenM/micropy-cli/commit/2435097))
* **cli:** Search Available Stubs ([#27](https://github.com/BradenM/micropy-cli/issues/27)) ([1622a61](https://github.com/BradenM/micropy-cli/commit/1622a61))
* **cli:** Stream Downloads with Progress Bar ([b3d1401](https://github.com/BradenM/micropy-cli/commit/b3d1401))
* **stub:** Update Stubs to Use New Stubber Schema ([#23](https://github.com/BradenM/micropy-cli/issues/23)) ([f55b5da](https://github.com/BradenM/micropy-cli/commit/f55b5da)), closes [Josverl/micropython-stubber#4](https://github.com/Josverl/micropython-stubber/issues/4)
* **stubs:** Add Device Frozen Modules to Templates ([#24](https://github.com/BradenM/micropy-cli/issues/24)) ([218c41c](https://github.com/BradenM/micropy-cli/commit/218c41c))
* **stubs:** Add Firmware Frozen Modules to Templates ([5452756](https://github.com/BradenM/micropy-cli/commit/5452756))
* **stubs:** Add Stubs from Repositories ([#21](https://github.com/BradenM/micropy-cli/issues/21)) ([df9fde5](https://github.com/BradenM/micropy-cli/commit/df9fde5))
* **stubs:** Added Stub Stdout Verbosity ([6533866](https://github.com/BradenM/micropy-cli/commit/6533866))
* **stubs:** Device Stubs Firmware Resolution ([#25](https://github.com/BradenM/micropy-cli/issues/25)) ([b9a2357](https://github.com/BradenM/micropy-cli/commit/b9a2357))
* **stubs:** Replaced Stubs with Stub "Packages" ([8111618](https://github.com/BradenM/micropy-cli/commit/8111618))
* **stubs:** Stub Repositories ([#20](https://github.com/BradenM/micropy-cli/issues/20)) ([58acfe7](https://github.com/BradenM/micropy-cli/commit/58acfe7))
* **stubs:** Update Stub Creation ([#26](https://github.com/BradenM/micropy-cli/issues/26)) ([4f1f5bc](https://github.com/BradenM/micropy-cli/commit/4f1f5bc))
* **stubs:** Updated micropython-stubber to latest ([d927e60](https://github.com/BradenM/micropy-cli/commit/d927e60))
* Implemented Local and Remote Stub Sources ([#18](https://github.com/BradenM/micropy-cli/issues/18)) ([98ab23e](https://github.com/BradenM/micropy-cli/commit/98ab23e))
* **util:** Generic Utility Functions and Module Cleanup ([6e06654](https://github.com/BradenM/micropy-cli/commit/6e06654))


### Performance Improvements

* **cli:** Only Instantiate MicroPy when needed ([865afd6](https://github.com/BradenM/micropy-cli/commit/865afd6))



# [0.3.0](https://github.com/BradenM/micropy-cli/compare/v0.2.0...v0.3.0) (2019-06-26)


### Features

* **cli:** Version Flag ([0f9abf1](https://github.com/BradenM/micropy-cli/commit/0f9abf1))
* **log:** New Cli Output Style, Log Class Methods ([0b257e6](https://github.com/BradenM/micropy-cli/commit/0b257e6))
* **pyb:** PyboardWrapper Utility ([#13](https://github.com/BradenM/micropy-cli/issues/13)) ([5f7d2cf](https://github.com/BradenM/micropy-cli/commit/5f7d2cf))
* **stubs:** Stub Manager ([#5](https://github.com/BradenM/micropy-cli/issues/5)) ([097b452](https://github.com/BradenM/micropy-cli/commit/097b452))
* **utils:** Utils Module and Validator Utility  ([#4](https://github.com/BradenM/micropy-cli/issues/4)) ([be2c9c6](https://github.com/BradenM/micropy-cli/commit/be2c9c6))



# [0.2.0](https://github.com/BradenM/micropy-cli/compare/v0.1.1...v0.2.0) (2019-06-14)


### Features

* **log:** Added Logging to Template Module ([2e3f51a](https://github.com/BradenM/micropy-cli/commit/2e3f51a))
* **log:** Added Proper Log Formatting, cleaned messages before write. ([6c2fb25](https://github.com/BradenM/micropy-cli/commit/6c2fb25))
* **project:** Drop Cookiecutter for Purely Jinja2 ([#3](https://github.com/BradenM/micropy-cli/issues/3)) ([ef2d0ef](https://github.com/BradenM/micropy-cli/commit/ef2d0ef))



## [0.1.1](https://github.com/BradenM/micropy-cli/compare/v0.1.0...v0.1.1) (2019-06-10)


### Bug Fixes

* **setup:** Fix Missing .vscode Template Files ([806ce7c](https://github.com/BradenM/micropy-cli/commit/806ce7c))
* **setup:** Fixed missing cookiecutter package requirement ([22ab97c](https://github.com/BradenM/micropy-cli/commit/22ab97c))
* **setup:** Fixed Pypi misinformation, cleaned up dist-management files ([e662407](https://github.com/BradenM/micropy-cli/commit/e662407))



# [0.1.0](https://github.com/BradenM/micropy-cli/compare/0030fdd...v0.1.0) (2019-06-09)


### Bug Fixes

* Added rshell to setup.py ([ee3a232](https://github.com/BradenM/micropy-cli/commit/ee3a232))
* Fails First Time Setup ([7fad6ab](https://github.com/BradenM/micropy-cli/commit/7fad6ab))
* Fix Project Init ([e60b2fe](https://github.com/BradenM/micropy-cli/commit/e60b2fe))
* Packaging Fixes ([29af2d6](https://github.com/BradenM/micropy-cli/commit/29af2d6))
* Quick Fix before Project Class Restructure ([fafd2ac](https://github.com/BradenM/micropy-cli/commit/fafd2ac))
* Removed old command ([a80dbac](https://github.com/BradenM/micropy-cli/commit/a80dbac))
* **package:** Allow multiple versions of python, Update Reqs ([aaebc88](https://github.com/BradenM/micropy-cli/commit/aaebc88))
* **setup:** Included Template in Manifest ([868a49f](https://github.com/BradenM/micropy-cli/commit/868a49f))
* **stub:** Fixed Refresh Stubs ([78674e9](https://github.com/BradenM/micropy-cli/commit/78674e9))
* **stubs:** Cleaned Stub Names before Adding ([ceb608f](https://github.com/BradenM/micropy-cli/commit/ceb608f))
* **stubs:** Fixed missing logging.py ([f9ba1da](https://github.com/BradenM/micropy-cli/commit/f9ba1da))
* **stubs:** Removed Old Stub Command ([34a1a18](https://github.com/BradenM/micropy-cli/commit/34a1a18))
* **template:** Fixed src template ([881d550](https://github.com/BradenM/micropy-cli/commit/881d550))


### Features

* **project:** Project Module Rewrite to use Cookiecutter and JSON ([9224c6a](https://github.com/BradenM/micropy-cli/commit/9224c6a))
* **template:** Setup Template in Cookiecutter Fashion ([538d1db](https://github.com/BradenM/micropy-cli/commit/538d1db))
* Add Josverl Stubs on First Setup, Restructured MicroPy ([b4461b7](https://github.com/BradenM/micropy-cli/commit/b4461b7))
* Let Stub class handle validation and files ([38fe74a](https://github.com/BradenM/micropy-cli/commit/38fe74a))
* **log:** Added file logging to ServiceLog, Added docs ([390113b](https://github.com/BradenM/micropy-cli/commit/390113b))
* **log:** Added Logging ([298c481](https://github.com/BradenM/micropy-cli/commit/298c481))
* **log:** Added Silet Stdout Context Manager to Logger ([e3d2d91](https://github.com/BradenM/micropy-cli/commit/e3d2d91))
* **log:** Setup Logger as Borg for easy access ([009a685](https://github.com/BradenM/micropy-cli/commit/009a685))
* **log:** Setup ServiceLog to work as a single parent Logger with ch... ([20adb7d](https://github.com/BradenM/micropy-cli/commit/20adb7d))
* **pylint:** Added checkbox to choose stubs for pylint ([0777bf5](https://github.com/BradenM/micropy-cli/commit/0777bf5))
* **stub:** Added createstub.py download ([0b25176](https://github.com/BradenM/micropy-cli/commit/0b25176))
* **stub:** Added stub add, refresh commands ([e7739ec](https://github.com/BradenM/micropy-cli/commit/e7739ec))
* **stub:** Added Stub Class, Moved Stub logic to MicroPy/Stub ([c57594f](https://github.com/BradenM/micropy-cli/commit/c57594f))
* **stub:** Pass Multiple Stubs to .pylintrc ([e8acd42](https://github.com/BradenM/micropy-cli/commit/e8acd42))
* **stubs:** Added Automated Stub Creation on PyBoard ([7c058fd](https://github.com/BradenM/micropy-cli/commit/7c058fd))
* **stubs:** Added Basic Stub Exceptions ([2e62880](https://github.com/BradenM/micropy-cli/commit/2e62880))
* **stubs:** Added Stub Validation, Stub Class Restructure ([22686c0](https://github.com/BradenM/micropy-cli/commit/22686c0))
* Added MicroPy Parent Class ([f9a566a](https://github.com/BradenM/micropy-cli/commit/f9a566a))
* Added stubber as submodule over pulling files with requests ([efb38f7](https://github.com/BradenM/micropy-cli/commit/efb38f7))
* Finished Package Setup and Structure ([2064ea8](https://github.com/BradenM/micropy-cli/commit/2064ea8))
* Initial commit ([0030fdd](https://github.com/BradenM/micropy-cli/commit/0030fdd))
* Project Init and Template Serialization ([e77eef3](https://github.com/BradenM/micropy-cli/commit/e77eef3))
* Setup Template Files ([9f7b4a4](https://github.com/BradenM/micropy-cli/commit/9f7b4a4))
