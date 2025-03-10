import sqlite3

from typing import Dict

from lib.Function import AsyncWithContext

from .ActorInterface import ActorInterface
from .Config import Config
from .Timer import TimerRegistry
from .Log import Log
from .Domain import *
from .scenarios.ScenarioExecutorInterface import ScenarioExecutorInterface
from .scenarios.CheckReadyScenarioExecutor import CheckReadyScenarioExecutor
from .scenarios.ScheduleScenarioExecutor import ScheduleScenarioExecutor
from .scenarios.AskScenarioExecutor import AskScenarioExecutor
from .scenarios.AnswerScenarioExecutor import AnswerScenarioExecutor
from .scenarios.AdduserScenarioExecutor import AdduserScenarioExecutor
from .scenarios.AddproductScenarioExecutor import AddproductScenarioExecutor
from .scenarios.SubscribeScenarioExecutor import SubscribeScenarioExecutor

from db.DAO import *
from db.Domain import *


class System:
  def __init__(self, config: Config, actor: ActorInterface):
    self.config = config
    self.actor = actor
    # TODO: Make thread-safe
    self.timer_registry = TimerRegistry()

    config.logs_path.mkdir(exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = config.logs_path / f"system_{timestamp}.log"

    self.log = Log("System", log_file=str(log_file))
    try:
      self.config.db_path.parent.mkdir(exist_ok=True)
      self.conn = sqlite3.connect(config.db_path)
      self.conn.execute("PRAGMA foreign_keys = ON;")

      with open(config.root_path / "db" / "sql" / "CreateDB.sql", "r") as f:
        sql = ""
        for line in f:
          if line.strip().startswith("#"): continue
          sql += line
        stmts = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]

        with self.conn:
          for stmt in stmts:
            try:
              self.conn.executescript(stmt)
            except sqlite3.Error as e:
              self.log.error(f"Error executing SQL statement: {stmt[:100]}...")
              self.log.error(f"SQLite error: {str(e)}")
              raise
    except Exception as e:
      self.log.error(f"Failed to initialize database: {str(e)}")
      if self.conn:
        self.conn.close()
      raise

  async def register_user(self, user: User):
    self.log.debug(f"User {user.id},{user.identifier} check")

    if maybe_user := get_user(self.conn, user.id):
      update_user(self.conn, user)
      self.log.debug(f"User {maybe_user.identifier} was already registered")
    else:
      insert_user(self.conn, user)
      self.log.debug(f"User {user.identifier} registered")

    if not get_user_scenario(self.conn, user.id):
      insert_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))

    if user.identifier:
      for sub in fetch_user_manual_subscriptions_by_name(
          self.conn, user.identifier):
        if cur_sub := get_user_subscription(self.conn, user.id,
                                            sub.subscription_id):
          if cur_sub.end_date < sub.end_date:
            update_user_subscription(
                self.conn,
                UserSubscription(user.id, sub.subscription_id, sub.start_date,
                                 sub.end_date))
            await self.actor.send_text(
                user.id, f"Ваша подписка продлена до {sub.end_date}")
        else:
          insert_user_subscription(
              self.conn,
              UserSubscription(user.id, sub.subscription_id, sub.start_date,
                               sub.end_date))
          await self.actor.send_text(
              user.id, f"Ваша подписка активирована до {sub.end_date}")

    vars = self.config.read_vars()
    if "operators" in vars and user.identifier and user.identifier in vars[
        "operators"]:
      try:
        rank = int(vars["operators"][user.identifier])
      except ValueError:
        self.log.error(
            f"Invalid operator rank for user {user.identifier}: {vars['operators'][user.identifier]}"
        )
        return
      updated = Operator(user.id, user.identifier, rank)
      if get_operator(self.conn, user.id):
        update_operator(self.conn, updated)
      else:
        insert_operator(self.conn, updated)
      await self.set_operator_commands(updated)
      self.log.debug(f"User {user.identifier} is an operator with rank {rank}")

  async def set_operator_commands(self, operator: Operator):
    await self.actor.set_commands(
        CommandSet([
            Command("answer", "Answer the user's message"),
            Command("adduser", "Add a user to subscription list"),
            Command("addproduct", "Add a product"),
        ],
                   scope=[operator.id]))

  async def on_actor_init(self):
    self.scenario_ids = {
        "/ask": 1,
        "/schedule": 2,
        "/subscribe": 3,
        "check_ready": 4,  # not a command scenario, so no '/'

        # operator commands start
        "/answer": 5,
        "/adduser": 6,
        "/addproduct": 7,
    }
    self.operator_commands = set(["/answer", "/adduser", "/addproduct"])
    self.check_ready_executor = CheckReadyScenarioExecutor(
        self.log, self.actor, self.conn, self.config)
    # yapf: disable
    self.scenario_executors: Dict[int, ScenarioExecutorInterface] = {
        self.scenario_ids["/ask"]: AskScenarioExecutor(self.log, self.actor, self.conn, self.config),
        self.scenario_ids["/schedule"]: ScheduleScenarioExecutor(self.log, self.actor, self.conn, self.config),
        self.scenario_ids["/subscribe"]: SubscribeScenarioExecutor(self.log, self.actor, self.conn, self.config),
        self.scenario_ids["check_ready"]: self.check_ready_executor,
        self.scenario_ids["/answer"]: AnswerScenarioExecutor(self.log, self.actor, self.conn, self.config),
        self.scenario_ids["/adduser"]: AdduserScenarioExecutor(self.log, self.actor, self.conn, self.config),
        self.scenario_ids["/addproduct"]: AddproductScenarioExecutor(self.log, self.actor, self.conn, self.config),
    }
    # yapf: enable
    await self.actor.set_commands(
        CommandSet([
            Command("start", "Start the bot"),
            Command("help", "Get help message"),
            Command("ask", "Send next message to the operator"),
            Command("schedule", "Schedule next bot interaction"),
            Command("subscribe", "Purchase a subscription"),
        ]))

    await self.register_user(self.actor.get_self_user())

    sub_id = 1
    if not get_subscription(self.conn, sub_id):
      insert_subscription(
          self.conn, Subscription(sub_id, "main", 50000, "Main subscription"))

    self.timer_registry.new(
        "check_ready", 3, 5,
        AsyncWithContext(self.check_ready_executor.check_ready,
                         self.actor.get_event_loop()))

  async def on_sent_message(self, msg: Message):
    insert_message(self.conn, msg)

  async def on_message(self, user: User, msg: Message):
    await self.register_user(user)
    self.log.debug(f"Received message from {msg.chat_id}: '{msg.msg_text}'")
    insert_message(self.conn, msg)
    await self.execute_scenario(user, msg)

  async def on_command(self, command: str, user: User, msg: Message):
    await self.register_user(user)
    insert_message(self.conn, msg)

    if command == "/help":
      vars = self.config.read_vars()
      await self.actor.send_text(msg.chat_id, self.config.read_help_msg(vars),
                                 msg.id)
      self.log.info(f"Sent help message to {msg.chat_id}")
      return
    if command == "/start":
      vars = self.config.read_vars()
      vars["username"] = user.prettyName()
      await self.actor.send_text(msg.chat_id, self.config.read_start_msg(vars),
                                 msg.id)
      self.log.info(f"Started dialog with {msg.chat_id}, replying to {msg.id}")
      return

    if command not in self.scenario_ids:
      await self.actor.send_text(msg.chat_id, "Unknown command")
      self.log.info(f"Unknown command from chat {msg.chat_id}: '{command}'")
      return

    if command in self.operator_commands and not get_operator(
        self.conn, user.id):
      await self.actor.send_text(msg.chat_id, "Unknown command")
      self.log.info(
          f"Operator command from non-operator chat {msg.chat_id} ('{user.identifier}'): '{command}'"
      )
      return

    update_user_scenario(
        self.conn, UserScenario(user.id, self.scenario_ids[command], "{}"))
    await self.execute_scenario(user, msg)

  async def execute_scenario(self, user: User, msg: Message):
    scenario = get_user_scenario(self.conn, user.id)
    if not scenario or scenario.scenario_id not in self.scenario_executors:
      return
    await self.scenario_executors[scenario.scenario_id].execute(user, msg)

  def run(self):
    self.actor.set_up(log=self.log,
                      on_command=self.on_command,
                      on_message=self.on_message,
                      on_sent_message=self.on_sent_message,
                      on_init=self.on_actor_init)
    self.actor.run()

  def __del__(self):
    if self.conn:
      self.conn.commit()
      self.conn.close()
