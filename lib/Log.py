import logging
import sys
from typing import Optional


class Log:
  def __init__(self, name: str, log_file: Optional[str] = None):
    self.__logger = logging.getLogger(name)
    self.__logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    self.__logger.addHandler(console_handler)

    if log_file:
      file_handler = logging.FileHandler(log_file, encoding='utf-8')
      file_handler.setLevel(logging.DEBUG)
      file_handler.setFormatter(formatter)
      self.__logger.addHandler(file_handler)

  def log(self, level: int, msg: str):
    self.__logger.log(level, msg)

  def debug(self, msg: str):
    self.__logger.log(logging.DEBUG, msg)

  def info(self, msg: str):
    self.__logger.log(logging.INFO, msg)

  def warning(self, msg: str):
    self.__logger.log(logging.WARN, msg)

  def error(self, msg: str):
    self.__logger.log(logging.ERROR, msg)

  def critical(self, msg: str):
    self.__logger.log(logging.CRITICAL, msg)
