import logging
from typing import Optional, TextIO


class Log:
  def __init__(self, name: str, stream: Optional[TextIO] = None):
    self.logger = logging.getLogger(name)
    self.logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    self.logger.addHandler(console_handler)

    self.stream = stream

  def log(self, level: int, msg: str):
    if self.stream is None:
      self.logger.log(level, msg)
    else:
      self.stream.write(f'{msg}\n')

  def debug(self, msg: str):
    self.log(logging.DEBUG, msg)

  def info(self, msg: str):
    self.log(logging.INFO, msg)

  def warning(self, msg: str):
    self.log(logging.WARNING, msg)

  def error(self, msg: str):
    self.log(logging.ERROR, msg)

  def critical(self, msg: str):
    self.log(logging.CRITICAL, msg)
