from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from lib.Domain import Panel, Quiz
from db.Domain import Message

if TYPE_CHECKING:
  from .System import System


class ActorInterface(ABC):
  def __init__(self) -> None:
    pass

  @abstractmethod
  def set_up(self, system: "System") -> None:
    pass

  @abstractmethod
  def run(self) -> None:
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
  def get_own_id(self) -> int:
    pass
