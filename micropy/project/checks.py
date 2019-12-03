# -*- coding: utf-8 -*-

"""Various requirement checks for templates."""

import subprocess as subproc
from functools import partial as _p

from packaging import version

from micropy.logger import Log

VSCODE_MS_PY_MINVER = "2019.9.34474"

log = Log.get_logger('MicroPy')


def iter_vscode_ext(name=None):
    """Iterates over installed VSCode Extensions.

    Args:
        name (str, optional): Name of Extension to Yield

    """
    _cmd = "code --list-extensions --show-versions"
    proc = subproc.run(_cmd, stdout=subproc.PIPE, stderr=subproc.PIPE, shell=True)
    results = [e.strip() for e in proc.stdout.splitlines()]
    for ext in results:
        ename, vers = ext.split('@')
        if not name:
            yield (ename, vers)
        if name and ename == name:
            yield (ename, vers)


def vscode_ext_min_version(ext, min_version=VSCODE_MS_PY_MINVER, info=None):
    """Check if installed VScode Extension meets requirements.

    Args:
        ext (str): Name of Extension to Test
        min_version (str, optional): Minimum version.
            Defaults to VSCODE_MS_PY_MINVER.
        info (str, optional): Additional information to output.
            Defaults to None.

    Returns:
        bool: True if requirement is satisfied, False otherwise.

    """
    try:
        name, vers = next(iter_vscode_ext(name=ext), (ext, '0.0.0'))
    except Exception as e:
        log.debug(f"vscode check failed to run: {e}")
        log.debug("skipping...")
        return True
    else:
        cur_vers = version.parse(vers)
        min_vers = version.parse(min_version)
        if cur_vers >= min_vers:
            return True
        log.error(
            f"\nVSCode Extension {ext} failed to satisfy requirements!", bold=True)
        log.error(f"$[Min Required Version]: {min_vers}")
        log.error(f"$[Current Version:] {cur_vers}")
        if info:
            log.warn(info)
        return False


TEMPLATE_CHECKS = {
    'ms-python': _p(vscode_ext_min_version,
                    'ms-python.python',
                    info=(
                        "VSCode Integration will fail! "
                        "See $[BradenM/micropy-cli#50] for details.\n"
                    )
                    ),
}
