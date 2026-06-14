from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from src.state import State, View
from src.views import TUI


def create_keybindings(state : State,tui : TUI) -> KeyBindings:
    kb = KeyBindings()

    is_main_view = Condition(lambda: state.current_view == View.MAIN)
    is_new_job_view = Condition(lambda : state.current_view == View.NEW_JOB)
    @kb.add("q")
    @kb.add("c-c")
    def _(event):
        event.app.exit()


    @kb.add("b",filter=is_new_job_view)
    def _(event):
        state.current_view = View.MAIN
        # event.app.invalidate()


    @kb.add("enter",filter=is_new_job_view)
    def _(event):
        event.app.layout.focus_next()

    
    @kb.add("up", filter=is_main_view)
    def _(event):
        tui.main_view.selected_index = (tui.main_view.selected_index - 1) % len(state.jobs)


    @kb.add("down", filter=is_main_view)
    def _(event):
        tui.main_view.selected_index = (tui.main_view.selected_index + 1) % len(state.jobs)


    # @kb.add("enter",filter=is_main_view)
    # def _(event): 
    #     last_selected = keys[selected_index]


    @kb.add("c-a",filter=is_main_view)
    def _(event):
        state.current_view = View.NEW_JOB
        event.app.layout.focus(tui.new_job_view.buffer1)
        # event.app.invalidate()

    return kb