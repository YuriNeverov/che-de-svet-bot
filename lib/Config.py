import re
import yaml

from pathlib import Path
from typing import Dict, Any
from re import Match


class Config:
  def __init__(self, root_path: Path) -> None:
    self.root_path = root_path
    self.db_path = self.root_path / "res" / "state.db"
    self.start_msg_path = self.root_path / "res" / "start_message.txt"
    self.help_msg_path = self.root_path / "res" / "help_message.txt"
    self.token_path = self.root_path / "conf" / "bot_token.txt"
    self.vars_path = self.root_path / "conf" / "vars.yaml"
    self.logs_path = self.root_path / "logs"

  def read_token(self):
    try:
      with open(self.token_path, "r") as f:
        self.token = f.read().strip()
    except Exception as e:
      raise RuntimeError(
          f"Couldn't read token from path '{self.token_path}': {e}")

  def substitute_vars(self, text: str, variables: Dict[str, Any]) -> str:
    pattern = r'\$([a-zA-Zа-яА-Я0-9_-]+)'

    def replace_match(match: Match[str]) -> str:
      var_name = match.group(1)
      return str(variables.get(var_name, match.group(0)))

    return re.sub(pattern, replace_match, text)

  def read_vars(self) -> Dict[str, Any]:
    if not self.vars_path.exists(): return {}
    try:
      with open(self.vars_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}
    except Exception:
      return {}

  def read_msg_from_file(self, path: Path, vars: Dict[str, Any]) -> str:
    if not path.exists(): return ""
    try:
      with open(path, 'r', encoding='utf-8') as f:
        return self.substitute_vars(f.read().strip(), vars)
    except Exception:
      return ""

  def read_start_msg(self, vars: Dict[str, Any]) -> str:
    return self.read_msg_from_file(self.start_msg_path, vars)

  def read_help_msg(self, vars: Dict[str, Any]) -> str:
    return self.read_msg_from_file(self.help_msg_path, vars)
