from datetime import timezone
import json
from lib.Config import Config
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

from db.Domain import Message, User
from lib.Domain import Button, Panel, Quiz
from lib.Function import AsyncWithContext
from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *


class CheckReadyScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    await self.actor.send_text(msg.chat_id,
                               "This command is not implemented yet")

  async def send_product(self, user_id: int, product_id: int):
    product = get_product(self.conn, product_id)
    if not product:
      await self.actor.send_text(
          user_id,
          "Продукт не существует или удалён. Вы можете перезаписаться с /schedule."
      )
      return
    try:
      data = json.loads(product.data)
    except json.JSONDecodeError:
      await self.actor.send_text(user_id, "Внутренняя ошибка хранения данных.")
      self.log.error(
          f"JSON decode error for product {product.id} and data JSON '{product.data}'"
      )
      return

    if 'name' not in data or 'text' not in data or 'quiz' not in data:
      await self.actor.send_text(user_id,
                                 "Внутренняя ошибка представления данных.")
      self.log.error(
          f"Vital field absent for product {product.id} and data JSON '{product.data}'"
      )
      return

    await self.actor.send_text(user_id, f"{data['name']}")
    await self.actor.send_text(user_id, f"{data['text']}")

    def parseQuiz(s: str):
      lines = s.split('\n')
      question = lines[0]
      options: List[str] = []
      correct_option = 0
      for i, opt in enumerate(lines[1:]):
        if opt.startswith('+'):
          correct_option = i
        options.append(opt[1:].strip())
      return Quiz(question, options, correct_option)

    if data['quiz']:
      await self.actor.send_quiz(user_id, parseQuiz(data['quiz']))
    insert_product_user_delivered(self.conn, user_id, product_id)

  async def check_ready(self):
    def choice_yes(user_id: int, product_id: int):
      async def callback():
        await self.send_product(user_id, product_id)

      return AsyncWithContext(callback, self.actor.get_event_loop())

    def choice_no(user_id: int):
      async def callback():
        await self.actor.send_text(
            user_id, "Принято. Вы можете перезаписаться с /schedule.")

      return AsyncWithContext(callback, self.actor.get_event_loop())

    schedules = fetch_active_schedules(self.conn)
    now = datetime.now(timezone.utc)
    for schedule in schedules:
      if now < schedule.delivery_datetime:
        continue
      await self.actor.send_panel(
          schedule.user_id, "Ваше время пришло. Вы готовы?",
          Panel([[
              Button("Да", choice_yes(schedule.user_id, schedule.product_id)),
              Button("Нет", choice_no(schedule.user_id)),
          ]]))
      delete_schedule(self.conn, schedule.user_id, schedule.product_id)
