import asyncio
from datetime import datetime
from typing import Any, Coroutine, Optional
from telegram import Bot, BotCommand, Update, User
from telegram.ext import Application, MessageHandler, filters

from db.Domain import Message
from lib.ActorInterface import ActorInterface
from lib.System import System

from .DomainAdapter import to_domain_message, to_domain_user


class TelegramBotActor(ActorInterface):
  def __init__(self, token: str):
    self.token = token
    self.bot: Bot
    self.info: User
    self.event_loop: asyncio.AbstractEventLoop
    self.app: Application[Any, Any, Any, Any, Any, Any]

  def set_up(self, system: System) -> None:
    self.system = system

    async def fetch_bot_info(
        app: "Application[Bot, Any, Any, Any, Any, Any]") -> None:
      try:
        self.bot = app.bot
        self.info = await self.bot.get_me()
        self.event_loop = asyncio.get_event_loop()

        await self.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help")
        ])

        self.system.register_user(to_domain_user(self.info))
      except Exception as e:
        self.system.log.error(f"Failed to initialize bot: {e}")
        raise

    self.app = Application.builder().token(
        self.token).post_init(fetch_bot_info).build()  # type: ignore

    async def handler(update: Update, context: Any):
      try:
        if not update.message or not update.message.text or not update.message.from_user:
          return

        command = update.message.text.split()[0]
        user = to_domain_user(update.message.from_user)
        message = to_domain_message(update.message)

        try:
          await self.system.on_command(command, user, message)
        except Exception as e:
          self.system.log.error(f"Command handler failed for {command}: {e}")
          await self.reply_to(
              message,
              "An error occurred while processing your request",
              reply=True)

      except Exception as e:
        self.system.log.error(f"Message handler failed: {e}")

    self.app.add_handler(MessageHandler(filters.COMMAND,
                                        handler))  #type: ignore

  def run(self) -> None:
    self.app.run_polling()

  async def send_message(self, msg: Message) -> Optional[int]:
    if not msg.msg_text:
      return None

    try:
      actual_msg = await self.bot.send_message(
          chat_id=msg.chat_id,
          text=msg.msg_text,
          reply_to_message_id=msg.reply_to)
      msg.sent_datetime = actual_msg.date
      msg.id = actual_msg.id
      return actual_msg.id
    except Exception as e:
      self.system.log.error(f"Failed to send message to {msg.chat_id}: {e}")
      return None

  async def reply_to(self,
                     msg: Message,
                     text: str,
                     reply: bool = True) -> Optional[Message]:
    reply_msg = Message(id=0,
                        sender_user_id=self.get_own_id(),
                        chat_id=msg.chat_id,
                        msg_text=text,
                        msg_resource_path="",
                        sent_datetime=datetime.now(),
                        reply_to=msg.id if reply else None)
    await self.send_message(reply_msg)
    return reply_msg

  def send_message_s(self, msg: Message) -> None:
    self.do_sync(self.send_message(msg))

  def reply_to_s(self, msg: Message, text: str, reply: bool = True) -> None:
    self.do_sync(self.reply_to(msg, text, reply))

  def do_sync(self, coro: Coroutine[Any, Any, Any]) -> Optional[Any]:
    try:
      future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)
      return future.result()
    except Exception as e:
      self.system.log.error(f"Failed to execute synchronously: {e}")
      return None

  def get_own_id(self) -> int:
    return self.info.id
