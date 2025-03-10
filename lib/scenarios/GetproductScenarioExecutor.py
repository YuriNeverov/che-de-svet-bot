from lib.Config import Config
from lib.Domain import Quiz
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection
import json

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *
from db.Domain import Message, User, UserScenario


class GetproductScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    if not msg.msg_text:
      await self.actor.send_text(user.id, "Пустое сообщение")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    args = msg.msg_text.split()
    if len(args) < 2:
      await self.actor.send_text(
          user.id,
          "Формат команды /getproduct N, где N - номер продукта. Список номеров с названиями можно увидеть по команде /listproducts"
      )
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    numStr = args[1]
    try:
      num = int(numStr)
    except ValueError:
      await self.actor.send_text(
          user.id,
          "Формат команды /getproduct N, где N - номер продукта. Номер продукта должен быть числом."
      )
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    product = get_product(self.conn, num)
    if not product:
      await self.actor.send_text(user.id, "Продукт не существует или удалён.")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    try:
      data = json.loads(product.data)
    except json.JSONDecodeError:
      await self.actor.send_text(user.id, "Внутренняя ошибка хранения данных.")
      self.log.error(
          f"JSON decode error for product {product.id} and data JSON '{product.data}'"
      )
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    
    if 'name' not in data or 'text' not in data or 'quiz' not in data:
      await self.actor.send_text(user.id, "Внутренняя ошибка представления данных.")
      self.log.error(
          f"Vital field absent for product {product.id} and data JSON '{product.data}'"
      )
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return

    await self.actor.send_text(user.id, f"{data['name']}")
    await self.actor.send_text(user.id, f"{data['text']}")
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
      await self.actor.send_quiz(user.id, parseQuiz(data['quiz']))
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
