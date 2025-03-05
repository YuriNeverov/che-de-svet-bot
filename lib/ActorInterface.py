from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from db.Domain import *

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
  def send_message_s(self, msg: Message) -> None:
    pass

  @abstractmethod
  def reply_to_s(self, msg: Message, text: str, reply: bool = True) -> None:
    pass

  @abstractmethod
  def get_own_id(self) -> int:
    pass
