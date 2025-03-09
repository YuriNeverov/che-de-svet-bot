import threading
import time
from typing import Any, Dict, List

from .Function import Function


class Timer:
  def __init__(self, registry: "TimerRegistry", name: str, times: int,
               duration: float, func: Function, *args: Any, **kwargs: Any):
    self.registry = registry
    self.name = name
    self.times = times
    self.duration = duration
    self.args = args
    self.kwargs = kwargs
    self._stop_event = threading.Event()
    self._thread = threading.Thread(target=self._run)
    self.func = func

  def start(self):
    self._thread.start()

  def stop(self):
    self._stop_event.set()
    if threading.current_thread() is not self._thread:
      self._thread.join()

  def _run(self):
    count = 0
    while not self._stop_event.is_set() and (self.times == -1
                                             or count < self.times):
      try:
        self.func(*self.args, **self.kwargs)
      except Exception as e:
        print(f"Exception occurred: {e}")
      count += 1
      # TODO: Make true duration sleep (now it doesn't count time of self.func execution)
      time.sleep(self.duration)
    self.registry.delete(self.name)


class TimerRegistry:
  def __init__(self):
    self._timers: Dict[str, Timer] = {}

  def new(self, name: str, times: int, duration: float, func: Function, *args:
          Any, **kwargs: Any) -> None:
    if name in self._timers:
      return
    timer = Timer(self, name, times, duration, func, *args, **kwargs)
    self._timers[name] = timer
    timer.start()

  def delete(self, name: str) -> None:
    if name not in self._timers:
      return
    timer = self._timers.pop(name)
    timer.stop()

  def all(self) -> List[str]:
    return list(self._timers.keys())
