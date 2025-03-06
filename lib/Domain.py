from typing import Any, Callable, List, Optional

import uuid


class Button:
  def __init__(self, text: str, on_click: Optional[Callable[..., Any]] = None):
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
