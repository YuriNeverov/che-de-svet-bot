from abc import ABC, abstractmethod
from sqlite3 import Connection

from lib.Log import Log
from lib.ActorInterface import ActorInterface
from db.Domain import Message, User


class ScenarioExecutorInterface(ABC):
  def __init__(self, log: Log, actor: ActorInterface,
               conn: Connection) -> None:
    self.log = log
    self.actor = actor
    self.conn = conn

  @abstractmethod
  async def execute(self, user: User, msg: Message) -> None:
    pass
