from pathlib import Path

from front.tg.TelegramBotActor import TelegramBotActor
from lib.Config import Config
from lib.System import System


def main():
  path = Path(__file__).parent.absolute()
  config = Config(path)
  config.read_token()
  system = System(config=config, actor=TelegramBotActor(config.token))
  system.log.debug("debug log")
  system.log.info("info log")
  system.log.warning("warn log")
  system.log.error("error log")

  system.run()


if __name__ == '__main__':
  main()
