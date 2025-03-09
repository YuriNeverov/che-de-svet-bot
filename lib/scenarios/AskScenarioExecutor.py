from lib.Config import Config
from lib.Domain import Button, Panel
from lib.Function import AsyncWithContext
from .ScenarioExecutorInterface import ScenarioExecutorInterface

import json

from sqlite3 import Connection
from datetime import timedelta, timezone

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *
from db.Domain import Message, MessageToOperator, Operator, User, UserScenario


class AskScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  def get_closest_date(self, user: User):
    res = datetime.now(timezone.utc)
    vars = self.config.read_vars()
    max_msgs = 3
    if "max-messages-to-operator" in vars:
      try:
        max_msgs = int(vars["max-messages-to-operator"])
      except ValueError:
        pass
    last_n_messages = fetch_messages_to_operator_from_user_ordered(
        self.conn, user.id, max_msgs)
    if len(last_n_messages) < max_msgs:
      return res
    return last_n_messages[-1].sent_datetime + timedelta(days=7)

  async def execute(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    if not get_user_subscription(self.conn, user.id, 1):
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(user.id, f"У вас нет подписки.")
      return
    closest_date = self.get_closest_date(user)
    if datetime.now(timezone.utc) < closest_date:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(
          user.id,
          f"Лимит сообщений в неделю достигнут. Попробуйте {closest_date}.")
      return

    self.log.debug(f"In /ask scenario: state: '{scenario.state}'")

    state = json.loads(scenario.state)
    if not state:
      operators = fetch_operators(self.conn)
      panel = Panel()

      def on_click(operator: Operator):
        async def callback():
          new_state = json.dumps({"operator_id": operator.id})
          update_user_scenario_state(self.conn, user.id, state=new_state)
          await self.actor.send_text(
              user.id,
              f"Следующее сообщение пойдёт к оператору {operator.identifier}")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      for operator in operators:
        panel.add_row([Button(operator.identifier, on_click(operator))])
      await self.actor.send_panel(user.id,
                                  "Выберите оператора для обработки вопроса",
                                  panel)
    else:
      if "operator_id" not in state:
        self.log.debug(f"Invalid state in /ask: no 'operator_id'")
        return
      operator_id = state["operator_id"]

      def on_click_yes():
        async def callback():
          update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
          msgToOperator = MessageToOperator(
              0, user.id, operator_id, msg.msg_text if msg.msg_text else "",
              None, msg.sent_datetime, None)
          insert_message_to_operator(self.conn, msgToOperator)
          await self.actor.send_text(
              operator_id, f"m2o#{msgToOperator.id}\n{msg.msg_text}")
          await self.actor.send_text(user.id, "Запрос отправлен")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      def on_click_no():
        async def callback():
          await self.actor.send_text(
              user.id,
              f"Принято, следующее сообщение пойдёт к выбранному оператору")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      panel = Panel([
          [Button("Да", on_click_yes()),
           Button("Нет", on_click_no())],
      ])

      await self.actor.send_panel(
          user.id,
          "Это сообщение будет отправлено оператору, вы подтверждаете?", panel,
          msg.id)
