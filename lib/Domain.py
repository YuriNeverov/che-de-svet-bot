from typing import List, Optional

import uuid

from .Function import Function


class Button:
  def __init__(self, text: str, on_click: Optional[Function] = None):
    self.text = text
    self.callback_data = str(uuid.uuid4())
    self.on_click = on_click

  def __repr__(self):
    return f"Button(text={self.text}, callback_data={self.callback_data})"


class Panel:
  def __init__(self, buttons: Optional[List[List[Button]]] = None):
    self.buttons = buttons if buttons is not None else []

  def add_row(self, buttons: List[Button]):
    self.buttons.append(buttons)

  def add_button(self, button: Button, row: int = -1):
    if row == -1:
      if not self.buttons:
        self.buttons.append([])
      self.buttons[-1].append(button)
    else:
      while len(self.buttons) <= row:
        self.buttons.append([])
      self.buttons[row].append(button)

  def __repr__(self):
    return f"Panel(buttons={self.buttons})"


class Quiz:
  def __init__(self, question: str, options: List[str], correct_option: int):
    self.question = question
    self.options = options
    self.callback_data = str(uuid.uuid4())
    self.correct_option = correct_option

  def __repr__(self):
    return f"Quiz(question={self.question}, options={self.options}, correct_option={self.correct_option})"


class Command:
  def __init__(self, command: str, desc: str):
    self.command = command
    self.desc = desc

  def __repr__(self):
    return f"Command(command={self.command}, desc={self.desc})"


class CommandSet:
  def __init__(self, set: List[Command], scope: Optional[List[int]] = None):
    self.set = set
    self.scope = scope

  def __repr__(self):
    return f"CommandSet(set={self.set}, scope={self.scope})"
