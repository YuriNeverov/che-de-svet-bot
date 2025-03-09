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
from .scenarios.SendMessageScenarioExecutor import SendMessageScenarioExecutor
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

  def register_user(self, user: User):
    self.log.debug(f"User {user.id},{user.identifier} check")

    if maybe_user := get_user(self.conn, user.id):
      update_user(self.conn, user)
      self.log.debug(f"User {maybe_user.identifier} was already registered")
    else:
      insert_user(self.conn, user)
      self.log.debug(f"User {user.identifier} registered")

    if not get_user_scenario(self.conn, user.id):
      insert_user_scenario(self.conn, UserScenario(user.id, 0, "{}"))

  async def on_actor_init(self):
    self.scenario_ids = {
        "/message": 1,
        "/schedule": 2,
        "/subscribe": 3,
        "check_ready": 4,  # not a command scenario, so no '/'
    }
    self.check_ready_executor = CheckReadyScenarioExecutor(
        self.log, self.actor, self.conn)
    self.scenario_executors: Dict[int, ScenarioExecutorInterface] = {
        self.scenario_ids["/message"]:
        SendMessageScenarioExecutor(self.log, self.actor, self.conn),
        self.scenario_ids["/schedule"]:
        ScheduleScenarioExecutor(self.log, self.actor, self.conn),
        self.scenario_ids["/subscribe"]:
        SubscribeScenarioExecutor(self.log, self.actor, self.conn),
        self.scenario_ids["check_ready"]:
        self.check_ready_executor,
    }
    await self.actor.set_commands(
        CommandSet([
            Command("start", "Start the bot"),
            Command("help", "Get help message"),
            Command("message", "Send next message to the operator"),
            Command("schedule", "Schedule next bot interaction"),
            Command("subscribe", "Purchase a subscription"),
        ]))

    self.register_user(self.actor.get_self_user())

    self.timer_registry.new(
        "check_ready", 3, 5,
        AsyncWithContext(self.check_ready_executor.check_ready,
                         self.actor.get_event_loop()))

  async def on_message(self, user: User, msg: Message):
    self.register_user(user)
    self.log.debug(f"Received message from {msg.chat_id}: '{msg.msg_text}'")

  async def on_command(self, command: str, user: User, msg: Message):
    self.register_user(user)

    if command == "/help":
      vars = self.config.read_vars()
      await self.actor.reply_to(msg, self.config.read_help_msg(vars))
      self.log.info(f"Sent help message to {msg.chat_id}")
      return
    if command == "/start":
      vars = self.config.read_vars()
      vars["username"] = user.prettyName()
      await self.actor.reply_to(msg, self.config.read_start_msg(vars))
      self.log.info(f"Started dialog with {msg.chat_id}, replying to {msg.id}")
      return

    if command not in self.scenario_ids:
      await self.actor.reply_to(msg, "Unknown command", reply=False)
      self.log.info(f"Unknown command from chat {msg.chat_id}: '{command}'")
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
                      on_init=self.on_actor_init)
    self.actor.run()

  def __del__(self):
    if self.conn:
      self.conn.commit()
      self.conn.close()
