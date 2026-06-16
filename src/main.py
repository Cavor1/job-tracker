from prompt_toolkit import Application
from prompt_toolkit.layout import DynamicContainer, Layout

from src.database import create_tables
from src.keybindings import create_keybindings
from src.logger import log
from src.state import State
from src.styles import style
from src.views import TUI

if __name__ == "__main__":
    create_tables()
    log("hi")
    state = State()
    tui = TUI(state)
    root_container = DynamicContainer(tui.get_view)
    kb = create_keybindings(state, tui)
    app = Application(
        layout=Layout(root_container),
        key_bindings=kb,
        full_screen=True,
        style=style,
    )
    app.run()
