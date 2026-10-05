"""
micropy.data
~~~~~~~~~~~~~~

This module is merely to provide an easy method of locating
data files used by MicropyCli
"""

from pathlib import Path

__all__ = ["FILES", "LOG_FILE", "REPO_SOURCES", "ROOT", "SCHEMAS", "STUBBER", "STUB_DIR"]

# Paths
MOD_PATH = Path(__file__).parent
PATH = MOD_PATH.absolute()
ROOT = MOD_PATH.parent.absolute()

# Stub Schemas
SCHEMAS = PATH / "schemas"

# Default Stub Sources
REPO_SOURCES = PATH / "sources.json"

# Application Data
FILES = Path.home() / ".micropy"
STUB_DIR = FILES / "stubs"
LOG_FILE = FILES / "micropy.log"

# Libraries
LIB = ROOT / "lib"
STUBBER = LIB / "stubber"
