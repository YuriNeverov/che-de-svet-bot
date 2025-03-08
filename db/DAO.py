from datetime import datetime
from typing import List, Optional
from sqlite3 import Connection
from .Domain import (User, Operator, Subscription, Product,
                     ProductSubscription, ProductUserDelivered,
                     UserSubscription, Schedule, MessageToOperator, Message,
                     UserScenario)


def get_user(conn: Connection, user_id: int) -> Optional[User]:
  cursor = conn.cursor()
  cursor.execute("select * from users where id=?", (user_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return User(row[0], row[1], row[2], row[3])


def insert_user(conn: Connection, user: User) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into users (id, identifier, first_name, last_name) values (?, ?, ?, ?)",
      (user.id, user.identifier, user.first_name, user.last_name))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  return user.id


def update_user(conn: Connection, user: User):
  cursor = conn.cursor()
  cursor.execute(
      "update users set identifier=?, first_name=?, last_name=? where id=?",
      (user.identifier, user.first_name, user.last_name, user.id))
  conn.commit()


def get_operator(conn: Connection, operator_id: int) -> Optional[Operator]:
  cursor = conn.cursor()
  cursor.execute("select * from operators where id=?", (operator_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return Operator(row[0], row[1], row[2])


def get_all_operators(conn: Connection) -> List[Operator]:
  cursor = conn.cursor()
  cursor.execute("select * from operators")
  res: List[Operator] = []
  rows = cursor.fetchall()
  for row in rows:
    res.append(Operator(row[0], row[1], row[2]))
  return res


def insert_operator(conn: Connection, operator: Operator) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into operators (id, identifier, rank) values (?, ?, ?)",
      (operator.id, operator.identifier, operator.rank))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  return operator.id


def update_operator(conn: Connection, operator: Operator):
  cursor = conn.cursor()
  cursor.execute("update operators set identifier=?, rank=? where id=?",
                 (operator.identifier, operator.rank, operator.id))
  conn.commit()


def get_subscription(conn: Connection,
                     subscription_id: int) -> Optional[Subscription]:
  cursor = conn.cursor()
  cursor.execute("select * from subscriptions where id=?", (subscription_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return Subscription(row[0], row[1], row[2], row[3])


def insert_subscription(conn: Connection,
                        subscription: Subscription) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into subscriptions (identifier, price, description) values (?, ?, ?)",
      (subscription.identifier, subscription.price, subscription.description))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  subscription.id = cursor.lastrowid
  return subscription.id


def update_subscription(conn: Connection, subscription: Subscription):
  cursor = conn.cursor()
  cursor.execute(
      "update subscriptions set identifier=?, price=?, description=? where id=?",
      (subscription.identifier, subscription.price, subscription.description,
       subscription.id))
  conn.commit()


def get_product(conn: Connection, product_id: int) -> Optional[Product]:
  cursor = conn.cursor()
  cursor.execute("select * from products where id=?", (product_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return Product(row[0], row[1], row[2])


def insert_product(conn: Connection, product: Product) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into products (subscription_id, resource_folder_path) values (?, ?)",
      (product.subscription_id, product.resource_folder_path))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  product.id = cursor.lastrowid
  return product.id


def update_product(conn: Connection, product: Product):
  cursor = conn.cursor()
  cursor.execute(
      "update products set subscription_id=?, resource_folder_path=? where id=?",
      (product.subscription_id, product.resource_folder_path, product.id))
  conn.commit()


def get_product_subscription(conn: Connection, subscription_id: int,
                             product_id: int) -> Optional[ProductSubscription]:
  cursor = conn.cursor()
  cursor.execute(
      "select * from product_subscriptions where subscription_id=? and product_id=?",
      (subscription_id, product_id))
  row = cursor.fetchone()
  if row is None:
    return None
  return ProductSubscription(row[0], row[1])


def insert_product_subscription(
    conn: Connection,
    product_subscription: ProductSubscription) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into product_subscriptions (subscription_id, product_id) values (?, ?)",
      (product_subscription.subscription_id, product_subscription.product_id))
  conn.commit()
  return cursor.lastrowid


def get_product_user_delivered(
    conn: Connection, user_id: int,
    product_id: int) -> Optional[ProductUserDelivered]:
  cursor = conn.cursor()
  cursor.execute(
      "select * from product_user_delivered where user_id=? and product_id=?",
      (user_id, product_id))
  row = cursor.fetchone()
  if row is None:
    return None
  return ProductUserDelivered(row[0], row[1])


def insert_product_user_delivered(
    conn: Connection,
    product_user_delivered: ProductUserDelivered) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into product_user_delivered (user_id, product_id) values (?, ?)",
      (product_user_delivered.user_id, product_user_delivered.product_id))
  conn.commit()
  return cursor.lastrowid


def get_user_subscription(conn: Connection, user_id: int,
                          subscription_id: int) -> Optional[UserSubscription]:
  cursor = conn.cursor()
  cursor.execute(
      "select * from user_subscriptions where user_id=? and subscription_id=?",
      (user_id, subscription_id))
  row = cursor.fetchone()
  if row is None:
    return None
  return UserSubscription(row[0], row[1], row[2], row[3])


def insert_user_subscription(
    conn: Connection, user_subscription: UserSubscription) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into user_subscriptions (user_id, subscription_id, start_date, end_date) values (?, ?, ?, ?)",
      (user_subscription.user_id, user_subscription.subscription_id,
       user_subscription.start_date, user_subscription.end_date))
  conn.commit()
  return cursor.lastrowid


def update_user_subscription(conn: Connection,
                             user_subscription: UserSubscription):
  cursor = conn.cursor()
  cursor.execute(
      "update user_subscriptions set start_date=?, end_date=? where user_id=? and subscription_id=?",
      (user_subscription.start_date, user_subscription.end_date,
       user_subscription.user_id, user_subscription.subscription_id))
  conn.commit()


def get_schedule(conn: Connection, user_id: int,
                 product_id: int) -> Optional[Schedule]:
  cursor = conn.cursor()
  cursor.execute("select * from schedules where user_id=? and product_id=?",
                 (user_id, product_id))
  row = cursor.fetchone()
  if row is None:
    return None
  return Schedule(row[0], row[1], row[2], row[3])


def fetch_active_schedules(conn: Connection) -> List[Schedule]:
  cursor = conn.cursor()
  cursor.execute(
      "select * from schedules where elapsed = 0 and delivery_datetime < ?",
      (datetime.now(), ))
  return [
      Schedule(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()
  ]


def insert_schedule(conn: Connection, schedule: Schedule) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into schedules (user_id, product_id, delivery_datetime, elapsed) values (?, ?, ?, 0)",
      (schedule.user_id, schedule.product_id, schedule.delivery_datetime))
  conn.commit()
  return cursor.lastrowid


def update_schedule(conn: Connection, schedule: Schedule):
  cursor = conn.cursor()
  cursor.execute(
      "update schedules set delivery_datetime=?, elapsed=? where user_id=? and product_id=?",
      (schedule.delivery_datetime, schedule.elapsed, schedule.user_id,
       schedule.product_id))
  conn.commit()


def get_message_to_operator(conn: Connection,
                            message_id: int) -> Optional[MessageToOperator]:
  cursor = conn.cursor()
  cursor.execute("select * from messages_to_operators where id=?",
                 (message_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return MessageToOperator(row[0], row[1], row[2], row[3], row[4], row[5],
                           row[6])


def insert_message_to_operator(
    conn: Connection, message_to_operator: MessageToOperator) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into messages_to_operators (user_id, operator_id, msg_text, msg_pic_path, sent_datetime, received_datetime) values (?, ?, ?, ?, ?, ?)",
      (message_to_operator.user_id, message_to_operator.operator_id,
       message_to_operator.msg_text, message_to_operator.msg_pic_path,
       message_to_operator.sent_datetime,
       message_to_operator.received_datetime))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  message_to_operator.id = cursor.lastrowid
  return message_to_operator.id


def update_message_to_operator(conn: Connection,
                               message_to_operator: MessageToOperator):
  cursor = conn.cursor()
  cursor.execute(
      "update messages_to_operators set user_id=?, operator_id=?, msg_text=?, msg_pic_path=?, sent_datetime=?, received_datetime=? where id=?",
      (message_to_operator.user_id, message_to_operator.operator_id,
       message_to_operator.msg_text, message_to_operator.msg_pic_path,
       message_to_operator.sent_datetime,
       message_to_operator.received_datetime, message_to_operator.id))
  conn.commit()


def get_message(conn: Connection, chat_id: int,
                message_id: int) -> Optional[Message]:
  cursor = conn.cursor()
  cursor.execute("select * from messages where chat_id=? and id=?",
                 (chat_id, message_id))
  row = cursor.fetchone()
  if row is None:
    return None
  return Message(row[0], row[1], row[2], row[3], row[4], row[5], row[6])


def insert_message(conn: Connection, message: Message) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into messages (chat_id, id, sender_user_id, msg_text, msg_resource_path, sent_datetime, reply_to) values (?, ?, ?, ?, ?, ?, ?)",
      (message.chat_id, message.id, message.sender_user_id, message.msg_text,
       message.msg_resource_path, message.sent_datetime, message.reply_to))
  conn.commit()
  if cursor.lastrowid is None:
    return None
  message.id = cursor.lastrowid
  return message.id


def update_message(conn: Connection, message: Message):
  cursor = conn.cursor()
  cursor.execute(
      "update messages set sender_user_id=?, msg_text=?, msg_resource_path=?, sent_datetime=?, reply_to=? where chat_id=? and id=?",
      (message.sender_user_id, message.msg_text, message.msg_resource_path,
       message.sent_datetime, message.reply_to, message.chat_id, message.id))
  conn.commit()


def get_user_scenario(conn: Connection,
                      user_id: int) -> Optional[UserScenario]:
  cursor = conn.cursor()
  cursor.execute("select * from user_scenarios where user_id=?", (user_id, ))
  row = cursor.fetchone()
  if row is None:
    return None
  return UserScenario(row[0], row[1], row[2])


def insert_user_scenario(conn: Connection,
                         user_scenario: UserScenario) -> Optional[int]:
  cursor = conn.cursor()
  cursor.execute(
      "insert into user_scenarios (user_id, scenario_id, state) values (?, ?, ?)",
      (user_scenario.user_id, user_scenario.scenario_id, user_scenario.state))
  conn.commit()
  return cursor.lastrowid


def update_user_scenario(conn: Connection, user_scenario: UserScenario):
  cursor = conn.cursor()
  cursor.execute(
      "update user_scenarios set state=?, scenario_id=? where user_id=?",
      (user_scenario.state, user_scenario.scenario_id, user_scenario.user_id))
  conn.commit()
