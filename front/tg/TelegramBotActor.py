import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Optional, TypeVar
from telegram import Bot, BotCommand, BotCommandScopeChat, Update, User
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler

from db.Domain import Message, User as DomainUser
from lib.ActorInterface import ActorInterface
from lib.Function import AsyncResult
from lib.Log import Log
from lib.Domain import CommandSet, Panel, Quiz

from front.tg.DomainAdapter import to_domain_message, to_domain_user

T = TypeVar("T")


class TelegramBotActor(ActorInterface):
  def __init__(self, token: str):
    self.token = token
    self.bot: Bot
    self.info: User
    self.event_loop: asyncio.AbstractEventLoop
    self.log: Optional[Log] = None
    self.app: Application[Any, Any, Any, Any, Any, Any]
    self.active_panels: dict[int, Panel] = {}

  def set_up(
      self,
      log: Log,
      on_command: Callable[[str, DomainUser, Message], AsyncResult[None]],
      on_message: Callable[[DomainUser, Message], AsyncResult[None]],
      on_sent_message: Callable[[Message], AsyncResult[None]],
      on_init: Optional[Callable[[], AsyncResult[None]]] = None) -> None:
    self.log = log
    self.on_sent_message = on_sent_message

    async def handle_message(update: Update,
                             handler: Callable[..., AsyncResult[None]],
                             isCommand: bool) -> None:
      try:
        if not update.message or not update.message.text or not update.message.from_user:
          return

        user = to_domain_user(update.message.from_user)
        message = to_domain_message(update.message)

        try:
          if isCommand:
            args = update.message.text.split()
            command = args[0] if args else update.message.text
            await handler(command, user, message)
          else:
            await handler(user, message)

        except Exception as e:
          if self.log:
            self.log.error(f"Message handler failed: {e}")
          await self.send_text(
              message.chat_id,
              "An error occurred while processing your message", message.id)

      except Exception as e:
        if self.log:
          self.log.error(f"Message handler failed: {e}")

    async def post_init(
        app: "Application[Bot, Any, Any, Any, Any, Any]") -> None:
      try:
        self.bot = app.bot
        self.info = await self.bot.get_me()
        self.event_loop = asyncio.get_event_loop()
        if on_init:
          await on_init()
      except Exception as e:
        if self.log:
          self.log.error(f"Failed to initialize bot: {e}")
        raise

    self.app = Application.builder().token(
        self.token).post_init(post_init).build()  # type: ignore

    self.app.add_handler(
        MessageHandler(
            filters.COMMAND, lambda update, _: handle_message(
                update, on_command, isCommand=True)))
    self.app.add_handler(
        MessageHandler(
            ~filters.COMMAND, lambda update, _: handle_message(
                update, on_message, isCommand=False)))

    async def button_handler(update: Update, context: Any):
      try:
        query = update.callback_query
        user = update.effective_user
        if not query or not query.data or not user:
          return

        callback_data = query.data
        was_click = False
        if user.id in self.active_panels:
          panel = self.active_panels[user.id]
          for row in panel.buttons:
            for btn in row:
              if btn.callback_data == callback_data:
                was_click = True
                if btn.on_click:
                  btn.on_click()
                break
        if was_click:
          del self.active_panels[user.id]
        else:
          await self.send_text(
              user.id,
              "Похоже, что панель, кнопку которой вы нажали, уже устарела.")

        await query.answer()
      except Exception as e:
        if self.log:
          self.log.error(f"Button handler failed: {e}")

    self.app.add_handler(CallbackQueryHandler(button_handler))

  def run(self) -> None:
    self.app.run_polling()

  async def set_commands(self, command_set: CommandSet) -> None:
    if command_set.scope:
      for chat_id in command_set.scope:
        await self.bot.set_my_commands(
            [BotCommand(cmd.command, cmd.desc) for cmd in command_set.set],
            scope=BotCommandScopeChat(chat_id=chat_id))
      return
    await self.bot.set_my_commands(
        [BotCommand(cmd.command, cmd.desc) for cmd in command_set.set])

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
      await self.on_sent_message(msg)
      return actual_msg.id
    except Exception as e:
      if self.log:
        self.log.error(f"Failed to send message to {msg.chat_id}: {e}")
      return None

  async def send_text(self,
                      chat_id: int,
                      text: str,
                      reply_to: Optional[int] = None) -> Optional[Message]:
    reply_msg = Message(chat_id=chat_id,
                        id=0,
                        sender_user_id=self.get_self_user().id,
                        msg_text=text,
                        msg_resource_path=None,
                        sent_datetime=datetime.now(timezone.utc),
                        reply_to=reply_to)
    await self.send_message(reply_msg)
    return reply_msg

  async def send_panel(self,
                       chat_id: int,
                       text: str,
                       panel: Panel,
                       reply_to: Optional[int] = None) -> Optional[int]:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    try:
      keyboard = [[
          InlineKeyboardButton(btn.text, callback_data=btn.callback_data)
          for btn in row
      ] for row in panel.buttons]

      self.active_panels[chat_id] = panel

      message = await self.bot.send_message(
          chat_id=chat_id,
          text=text,
          reply_to_message_id=reply_to,
          reply_markup=InlineKeyboardMarkup(keyboard))

      return message.message_id
    except Exception as e:
      if self.log:
        self.log.error(f"Failed to send panel to {chat_id}: {e}")
      return None

  async def send_quiz(self,
                      chat_id: int,
                      quiz: Quiz,
                      reply_to: Optional[int] = None) -> Optional[int]:
    try:
      if len(quiz.options) > 10:
        raise ValueError("Telegram quizzes support maximum 10 options")
      if quiz.correct_option < 0 or quiz.correct_option >= len(quiz.options):
        raise ValueError("correct_option must be a valid index for options")

      from typing import cast
      from telegram._utils.types import CorrectOptionID

      correct_option = cast(CorrectOptionID, quiz.correct_option)

      message = await self.bot.send_poll(chat_id=chat_id,
                                         question=quiz.question,
                                         options=quiz.options,
                                         type="quiz",
                                         correct_option_id=correct_option,
                                         is_anonymous=False,
                                         reply_to_message_id=reply_to)
      return message.message_id
    except Exception as e:
      if self.log:
        self.log.error(f"Failed to send quiz to {chat_id}: {e}")
      return None

  def get_self_user(self) -> DomainUser:
    return to_domain_user(self.info)

  def get_event_loop(self) -> asyncio.AbstractEventLoop:
    return self.event_loop
