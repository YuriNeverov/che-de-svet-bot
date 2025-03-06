from typing import Optional
from datetime import datetime


class User:
  def __init__(self, id: int, identifier: Optional[str], first_name: str,
               last_name: Optional[str]):
    self.id = id
    self.identifier = identifier
    self.first_name = first_name
    self.last_name = last_name

  def prettyName(self) -> str:
    if not self.last_name:
      return self.first_name
    return f"{self.first_name} {self.last_name}"


class Operator:
  def __init__(self, id: int, identifier: str, rank: int):
    self.id = id
    self.identifier = identifier
    self.rank = rank


class Subscription:
  def __init__(self, id: int, identifier: str, price: int, description: str):
    self.id = id
    self.identifier = identifier
    self.price = price
    self.description = description


class Product:
  def __init__(self, id: int, subscription_id: int, resource_folder_path: str):
    self.id = id
    self.subscription_id = subscription_id
    self.resource_folder_path = resource_folder_path


class ProductSubscription:
  def __init__(self, subscription_id: int, product_id: int):
    self.subscription_id = subscription_id
    self.product_id = product_id


class ProductUserDelivered:
  def __init__(self, user_id: int, product_id: int):
    self.user_id = user_id
    self.product_id = product_id


class UserSubscription:
  def __init__(self, user_id: int, subscription_id: int, start_date: str,
               end_date: Optional[str]):
    self.user_id = user_id
    self.subscription_id = subscription_id
    self.start_date = start_date
    self.end_date = end_date


class Schedule:
  def __init__(self, user_id: int, product_id: int, delivery_datetime: str):
    self.user_id = user_id
    self.product_id = product_id
    self.delivery_datetime = delivery_datetime


class MessageToOperator:
  def __init__(self, id: int, user_id: int, operator_id: int, msg_text: str,
               msg_pic_path: Optional[str], sent_datetime: datetime,
               received_datetime: Optional[datetime]):
    self.id = id
    self.user_id = user_id
    self.operator_id = operator_id
    self.msg_text = msg_text
    self.msg_pic_path = msg_pic_path
    self.sent_datetime = sent_datetime
    self.received_datetime = received_datetime


class Message:
  def __init__(self, chat_id: int, id: int, sender_user_id: Optional[int],
               msg_text: Optional[str], msg_resource_path: Optional[str],
               sent_datetime: datetime, reply_to: Optional[int]):
    self.chat_id = chat_id
    self.id = id
    self.sender_user_id = sender_user_id
    self.msg_text = msg_text
    self.msg_resource_path = msg_resource_path
    self.sent_datetime = sent_datetime
    self.reply_to = reply_to


class UserScenario:
  def __init__(self, user_id: int, scenario_id: int, state: str):
    self.user_id = user_id
    self.scenario_id = scenario_id
    self.state = state
