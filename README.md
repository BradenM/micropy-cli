# Micropy Cli [![PyPI][pypi-img]][pypi-url] [![PyPI - Python Version][pypiv-img]][pypi-url] [![Travis (.com)][travis-img]][travis-url] [![Coverage Status][cover-img]][cover-url]


Micropy Cli is a project management/generation tool for writing [Micropython](https://micropython.org/) code in modern IDEs such as VSCode.
Its primary goal is to automate the process of creating a workspace complete with:

* **Linting** compatible with Micropython
* VSCode **Intellisense**
* **Autocompletion**
* Dependency Management
* VCS Compatibility


<p align='center'>
    <img width='95%' src='.github/img/micropy.svg' alt="Micropy Demo SVG">
</p>

[pypi-img]: https://img.shields.io/pypi/v/micropy-cli.svg?style=popout-square
[pypi-url]: https://pypi.org/project/micropy-cli/
[pypiv-img]: https://img.shields.io/pypi/pyversions/micropy-cli.svg?style=popout-square
[travis-img]: https://img.shields.io/travis/com/BradenM/micropy-cli/master.svg?style=popout-square
[travis-url]: https://travis-ci.com/BradenM/micropy-cli
[cover-img]: https://coveralls.io/repos/github/BradenM/micropy-cli/badge.svg
[cover-url]: https://coveralls.io/github/BradenM/micropy-cli

## Installation

You can download and install the latest version of this software from the Python package index (PyPI) as follows:

`pip install --upgrade micropy-cli`

### VSCode Integration

If you plan on using `micropy-cli` for it's VSCode related features, you must install the `vscode-python` extension:

`code --install-extension ms-python.python`

You can find the offical page [here](https://marketplace.visualstudio.com/items?itemName=ms-python.python).

> Note: As of `micropy-cli v2.1.1`, you must use version `2019.9.34474` of `vscode-python` or higher. See [#50](https://github.com/BradenM/micropy-cli/issues/50) for details.


## Usage

```sh
Usage: micropy [OPTIONS] COMMAND [ARGS]...

  CLI Application for creating/managing Micropython Projects.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init     Create new Micropython Project
  install  Install Project Requirements
  stubs    Manage Micropy Stubs
```

### Creating a Project

Creating a new project folder is as simple as:

1. Executing `micropy init <PROJECT NAME>`
2. Selecting which templates to use
3. Selecting your target device/firmware
4. Boom. Your workspace is ready.

<p align='center'>
    <img src='https://github.com/BradenM/micropy-cli/raw/master/.github/img/demo.gif' alt="Micropy Demo">
</p>


#### Micropy Project Environment

When creating a project with `micropy-cli`, two special items are added:

* A `.micropy/` folder
* A `micropy.json` file

The `.micropy/` contains symlinks from your project to your `$HOME/.micropy/stubs` folder. By doing this, micropy can reference the required stub files for your project as relative to it, rather than using absolute paths to `$HOME/.micropy`. How does this benefit you? Thanks to this feature, you can feel free to push common setting files such as `settings.json` and `.pylint.rc` to your remote git repository. This way, others who clone your repo can achieve a matching workspace in their local environment.

> Note: The generated `.micropy/` folder should be *IGNORED* by your VCS. It is created locally for each environment via the `micropy.json` file.

The `micropy.json` file contains information micropy needs in order to resolve your projects required files when other clone your repo. Think of it as a `package.json` for micropython.

#### Cloning a Micropy Environment

To setup a Micropy environment locally, simply:

* Install `micropy-cli`
* Navigate to the project directory
* Execute `micropy`

Micropy will automatically configure and install any stubs required by a project thanks to its `micropy.json` file.

### Project Dependencies

While all modules that are included in your targeted micropython firmware are available with autocompletion, intellisense, and linting, most projects require external dependencies.

Currently, handling dependencies with micropython is a bit tricky. Maybe you can install a cpython version of your requirement? Maybe you could just copy and paste it? What if it needs to be frozen?

Micropy handles all these issues for you automatically. Not only does it track your project's dependencies, it keeps both `requirements.txt` and `dev-requirements.txt` updated, enables autocompletion/intellisense for each dep, and allows you to import them just as you would on your device.

This allows you to include your requirement however you want, whether that be as a frozen module in your custom built firmware, or simply in the `/lib` folder on your device.

#### Installing Packages

To add a package as a requirement for your project, run:

`micropy install <PACKAGE_NAMES>`

while in your project's root directory.

This will automatically execute the following:

* Source `PACKAGE_NAMES` from pypi, as a url, or a local path
* Retrieve the module/package and stub it, adding it to your local `.micropy` folder.
* Add requirement to your `micropy.json`
* Update `requirements.txt`

To install dev packages that are not needed on your device, but are needed for local development, add the `--dev` flag. This will do everything above **except** stub the requirement.

You can also install all requirements found in `micropy.json`/`requirements.txt`/`dev-requirements.txt` by executing `micropy install` without passing any packages. Micropy will automatically do this when setting up a local environment of an existing micropy project.

#### Example

Lets say your new project will depend on [picoweb](https://pypi.org/project/picoweb/) and [blynklib](https://pypi.org/project/blynklib/). Plus, you'd like to use [rshell](https://pypi.org/project/rshell/) to communicate directly with your device. After creating your project via `micropy init`, you can install your requirements as so:

<p align='center'>
    <img width="70%" src='.github/img/install_demo.svg' alt="Micropy Pkg Install Demo">
</p>

Now you or anybody cloning your project can import those requirements normally, and have the benefits of all the features micropy brings:

<p align='center'>
    <img width="70%" src='https://github.com/BradenM/micropy-cli/raw/master/.github/img/deps_demo.gif' alt="Micropy Deps Demo">
</p>


### Stub Management

Stub files are the magic behind how micropy allows features such as linting, Intellisense, and autocompletion to work. To achieve the best results with MicropyCli, its important that you first add the appropriate stubs for the device/firmware your project uses.

> Note: When working in a micropy project, all stub related commands will also be executed on the active project. (i.e if in a project and you run `micropy stubs add <stub-name>`, then that stub retrieved AND added to the active project.)

#### Adding Stubs

Adding stubs to Micropy is a breeze. Simply run: `micropy stubs add <STUB_NAME>`
By sourcing [micropy-stubs](https://github.com/BradenM/micropy-stubs), MicroPy has several premade stub packages to choose from.

These packages generally use the following naming schema:

`<device>-<firmware>-<version>`

For example, running `micropy stubs add esp32-micropython-1.11.0` will install the following:
* Micropython Specific Stubs
* ESP32 Micropython v1.11 Device Specific Stubs
* Frozen Modules for both device and firmware

You can search stubs that are made available to Micropy via `micropy stubs search <QUERY>`

Alternatively, using `micropy stubs add <PATH>`, you can manually add stubs to Micropy.
For manual stub generation, please see [Josvel/micropython-stubber](https://github.com/Josverl/micropython-stubber).

#### Creating Stubs

Using `micropy stubs create <PORT/IP_ADDRESS>`, MicropyCli can automatically generate and add stubs from any Micropython device you have on hand. This can be done over both USB and WiFi.

> Note: For stub creation, micropy-cli has additional dependencies.
>
> These can be installed by executing: `pip install micropy-cli[create_stubs]`


#### Viewing Stubs

To list stubs you have installed, simply run `micropy stubs list`.

To search for stubs for your device, use `micropy stubs search <QUERY>`.

## See Also

* [VSCode IntelliSense, Autocompletion & Linting capabilities](https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense)
    - An awesome article written by [lemariva](https://github.com/lemariva). It covers creating a micropython project environment from scratch using `micropy-cli` and [pymakr-vsc](pymakr-vsc). Great place to start if you're new to this!


## Acknowledgements

### Micropython-Stubber
[Josvel/micropython-stubber](https://github.com/Josverl/micropython-stubber)

Josverl's Repo is full of information regarding Micropython compatibility with VSCode and more. To find out more about how this process works, take a look at it.

micropy-cli and [micropy-stubs](https://github.com/BradenM/micropy-stubs) depend on micropython-stubber for its ability to generate frozen modules, create stubs on a pyboard, and more.

