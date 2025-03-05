import threading
import time
from typing import Callable, Any, Dict, List


class Timer:
  def __init__(self, name: str, times: int, duration: float,
               func: Callable[..., Any], *args: Any, **kwargs: Any):
    self.name = name
    self.times = times
    self.duration = duration
    self.func = func
    self.args = args
    self.kwargs = kwargs
    self._stop_event = threading.Event()
    self._thread = threading.Thread(target=self._run)

  def start(self):
    self._thread.start()

  def stop(self):
    self._stop_event.set()
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


class TimerRegistry:
  def __init__(self):
    self._timers: Dict[str, Timer] = {}

  def new(self, name: str, times: int, duration: float,
          func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    if name in self._timers:
      return
    timer = Timer(name, times, duration, func, *args, **kwargs)
    self._timers[name] = timer
    timer.start()

  def delete(self, name: str) -> None:
    if name not in self._timers:
      return
    timer = self._timers.pop(name)
    timer.stop()

  def all(self) -> List[str]:
    return list(self._timers.keys())
