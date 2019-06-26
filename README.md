# Micropy Cli [![PyPI][pypi-img]][pypi-url] [![PyPI - Python Version][pypiv-img]][pypi-url] [![Travis (.com)][travis-img]][travis-url] [![Coverage Status][cover-img]][cover-url]


Micropy Cli is a project management/generation tool for writing [Micropython](https://micropython.org/) code in modern IDEs such as VSCode.
Its primary goal is to automate the process of creating a workspace complete with:

* **Linting** compatible with Micropython
* VSCode **Intellisense**
* **Autocompletion**
* Dependency Management
* VCS Compatibility

<!-- Command line Application for automating Micropython project creation in Visual Studio Code. -->

<p align='center'>
    <img width='725' src='.github/img/micropy.svg' alt="Micropy Demo SVG">
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

## Usage

```sh
Usage: micropy [OPTIONS] COMMAND [ARGS]...

  CLI Application for creating/managing Micropython Projects.

Options:
  --help  Show this message and exit.

Commands:
  init   Create new Micropython Project
  stubs  Manage Stubs
```

### Creating a Project

Creating a new project folder is as simple as:

1. Executing `micropy init <PROJECT NAME>`
2. Selecting your target device/firmware
3. Boom. Your workspace is ready.

### Stub Management

Micropy Comes Prebundled with stubs provided by [Josvel/micropython-stubber](https://github.com/Josverl/micropython-stubber). If your device/firmware combination isn't available, you can create them via one of the following methods.

#### Creating Stubs

Using `micropy stubs create <PORT/IP_ADDRESS>`, MicropyCli can automatically generate and add stubs from any Micropython device you have on hand. This can be done over both USB and WiFi.

#### Adding Stubs

Alternatively, using `micropy stubs add <PATH>`, you can manually add stubs to Micropy.
For manual stub generation, please see [Josvel/micropython-stubber](https://github.com/Josverl/micropython-stubber).

#### Viewing Stubs

To preview stubs you have installed, simply run `micropy stubs list`.
This will output all stubs available to MicropyCli in the format: `<device_name>@<firmware_version>`


## Credit

### Micropython-Stubber
[Josvel/micropython-stubber](https://github.com/Josverl/micropython-stubber)

Josverl's Repo is full of information regarding Micropython compatibility with VSCode and more. To find out more about how this process works, take a look at it.

Thanks to Josverl's research, MicropyCli can:
* Generate stubs on a Pydevice
* Come prebundled with popular stubs
* Generate frozen modules
* and much more
