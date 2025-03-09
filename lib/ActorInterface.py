from abc import ABC, abstractmethod
from typing import Callable, Optional

from lib.Domain import CommandSet, Panel, Quiz
from lib.Function import AsyncResult
from lib.Log import Log
from db.Domain import Message, User

from asyncio import AbstractEventLoop


class ActorInterface(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def set_up(
      self,
      log: Log,
      on_command: Callable[[str, User, Message], AsyncResult[None]],
      on_message: Callable[[User, Message], AsyncResult[None]],
      on_sent_message: Callable[[Message], AsyncResult[None]],
      on_init: Optional[Callable[[], AsyncResult[None]]] = None) -> None:
    pass

  @abstractmethod
  def run(self) -> None:
    pass

  @abstractmethod
  async def set_commands(self, command_set: CommandSet) -> None:
    pass

  @abstractmethod
  async def send_message(self, msg: Message) -> Optional[int]:
    pass

  @abstractmethod
  async def send_text(self,
                      chat_id: int,
                      text: str,
                      reply_to: Optional[int] = None) -> Optional[Message]:
    pass

  @abstractmethod
  async def send_panel(self,
                       chat_id: int,
                       text: str,
                       panel: Panel,
                       reply_to: Optional[int] = None) -> Optional[int]:
    pass

  @abstractmethod
  async def send_quiz(self,
                      chat_id: int,
                      quiz: Quiz,
                      reply_to: Optional[int] = None) -> Optional[int]:
    pass

  @abstractmethod
  def get_self_user(self) -> User:
    pass

  @abstractmethod
  def get_event_loop(self) -> AbstractEventLoop:
    pass
