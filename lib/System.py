import sqlite3

from .ActorInterface import ActorInterface
from .Config import Config
from .Timer import TimerRegistry
from .Log import Log
from db.DAO import *
from db.Domain import *


class System:
  def __init__(self, config: Config, actor: ActorInterface):
    self.config = config
    self.actor = actor
    # TODO: Make thread-safe
    self.timer_registry = TimerRegistry()
    self.log = Log("System")
    try:
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
    self.log.info(f"User {user.id},{user.identifier} check")
    maybe_user = get_user(self.conn, user.id)
    if maybe_user:
      self.log.info(f"User {maybe_user.identifier} already registered")
      return
    insert_user(self.conn, user)
    self.log.info(f"User {user.identifier} is being registered")

  async def on_command(self, command: str, user: User, msg: Message):
    self.register_user(user)
    if command == "/help":
      await self.actor.reply_to(msg, "Help message")
      self.log.info(f"Sent help message to {msg.chat_id}")
    elif command == "/start":
      await self.actor.reply_to(msg, "Started dialog, timed 3 replies")
      self.log.info(f"Started dialog with {msg.chat_id}, replying to {msg.id}")
      self.timer_registry.new("Test", 3, 2,
                              lambda: self.actor.reply_to_s(msg, "Timed msg"))
    else:
      await self.actor.reply_to(msg, "Unknown command", reply=False)
      self.log.info(f"Unknown command from chat {msg.chat_id}: '{command}'")

  def run(self):
    self.actor.set_up(self)
    self.actor.run()

  def __del__(self):
    if self.conn:
      self.conn.commit()
      self.conn.close()
