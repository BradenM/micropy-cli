from __future__ import annotations

from functools import partialmethod
from typing import Any, Callable, NamedTuple, cast

from micropy.pyd.abc import (
    EndHandler,
    MessageConsumer,
    MessageHandler,
    StartHandler,
    StreamConsumer,
    UpdateHandler,
)
from tqdm import tqdm


class ProgressStreamConsumer:
    bar: tqdm

    def __init__(
        self,
        on_description: Callable[
            [str, dict[str, Any] | None], tuple[str, dict[str, Any] | None]
        ] = None,
        **kwargs,
    ):
        self._on_description = on_description or (lambda s, cfg: (s, cfg))

    def on_start(self, *, name: str = None, size: int | None = None):
        bar_format = "{l_bar}{bar}| [{n_fmt}/{total_fmt} @ {rate_fmt}]"
        tqdm_kwargs = {
            "unit_scale": True,
            "unit_divisor": 1024,
            "bar_format": bar_format,
        }
        _name, _tqdm_kws = self._on_description(name or "", tqdm_kwargs)
        # todo: use union operator when min py version is 3.9.
        tqdm_kwargs.update(_tqdm_kws or dict())
        self.bar = tqdm(total=size, unit="B", **tqdm_kwargs)

    def on_update(self, *, size: int | None = None):
        self.bar.update(size)

    def on_end(self):
        self.bar.close()


class ConsumerDelegate:
    consumers: list[StreamConsumer | MessageConsumer]

    def __init__(self, *consumers: StreamConsumer | MessageConsumer | None):
        self.consumers = [i for i in consumers if i]

    def consumer_for(self, action: str, *args, **kwargs):
        _consumer = next((i for i in self.consumers if hasattr(i, action)), None)
        if _consumer is None:
            # default noop
            return
        return getattr(_consumer, action)(*args, **kwargs)

    on_message = cast(MessageHandler, partialmethod(consumer_for, "on_message"))
    on_start = cast(StartHandler, partialmethod(consumer_for, "on_start"))
    on_update = cast(UpdateHandler, partialmethod(consumer_for, "on_update"))
    on_end = cast(EndHandler, partialmethod(consumer_for, "on_end"))


class StreamHandlers(NamedTuple):
    on_start: StartHandler
    on_update: UpdateHandler
    on_end: EndHandler


class MessageHandlers(NamedTuple):
    on_message: MessageHandler
