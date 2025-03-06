
from pathlib import Path

path = Path(__file__).parent.absolute()
conf = path / "conf"
conf.mkdir(exist_ok=True)
res = path / "res"
res.mkdir(exist_ok=True)

vars_yaml = """bot-name: "Тестовый бот"
max-messages-to-operator: 3
"""

help_message = """/start - старт бота.
/help - вызов этой команды.
/schedule - установить время получения следующего текста и квиза.
/message - послать следующее сообщение оператору (не более $max-messages-to-operator раз в неделю).
/subscribe - приобрести подписку на проект.
"""

start_message = """Добрый день, $username!

Это бот $bot-name!

Вы можете ввести команду /help, чтобы узнать, что делают остальные команды!
"""

if not (conf / "vars.yaml").exists():
  with open(conf / "vars.yaml", "w") as file:
    file.write(vars_yaml)

if not (res / "help_message.txt").exists():
  with open(res / "help_message.txt", "w") as file:
    file.write(help_message)

if not (res / "start_message.txt").exists():
  with open(res / "start_message.txt", "w") as file:
    file.write(start_message)
