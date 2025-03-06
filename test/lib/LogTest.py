import tempfile
import shutil

import unittest
import logging
from typing import Any
from pathlib import Path
from unittest.mock import patch, MagicMock

from lib.Log import Log


class TestLog(unittest.TestCase):
  @patch('logging.getLogger')
  def test_log(self, mock_get_log: Any):
    mock_log = MagicMock()
    mock_get_log.return_value = mock_log

    log = Log('test')

    log.log(logging.INFO, 'test message')
    mock_log.log.assert_called_once_with(logging.INFO, 'test message')

    log.debug('debug message')
    mock_log.log.assert_called_with(logging.DEBUG, 'debug message')

    log.info('info message')
    mock_log.log.assert_called_with(logging.INFO, 'info message')

    log.warning('warning message')
    mock_log.log.assert_called_with(logging.WARNING, 'warning message')

    log.error('error message')
    mock_log.log.assert_called_with(logging.ERROR, 'error message')

    log.critical('critical message')
    mock_log.log.assert_called_with(logging.CRITICAL, 'critical message')


class TestLogFileHandler(unittest.TestCase):
  def setUp(self):
    self.temp_dir = Path(tempfile.mkdtemp(prefix='logtest_'))
    self.log_file = self.temp_dir / 'test.log'

  def tearDown(self):
    # Close all handlers to release file handles
    for handler in logging.getLogger('test').handlers:
      handler.close()
    # Remove temp directory
    shutil.rmtree(self.temp_dir)

  def test_file_logging(self):
    log = Log('test', log_file=self.log_file.as_posix())

    test_message = "Test file logging"
    log.info(test_message)

    with open(self.log_file, 'r') as f:
      content = f.read()
      self.assertIn(test_message, content)


if __name__ == '__main__':
  unittest.main()
