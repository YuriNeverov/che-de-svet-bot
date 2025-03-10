from lib.Config import Config
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection
import json

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *
from db.Domain import Message, User, UserScenario


class ListproductsScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    sub_id = 1
    products = fetch_products_by_subscription(self.conn, sub_id)

    if not products:
      await self.actor.send_text(user.id, "Нет продуктов для подписки 1")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return

    product_list = "\n".join(
        [f"{p.id}. {json.loads(p.data)['name']}" for p in products])

    await self.actor.send_text(user.id,
                               f"Продукты для подписки 1:\n{product_list}")
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
