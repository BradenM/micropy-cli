from __future__ import annotations

try:
    from importlib import metadata as _metadata
except ImportError:
    # compat for py <3.10
    import importlib_metadata as metadata
else:
    # workaround for
    # https://github.com/python/mypy/issues/1393
    metadata = _metadata

__all__ = ["metadata"]
