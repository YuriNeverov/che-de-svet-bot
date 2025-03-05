import telegram as tg
from db.Domain import *


def to_domain_message(msg: tg.Message) -> Message:
  return Message(
      msg.chat.id, msg.message_id, msg.from_user.id if msg.from_user else None,
      msg.text, "", msg.date,
      msg.reply_to_message.message_id if msg.reply_to_message else None)


def to_domain_user(user: tg.User) -> User:
  return User(user.id, user.username)
