from db.DAO import *
from lib.Config import Config
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection
import json

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.Domain import Message, User, UserScenario


class ScheduleScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection,
               config: Config):
    super().__init__(log, actor, conn, config)

  async def execute(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    sub_id = 1
    if not get_user_subscription(self.conn, user.id, sub_id):
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(user.id, f"У вас нет подписки.")
      return

    if not msg.msg_text:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(msg.chat_id, "Пустое сообщение")
      return

    try:
      state = json.loads(scenario.state)
    except json.JSONDecodeError:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(msg.chat_id, "Внутренняя ошибка.")
      return

    if "product-id" not in state:
      products = fetch_products_by_subscription(self.conn, sub_id)
      delivered = set(fetch_user_delivered_product_ids(self.conn, user.id))
      product: Optional[Product] = None
      for p in products:
        if p.id not in delivered:
          product = p
          break
      if product is None:
        update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
        await self.actor.send_text(msg.chat_id, "Вы всё посмотрели.")
        return
      state["product-id"] = product.id
      update_user_scenario_state(self.conn, user.id, json.dumps(state))
      await self.actor.send_text(
          msg.chat_id, "Введите дату (часовой пояс МСК) в формате ДД.ММ.ГГГГ")
      return

    product_id = state["product-id"]

    async def dateError():
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(
          msg.chat_id,
          "Неверный формат даты или несуществующая дата. Введите снова.")

    if "date" not in state:
      parts = msg.msg_text.strip().split(".")
      if len(parts) != 3:
        await dateError()
        return

      date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"

      try:
        date = datetime.fromisoformat(date_str)
      except ValueError:
        await dateError()
        return

      state["date"] = date_str
      update_user_scenario_state(self.conn, user.id, json.dumps(state))
      await self.actor.send_text(
          msg.chat_id,
          "Принято, введите время (часовой пояс МСК) в формате ЧЧ:мм.")
      return

    async def timeError():
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      await self.actor.send_text(msg.chat_id,
                                 "Неверный формат времени. Введите снова.")

    parts = msg.msg_text.strip().split(":")
    if len(parts) != 2:
      await timeError()
      return

    full_datetime = f"{state['date']} {parts[0]}:{parts[1]}:00.000+03:00"
    try:
      date = datetime.fromisoformat(full_datetime)
    except ValueError:
      await timeError()
      return

    insert_schedule(self.conn, Schedule(user.id, product_id, date, False))
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
    await self.actor.send_text(
        msg.chat_id,
        f"Принято, вы записаны на {date.strftime('%d.%m.%y %H:%M')} (часовой пояс МСК)."
    )
