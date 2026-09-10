from prompt_toolkit import Application
from prompt_toolkit.layout import DynamicContainer, Layout

from job_tracker.utils import seed_job_event_types
from job_tracker.database import create_tables
from job_tracker.keybindings import create_keybindings
from job_tracker.logger import log
from job_tracker.state import load_state
from job_tracker.styles import style
from job_tracker.views import TUI

def main():
    create_tables()
    seed_job_event_types()
    log("hi")
    state = load_state()
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

if __name__ == "__main__":
    main()


