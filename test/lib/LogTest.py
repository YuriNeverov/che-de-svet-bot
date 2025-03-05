import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
import logging
from typing import Any
from unittest.mock import patch, MagicMock

from lib.Log import Log


class TestLog(unittest.TestCase):
  @patch('logging.getLogger')
  def test_log(self, mock_get_log: Any):
    mock_log = MagicMock()
    mock_get_log.return_value = mock_log

    log = Log('test')

    self.assertEqual(log.logger, mock_log)
    self.assertIsNone(log.stream)

    log.logger.log(logging.INFO, 'test message')
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

    mock_stream = MagicMock()
    log = Log('test', mock_stream)

    self.assertEqual(log.logger, mock_log)
    self.assertEqual(log.stream, mock_stream)

    log.log(logging.INFO, 'test message')
    mock_stream.write.assert_called_once_with('test message\n')

    log.debug('debug message')
    mock_stream.write.assert_called_with('debug message\n')

    log.info('info message')
    mock_stream.write.assert_called_with('info message\n')

    log.warning('warning message')
    mock_stream.write.assert_called_with('warning message\n')

    log.error('error message')
    mock_stream.write.assert_called_with('error message\n')

    log.critical('critical message')
    mock_stream.write.assert_called_with('critical message\n')


if __name__ == '__main__':
  unittest.main()
