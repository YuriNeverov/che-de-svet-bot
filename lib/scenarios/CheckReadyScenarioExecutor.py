from .ScenarioExecutorInterface import ScenarioExecutorInterface

from sqlite3 import Connection

from lib.ActorInterface import ActorInterface
from lib.Log import Log
from db.Domain import Message, User


class CheckReadyScenarioExecutor(ScenarioExecutorInterface):
  def __init__(self, log: Log, actor: ActorInterface, conn: Connection):
    super().__init__(log, actor, conn)

  async def execute(self, user: User, msg: Message):
    await self.actor.reply_to(msg,
                              "This command is not implemented yet",
                              reply=False)
