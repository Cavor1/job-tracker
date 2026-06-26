from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from src.controller import new_job
from src.logger import log
from src.state import State, View
from src.views import TUI


def create_keybindings(state: State, tui: TUI) -> KeyBindings:
    kb = KeyBindings()
    is_main_view = Condition(lambda: state.current_view == View.MAIN)
    is_new_job_view = Condition(lambda: state.current_view == View.NEW_JOB)

    @kb.add("c-q")
    @kb.add("c-c")
    def _(event):
        event.app.exit()

    @kb.add("b", filter=is_new_job_view)
    def _(event):
        state.current_view = View.MAIN

    @kb.add("c-down", filter=is_new_job_view)
    def _(event):
        event.app.layout.focus_next()

    @kb.add("c-up", filter=is_new_job_view)
    def _(event):
        event.app.layout.focus_previous()

    @kb.add("up", filter=is_main_view)
    def _(event):
        tui.main_view.selected_index = (tui.main_view.selected_index - 1) % len(
            state.jobs
        )

    @kb.add("down", filter=is_main_view)
    def _(event):
        tui.main_view.selected_index = (tui.main_view.selected_index + 1) % len(
            state.jobs
        )

    @kb.add("c-a", filter=is_main_view)
    def _(event):
        state.current_view = View.NEW_JOB
        event.app.layout.focus(tui.new_job_view.link)

    @kb.add("enter", filter=is_new_job_view)
    def _(event):
        try:
            job = tui.new_job_view.parse_form()
        except Exception as e:
            log(f"{e}")
            return
        # log(f"{job}")
        new_job(job)
        tui.refresh()
        event.app.invalidate()
        state.current_view = View.MAIN

    return kb
