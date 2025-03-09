from lib.Config import Config
from lib.Domain import Button, Panel
from lib.Function import AsyncWithContext
from .ScenarioExecutorInterface import ScenarioExecutorInterface

import json

from sqlite3 import Connection

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import get_message, get_message_to_operator, get_user_scenario, update_user_scenario, update_user_scenario_state
from db.Domain import Message, User, UserScenario


class AnswerScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    self.log.debug(f"In /answer scenario: state: '{scenario.state}'")
    state = json.loads(scenario.state)
    if not state:
      if msg.reply_to is None:
        update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
        await self.actor.send_text(
            user.id,
            "Эта команда должна применяться в реплае на сообщение с тегом m2o#N"
        )
        return
      reply_to = get_message(self.conn, msg.chat_id, msg.reply_to)
      if reply_to is None or not reply_to.msg_text or not reply_to.msg_text.startswith(
          "m2o#"):
        update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
        await self.actor.send_text(
            user.id,
            "Эта команда должна применяться в реплае на сообщение с тегом m2o#N"
        )
        return
      m2oidStr = reply_to.msg_text.split()[0].split("#")[1]
      try:
        m2oid = int(m2oidStr)
      except ValueError:
        update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
        await self.actor.send_text(
            user.id, f"'{m2oidStr} в теге m2o#N должно быть целым числом")
        return
      new_state = json.dumps({"m2oid": m2oid})
      update_user_scenario_state(self.conn, user.id, new_state)
      await self.actor.send_text(
          user.id,
          f"Следующее сообщение пойдёт в ответ автору выбранного сообщения")
      return

    if "m2oid" not in state:
      self.log.debug(f"Invalid state in /answer: no 'm2oid'")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    m2oid = state["m2oid"]

    m2o = get_message_to_operator(self.conn, m2oid)
    if m2o is None:
      self.log.debug(f"DB failure in /answer: no record for m2oid={m2oid}")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return

    def on_click_yes():
      async def callback():
        update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
        await self.actor.send_text(
            m2o.user_id, f"В ответ на '{m2o.msg_text}':\n{msg.msg_text}")
        await self.actor.send_text(user.id, "Ответ отправлен")

      return AsyncWithContext(callback, self.actor.get_event_loop())

    def on_click_no():
      async def callback():
        await self.actor.send_text(
            user.id,
            f"Принято, следующее сообщение пойдёт в ответ автору выбранного сообщения"
        )

      return AsyncWithContext(callback, self.actor.get_event_loop())

    panel = Panel([
        [Button("Да", on_click_yes()),
         Button("Нет", on_click_no())],
    ])

    await self.actor.send_panel(
        user.id,
        "Это сообщение пойдёт в ответ автору выбранного сообщения, вы подтверждаете?",
        panel, msg.id)
