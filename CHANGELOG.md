<a name="v3.0.0"></a>
## v3.0.0 (2019-10-13)


#### Breaking Changes

*   MicroPy Class refactor renamed core attributes ([bd24ada6](bd24ada6))
*   All Data Path references moved to `micropy.data` module

#### Features

*   Add Flag for Skipping Template Checks ([863c97ca](863c97ca))
*   Search/Retrieve Stubs Directly from micropy-stubs ([0717f373](0717f373))
*   Update MicropyCli Stub Sources ([437d32e9](437d32e9))
*   Refactor MicroPy Class for Better State Management ([711244be](711244be))
*   Updated micropython-stubber to latest version

#### Bug Fixes

*   Project Fails to Init due to Checks on Windows ([06b894ff](06b894ff), closes [#59](59))
*   Stub Package Url fails to resolve on Windows ([3397465e](3397465e))
*   Handle Chunked Content Length on Package Download ([f1dfe5ac](f1dfe5ac))
*   Package urls not resolving correctly ([55f3d34e](55f3d34e))
*   Fails to load Project if Template Files are Missing (#55) ([f8c14c91](f8c14c91))

#### Performance

*   Lazy Load Stubs ([bd24ada6](bd24ada6))
*   Lazy Load Current Active Project ([54b33d51](54b33d51))
*   Cache Remote Stub Package Sources
*   Cache Remote Stub Search Queries
*   Removed unnecessary network requests on startup
*   Overall Code Cleanup



<a name="v2.2.0"></a>
## v2.2.0 (2019-09-28)


#### Performance

* **stubs:**  Cache Available Stubs for Searching ([998b125a](998b125a))

#### Features

*   Template Checks, MS-Python Version Warning (#52) ([fc151f6b](fc151f6b))
* **cli:**  Automatic Update Alerts (#54) ([1f33abef](1f33abef))
* **vscode:**  Ensure Jedi is Disabled in VSCode Template ([efce877a](efce877a))



<a name="v2.1.1"></a>
### v2.1.1 (2019-09-22)


#### Bug Fixes

* **hotfix:**  Remove workspaceRoot var from VSCode Settings (#51) ([d4ddf139](d4ddf139), closes [#50](50))

#### Breaking Changes

* Requires >= `ms-python.python@2019.9.34474` for VSCode Integration **Only**

#### Notes

*   Relicensed under MIT ([f2f191b5](f2f191b5))


<a name="v2.1.0"></a>
## v2.1.0 (2019-09-01)


#### Features

* **log:**  Cap Log File at 2MB ([2d8ad6d6](2d8ad6d6))
* **project:**
  *  Init Project with Micropy Dev Dependency ([1d2fac85](1d2fac85))
  *  Git Ignore Template Option ([12ce75c6](12ce75c6))

#### Bug Fixes

* **project:**  Requirement Files skipped on First Init ([25decf8d](25decf8d))
* **windows:**  Support User Level Directory Linking (#45) ([d67aea80](d67aea80))



<a name="v2.0.2"></a>
### v2.0.2 (2019-08-21)


#### Bug Fixes

* **dep:**  Require appropriate Click version ([6f75e191](6f75e191), closes [#40](40))
* **windows:**  Warn User if MicroPy Lacks Admin Privs ([9e8f3141](9e8f3141))



<a name="v2.0.1"></a>
### v2.0.1 (2019-07-26)


#### Bug Fixes

* **stubs:**  Reduce Schema Strictness ([9343ba1b](9343ba1b))



<a name="v2.0.0"></a>
## v2.0.0 (2019-07-26)


#### Bug Fixes

* **dep:**  Broken Docutils Dependency ([ecfc7419](ecfc7419))
* **project:**  Only modules install correctly ([87fe8ef9](87fe8ef9))

#### Features

*   Add Optional Pyminifier Dep for Stub Creation ([befa4404](befa4404))
* **cli:**
  *  Verbosity Flag for Stub Creation ([f93c8b1e](f93c8b1e))
  *  Install Python Packages for Project ([16cd13cb](16cd13cb))
* **dep:**
  *  Packaging Module Requirement ([36992f7b](36992f7b))
  *  Update Tox to latest ([177f7592](177f7592))
  *  Update Stubber to Process Branch ([da9fb6b3](da9fb6b3))
* **project:**
  *  Update requirements.txt Files on Install ([00f5a923](00f5a923))
  *  Install from Requirements.txt ([ac236c62](ac236c62))
  *  Project Config in Info File ([22600153](22600153))
  *  Template Update Functionality ([f4b91f72](f4b91f72))
  *  Retrieve and Stub Project Requirements ([0ecf6af9](0ecf6af9))
  *  Make Templates Optional via CLI (#30) ([eb460d3f](eb460d3f))
* **pyb:**  Handle Pyboard Output and Errors ([26136c69](26136c69))
* **stubs:**  Minify Stubber Before Executing ([2b6cdd26](2b6cdd26))
* **util:**  Generate Stub from File Utility ([aac79e36](aac79e36))



<a name="v1.1.3"></a>
### v1.1.3 (2019-07-20)


#### Bug Fixes

*   ValueError raised after Creating Project in Windows (#33) ([ac1c0f73](ac1c0f73))
*   Unicode Error raised when logging on Windows (#32) ([2eb5a456](2eb5a456), closes [#31](31))



<a name="v1.1.2"></a>
### v1.1.2 (2019-07-19)


#### Bug Fixes

* **stubs:**  Ensure Firmware Stubs Load First ([0c50d9ab](0c50d9ab))



<a name="v1.1.1"></a>
### v1.1.1 (2019-07-17)


#### Bug Fixes

*   Temp Hotfix for False Stub Duplication ([49e4ad26](49e4ad26))



<a name="v1.1.0"></a>
## v1.1.0 (2019-07-17)


#### Features

* **cli:**
  *  List Project Stubs if in Project Directory ([71eb0ce1](71eb0ce1))
  *  Stubs now list by Firmware ([34271b9e](34271b9e))
  *  Create Formatted Strings from Logger ([58ee3ec0](58ee3ec0))
  *  Added --force flag when adding stubs ([618adbfc](618adbfc))
* **project:**
  *  Micropy Project Info File (#29) ([49420ca4](49420ca4), closes [#9](9))
  *  Micropy Project Folder (#28) ([977ff1f8](977ff1f8))

#### Bug Fixes

* **cli:**
  *  Stub List always prints Unknown ([52d20459](52d20459))
  *  Made Stub Search Case Insensitive ([f7144c7e](f7144c7e))
* **stubs:**  FileExistsError when adding existing Stub ([f9858f98](f9858f98))



<a name="v1.0.0"></a>
## v1.0.0 (2019-07-11)


#### Performance

* **cli:**  Only Instantiate MicroPy when needed ([865afd6b](865afd6b))

#### Features

* **cli:**
  *  Search Available Stubs (#27) ([1622a619](1622a619))
  *  Stream Downloads with Progress Bar ([b3d1401d](b3d1401d))
  *  Minified Cli Output Style ([2435097d](2435097d))
* **stubs:**
  *  Updated micropython-stubber to latest ([d927e601](d927e601))
  *  Update Stubs to Use New Stubber Schema (#23) ([f55b5da1](f55b5da1))
  *  Update Stub Creation (#26) ([4f1f5bc2](4f1f5bc2))
  *  Added Stub Stdout Verbosity ([65338667](65338667))
  *  Add Firmware Frozen Modules to Templates ([5452756d](5452756d))
  *  Implemented Local and Remote Stub Sources (#18) ([98ab23ef](98ab23ef))
  *  Device Stubs Firmware Resolution (#25) ([b9a2357f](b9a2357f))
  *  Add Device Frozen Modules to Templates (#24) ([218c41cb](218c41cb))
  *  Add Stubs from Repositories (#21) ([df9fde52](df9fde52))
  *  Replaced Stubs with Stub "Packages" ([8111618f](8111618f))
  *  Stub Repositories (#20) ([58acfe70](58acfe70))
* **util:**  Generic Utility Functions and Module Cleanup ([6e066547](6e066547))

#### Bug Fixes

* **cli:**
  * Create Stubs Help Formatting ([4439ebe2](4439ebe2))
  * Init Crashes if no Stubs are Loaded ([5547eb76](5547eb76))
* **log:**  Output Highlight Bug, Cleanup ([fd6b2439](fd6b2439))
* **stub:**  Stub Name without Firmware ([94f5f78c](94f5f78c))
* **stubs:**
  *  Firmware not showing as Installed in Stub Search ([db1f74aa](db1f74aa))
  *  Fix Existing Firmware Reinstall ([5c8e0261](5c8e0261))



<a name="v0.3.0"></a>
## v0.3.0 (2019-06-26)


#### Features

* **cli:**  Version Flag ([0f9abf1c](0f9abf1c))
* **log:**  New Cli Output Style, Log Class Methods ([0b257e6f](0b257e6f))
* **pyb:**  PyboardWrapper Utility (#13) ([5f7d2cfe](5f7d2cfe))
* **stubs:**  Stub Manager (#5) ([097b4529](097b4529))
* **utils:**  Utils Module and Validator Utility  (#4) ([be2c9c67](be2c9c67))



<a name="v0.2.0"></a>
## v0.2.0 (2019-06-14)


#### Features

* **log:**
  *  Added Proper Log Formatting, cleaned messages before write. ([6c2fb25c](6c2fb25c))
  *  Added Logging to Template Module ([2e3f51a5](2e3f51a5))
* **project:**  Drop Cookiecutter for Purely Jinja2 (#3) ([ef2d0ef3](ef2d0ef3))

#### Bug Fixes

* **project:** Fixed providing relative paths to `micropy init` ([ef2d0ef3](ef2d0ef3))
* **log:** Fixed Unicode and other characters being written to log ([6c2fb25c](6c2fb25c))



<a name="v0.1.1"></a>
### v0.1.1 (2019-06-10)


#### Bug Fixes

* **setup:**
  *  Fixed missing cookiecutter package requirement ([22ab97cb](22ab97cb))
  *  Fixed Pypi misinformation, cleaned up dist-management files ([e6624072](e6624072))
  *  Fix Missing .vscode Template Files ([806ce7c5](806ce7c5))


<a name="v0.1.0"></a>
### v0.1.0 (2019-06-9)


#### Features

* Initial Release!



