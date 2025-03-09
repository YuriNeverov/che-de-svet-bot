from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

from db.Domain import Message, User
from lib.Domain import Button, Panel
from lib.Function import AsyncWithContext
from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import fetch_users


class CheckReadyScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection):
    super().__init__(log, actor, conn)

  async def execute(self, user: User, msg: Message):
    await self.actor.send_text(msg.chat_id,
                               "This command is not implemented yet")

  async def check_ready(self):
    def send_message(user: User, text: str):
      async def sender():
        await self.actor.send_text(user.id, text)

      return sender
    return

    for user in fetch_users(self.conn):
      if user.id == self.actor.get_self_user().id: continue
      self.log.info(f"try to ping user {user.prettyName()}")
      await self.actor.send_panel(
          user.id, "Вы готовы?",
          Panel([[
              Button(
                  "Да",
                  AsyncWithContext(
                      send_message(user, "Отлично, вот ваш текст"),
                      self.actor.get_event_loop())),
              Button(
                  "Нет",
                  AsyncWithContext(
                      send_message(
                          user,
                          "Жаль. Но вы можете записаться ещё раз через /schedule"
                      ), self.actor.get_event_loop()))
          ],
                 [
                     Button(
                         "Кто такой я?",
                         AsyncWithContext(
                             send_message(user,
                                          "А надо было выпуск смотреть."),
                             self.actor.get_event_loop()))
                 ]]))
