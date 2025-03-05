from datetime import datetime
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from typing import Any
from unittest.mock import patch, MagicMock
from db.DAO import *
from db.Domain import *


class TestInsertMessage(unittest.TestCase):
  @patch('sqlite3.connect')
  def test_insert_message(self, mock_connect: Any):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    message = Message(1, 1, 1, 'test message', 'test_resource_path',
                      datetime.now(), None)

    message_id = insert_message(mock_conn, message)

    self.assertEqual(message_id, 1)
    self.assertEqual(message.id, 1)
    mock_cursor.execute.assert_called_once_with(
        "insert into messages (chat_id, id, sender_user_id, msg_text, msg_resource_path, sent_datetime, reply_to) values (?, ?, ?, ?, ?, ?, ?)",
        (message.id, message.sender_user_id, message.chat_id, message.msg_text,
         message.msg_resource_path, message.sent_datetime, message.reply_to))
    mock_conn.commit.assert_called_once()


class TestGetMessage(unittest.TestCase):
  @patch('sqlite3.connect')
  def test_get_message(self, mock_connect: Any):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    now = datetime.now()
    mock_cursor.fetchone.return_value = (1, 1, 1, 'test message',
                                         'test_resource_path', now, None)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    message = get_message(mock_conn, 1, 1)

    self.assertTrue(message)
    assert message
    self.assertEqual(message.id, 1)
    self.assertEqual(message.sender_user_id, 1)
    self.assertEqual(message.chat_id, 1)
    self.assertEqual(message.msg_text, 'test message')
    self.assertEqual(message.msg_resource_path, 'test_resource_path')
    self.assertEqual(message.sent_datetime, now)
    self.assertEqual(message.reply_to, None)
    mock_cursor.execute.assert_called_once_with(
        "select * from messages where chat_id=? and id=?", (1, 1))
    mock_cursor.fetchone.assert_called_once()


class TestGetMessageNonNoneReplyTo(unittest.TestCase):
  @patch('sqlite3.connect')
  def test_get_message(self, mock_connect: Any):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    now = datetime.now()
    mock_cursor.fetchone.return_value = (1, 2, 1, 'test message',
                                         'test_resource_path', now, 1)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    message = get_message(mock_conn, 1, 2)

    self.assertTrue(message)
    assert message
    self.assertEqual(message.id, 2)
    self.assertEqual(message.sender_user_id, 1)
    self.assertEqual(message.chat_id, 1)
    self.assertEqual(message.msg_text, 'test message')
    self.assertEqual(message.msg_resource_path, 'test_resource_path')
    self.assertEqual(message.sent_datetime, now)
    self.assertEqual(message.reply_to, 1)
    mock_cursor.execute.assert_called_once_with(
        "select * from messages where chat_id=? and id=?", (1, 2))
    mock_cursor.fetchone.assert_called_once()


if __name__ == '__main__':
  unittest.main()
