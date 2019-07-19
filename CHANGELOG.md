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



