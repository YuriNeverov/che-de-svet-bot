from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Optional

from lib.Domain import CommandSet, Panel, Quiz
from lib.Log import Log
from db.Domain import Message, User


class ActorInterface(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def set_up(
      self,
      log: Log,
      on_command: Callable[[str, User, Message], Coroutine[Any, Any, None]],
      on_message: Callable[[User, Message], Coroutine[Any, Any, None]],
      on_init: Optional[Callable[[], Coroutine[Any, Any,
                                               None]]] = None) -> None:
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
  async def reply_to(self,
                     msg: Message,
                     text: str,
                     reply: bool = True) -> Optional[Message]:
    pass

  @abstractmethod
  async def send_panel(self, chat_id: int, text: str,
                       panel: Panel) -> Optional[int]:
    pass

  @abstractmethod
  async def send_quiz(self, chat_id: int, quiz: Quiz) -> Optional[int]:
    pass

  @abstractmethod
  def set_commands_s(self, command_set: CommandSet) -> None:
    pass

  @abstractmethod
  def send_message_s(self, msg: Message) -> None:
    pass

  @abstractmethod
  def reply_to_s(self, msg: Message, text: str, reply: bool = True) -> None:
    pass

  @abstractmethod
  def send_panel_s(self, chat_id: int, text: str,
                   panel: Panel) -> Optional[int]:
    pass

  @abstractmethod
  def send_quiz_s(self, chat_id: int, quiz: Quiz) -> Optional[int]:
    pass

  @abstractmethod
  def get_self_user(self) -> User:
    pass
