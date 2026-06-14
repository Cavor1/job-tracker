
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import BufferControl, DynamicContainer, Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Frame, Box


@dataclass
class Job():
    title : str
    description : str



jobs = [Job(title="job1", description="des1")] 
keys = [j.title for j in jobs]
descriptions = [j.description for j in jobs]
selected_index = 0
last_selected = None

kb = KeyBindings()

class View(StrEnum):
    MAIN = "main"
    NEW_JOB = "new_job"
    
current_view : View = View.MAIN

def get_menu_text():
    result = []

    for i, key in enumerate(keys):
        if i == selected_index:
            result.append(("class:selected", f"> {key}\n"))
        else:
            result.append(("", f"  {key}\n"))

    return result


def get_description_text():
    key = keys[selected_index]
    description = descriptions[selected_index]

    text = [
        ("class:title", "Current item\n"),
        ("", f"Job: {key}\n"),
        ("",description)
    ]

    if last_selected is not None:
        pass

    text.append(("", "\n"))
    text.append(("class:hint", "Use ↑/↓ to navigate, Enter to click, q to quit"))

    return text


menu_control = FormattedTextControl(get_menu_text)
url_control = FormattedTextControl(get_description_text)

menu_window = Window(menu_control, width=30)
url_window = Window(url_control)

main_container = HSplit(
    [
        Frame(
            Box(
                VSplit(
                    [
                        Frame(menu_window, title="Jobs"),
                        Frame(url_window, title="Details"),
                    ]
                ),
                padding=1,
            ),
            title="Dictionary URL Browser",
        )
    ]
)
buffer1 = Buffer()
buffer2 = Buffer()
new_job_container = VSplit([
    Window(content=BufferControl(buffer=buffer1)),
    Window(width=1, char='|'),
    Window(content=BufferControl(buffer=buffer2)),
])
def get_container():
    global current_view
    match current_view:
        case View.MAIN:
            return main_container
        case View.NEW_JOB:
            return new_job_container

root_container = DynamicContainer(get_container)

@kb.add("q")
@kb.add("c-c")
def quit_app(event):
    event.app.exit()


@kb.add("up")
def move_up(event):
    global selected_index
    selected_index = (selected_index - 1) % len(keys)


@kb.add("down")
def move_down(event):
    global selected_index
    selected_index = (selected_index + 1) % len(keys)


@kb.add("enter")
def click_item(event): 
    if current_view == View.MAIN:
        global last_selected
        last_selected = keys[selected_index]
    elif current_view == View.NEW_JOB:
        event.app.layout.focus_next()

@kb.add("c-a")
def new_job(event):
    global current_view
    if current_view == View.MAIN:
        current_view = View.NEW_JOB
        event.app.layout.focus(buffer1)
    else:
        current_view = View.MAIN

    event.app.invalidate()


app = Application(
    layout=Layout(root_container),
    key_bindings=kb,
    full_screen=True,
    style=None,
)


app.run()