from __future__ import annotations

from typing import Any, Callable

from tqdm import tqdm


class ProgressStreamConsumer:
    bar: tqdm

    def __init__(
        self,
        on_description: Callable[[str, dict[str, Any] | None], tuple[str, dict[str, Any]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._on_description = on_description or (
            lambda s, cfg: (
                s,
                cfg,
            )
        )

    # def consumer(self, msg: str | bytes):
    #     if msg:
    #         _msg = msg if isinstance(msg, str) else msg.decode()
    #         self.on_message(_msg)

    def on_start(self, *, name: str = None, size: int | None = None):
        bar_format = "{l_bar}{bar}| [{n_fmt}/{total_fmt} @ {rate_fmt}]"
        tqdm_kwargs = {
            "unit_scale": True,
            "unit_divisor": 1024,
            "bar_format": bar_format,
        }
        _name, _tqdm_kws = self._on_description(name or "", tqdm_kwargs)
        self.bar = tqdm(total=size, unit="B", **(tqdm_kwargs | (_tqdm_kws or dict())))

    def on_update(self, *, size: int | None = None):
        self.bar.update(size)

    def on_end(self):
        self.bar.close()
