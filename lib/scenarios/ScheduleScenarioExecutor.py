from db.DAO import update_user_scenario
from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.Domain import Message, User, UserScenario


class ScheduleScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection):
    super().__init__(log, actor, conn)

  async def execute(self, user: User, msg: Message):
    update_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))
    await self.actor.send_text(msg.chat_id,
                               "This command is not implemented yet")
