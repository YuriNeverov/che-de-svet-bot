import asyncio

from typing import Callable, Any, Union, Coroutine


class AsyncWithContext:
  def __init__(self, func: Callable[..., Coroutine[Any, Any, Any]],
               loop: asyncio.AbstractEventLoop) -> None:
    self.func = func
    self.loop = loop

  def __call__(self, *args: Any, **kwargs: Any) -> Any:
    asyncio.run_coroutine_threadsafe(self.func(*args, **kwargs), self.loop)


Function = Union[Callable[..., Any], AsyncWithContext]
