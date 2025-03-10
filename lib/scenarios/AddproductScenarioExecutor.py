from lib.Config import Config
from lib.Domain import Button, Panel
from lib.Function import AsyncWithContext
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

import json

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *
from db.Domain import Message, User, UserScenario


class AddproductScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    self.log.debug(f"In /addproduct scenario: state: '{scenario.state}'")

    state = json.loads(scenario.state)

    if not msg.msg_text:
      await self.actor.send_text(user.id, f"Сообщение должно быть непусто")
      return

    if "text-complete" not in state:
      state["text-complete"] = False
      update_user_scenario_state(self.conn, user.id, json.dumps(state))
      await self.actor.send_text(user.id, f"Введите название продукта")
      return

    if "name" not in state:

      def on_click_yes():
        async def callback():
          state["name"] = msg.msg_text
          update_user_scenario_state(self.conn, user.id, json.dumps(state))
          await self.actor.send_text(user.id, f"Введите текст")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      def on_click_no():
        async def callback():
          await self.actor.send_text(user.id,
                                     f"Принято, введите название продукта")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      panel = Panel([
          [Button("Да", on_click_yes()),
           Button("Нет", on_click_no())],
      ])
      await self.actor.send_panel(user.id, f"Подтверждаете имя?", panel,
                                  msg.id)

      return

    if not state["text-complete"]:
      if "text" not in state:
        state["text"] = msg.msg_text
      else:
        state["text"] += msg.msg_text
      update_user_scenario_state(self.conn, user.id, json.dumps(state))

      def on_click_yes():
        async def callback():
          state["text-complete"] = True
          update_user_scenario_state(self.conn, user.id, json.dumps(state))
          await self.actor.send_text(
              user.id, f"""Введите квиз в формате:
Вопрос? (можно без знака вопроса)
- Вариант 1
+ Правильный вариант 2
- Вариант 3
Либо поставьте "-" если квиза не будет""")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      def on_click_no():
        async def callback():
          await self.actor.send_text(user.id, f"Принято, продолжайте текст")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      panel = Panel([
          [Button("Да", on_click_yes()),
           Button("Нет", on_click_no())],
      ])
      sample = ""
      if len(state["text"]) > 100:
        sample = f" '{state['text'][:50]} [...] {state['text'][-50:]}'"

      await self.actor.send_panel(user.id, f"Подтверждаете текст{sample}?",
                                  panel)

      return

    if "quiz" not in state:
      if msg.msg_text.strip() == "-":
        state["quiz"] = None
      else:
        lines = msg.msg_text.split("\n")
        if len(lines) < 2:
          await self.actor.send_text(user.id,
                                     f"Нет вариантов ответа! Введите снова.")
          return
        if len(lines) > 11:
          await self.actor.send_text(
              user.id, f"Больше 10 вариантов ответа! Введите снова.")
          return
        lines = [line.strip() for line in lines]
        pluses = 0
        mults = 0
        for line in lines[1:]:
          if line.startswith("+"):
            pluses += 1
          elif line.startswith("-"):
            mults += 1
        if pluses != 1:
          await self.actor.send_text(
              user.id, "Должен быть 1 правильный ответ! Введите снова.")
          return
        if mults != len(lines) - 2:
          await self.actor.send_text(
              user.id,
              "Неверные варианты должны начинаться с -! Введите снова.")
          return
        state["quiz"] = '\n'.join(lines)

      def on_click_yes():
        async def callback():
          product = Product(
              0,
              json.dumps({
                  "name": state["name"],
                  "text": state["text"],
                  "quiz": state["quiz"]
              }))
          insert_product(self.conn, product)
          sub_id = 1
          insert_product_subscription(self.conn, sub_id, product.id)
          update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
          await self.actor.send_text(user.id, "Продукт добавлен!")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      def on_click_no():
        async def callback():
          await self.actor.send_text(user.id, f"Принято, введите квиз снова.")

        return AsyncWithContext(callback, self.actor.get_event_loop())

      panel = Panel([
          [Button("Да", on_click_yes()),
           Button("Нет", on_click_no())],
      ])

      question = "Подтверждаете отсутствие квиза?" if state[
          "quiz"] is None else "Подтверждаете квиз?"

      await self.actor.send_panel(user.id, question, panel, msg.id)

      return
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
