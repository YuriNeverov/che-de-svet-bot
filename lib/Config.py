from pathlib import Path


class Config:
  def __init__(self, root_path: Path):
    self.root_path = root_path
    self.db_path = self.root_path / "res" / "state.db"
    self.token_path = self.root_path / "conf" / "bot_token.conf"

  def read_token(self):
    try:
      with open(self.token_path, "r") as f:
        self.token = f.read().strip()
    except Exception as e:
      raise RuntimeError(
          f"Couldn't read token from path '{self.token_path}': {e}")
