import asyncio

from typing import Callable, Any, TypeVar, Union, Coroutine

T = TypeVar('T')

AsyncResult = Coroutine[Any, Any, T]


class AsyncWithContext:
  def __init__(self, func: Callable[..., AsyncResult[T]],
               loop: asyncio.AbstractEventLoop) -> None:
    self.func = func
    self.loop = loop

  def __call__(self, *args: Any, **kwargs: Any):
    asyncio.run_coroutine_threadsafe(self.func(*args, **kwargs), self.loop)


Function = Union[Callable[..., Any], AsyncWithContext]
