from datetime import datetime, timedelta
from lib.Domain import Button, Panel
from lib.Function import AsyncWithContext
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.DAO import *
from db.Domain import Message, User, UserScenario


class AdduserScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection):
    super().__init__(log, actor, conn)

  async def execute(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario:
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return
    self.log.debug(f"In /adduser scenario: state: '{scenario.state}'")

    if msg.msg_text is None or len(msg.msg_text.split()) < 2:
      await self.actor.send_text(user.id, "Нужен юзернейм пользователя")
      update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
      return

    username = msg.msg_text.split()[1].lstrip("@")

    def on_click_yes():
      async def callback():
        now = datetime.now()
        then = now + timedelta(days=30)
        #TODO: track subscriptions
        sub_id = 1
        if maybe_user := find_user_by_name(self.conn, username):
          if cur_subscription := get_user_subscription(self.conn,
                                                       maybe_user.id, sub_id):
            if cur_subscription.end_date < then:
              update_user_subscription(
                  self.conn,
                  UserSubscription(maybe_user.id, sub_id,
                                   cur_subscription.start_date, then))
              await self.actor.send_text(user.id,
                                         f"Подписка продлена до {then}")
              await self.actor.send_text(maybe_user.id,
                                         f"Ваша подписка продлена до {then}")
            else:
              await self.actor.send_text(
                  user.id,
                  f"Период подписки пользователя уже больше заданного {then}: {cur_subscription.end_date}"
              )
          else:
            insert_user_subscription(
                self.conn, UserSubscription(maybe_user.id, sub_id, now, then))
            await self.actor.send_text(user.id,
                                       f"Подписка активирована до {then}")
            await self.actor.send_text(
                maybe_user.id, f"Ваша подписка активирована до {then}")
        else:
          if cur_subscription := get_user_manual_subscription(
              self.conn, username, sub_id):
            await self.actor.send_text(
                user.id,
                f"Подписка пользователя уже установлена на активацию до {cur_subscription.end_date}"
            )
          else:
            insert_user_manual_subscription(
                self.conn, UserManualSubscription(username, sub_id, now, then))
            await self.actor.send_text(
                user.id,
                f"Подписка пользователя установлена на активацию до {then} (будет активирована после регистрации в боте)"
            )

      return AsyncWithContext(callback, self.actor.get_event_loop())

    def on_click_no():
      async def callback():
        await self.actor.send_text(
            user.id, f"Принято, операция добавления подписки сброшена")

      return AsyncWithContext(callback, self.actor.get_event_loop())

    panel = Panel([
        [Button("Да", on_click_yes()),
         Button("Нет", on_click_no())],
    ])

    await self.actor.send_panel(
        user.id,
        f"Подписка активируется для пользователя с юзернеймом '{username}', вы подтверждаете?",
        panel, msg.id)
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
