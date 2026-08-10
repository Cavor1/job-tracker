from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings

from src.controller import new_job, new_job_event
from src.logger import log
from src.models import JobEvent
from src.state import State, View
from src.views import TUI


def create_keybindings(state: State, tui: TUI) -> KeyBindings:
    kb = KeyBindings()
    is_main_view = Condition(lambda: state.current_view == View.MAIN)
    is_new_job_view = Condition(lambda: state.current_view == View.NEW_JOB)
    is_new_event_view = Condition(lambda: state.current_view == View.NEW_EVENT)

    #MAIN VIEW KEYBINDINGS

    @kb.add("c-q",filter=is_main_view)
    @kb.add("c-c")
    def _(event):
        event.app.exit()

    @kb.add("tab",filter=is_main_view)
    def _(event):
        event.app.layout.focus(tui.main_view.details_window)

    @kb.add("up", filter=is_main_view)
    def _(event):
        tui.main_view.select_prev()
    @kb.add("down", filter=is_main_view)
    def _(event):
        tui.main_view.select_next()
    @kb.add("c-a", filter=is_main_view)
    def _(event):
        state.current_view = View.NEW_JOB
        event.app.layout.focus(tui.new_job_view.link)

    @kb.add("enter", filter=is_main_view)
    def _(event):
        state.current_view = View.NEW_EVENT
        event.app.layout.focus(tui.main_view.new_event_window.event_type_text_area)

    #NEW JOB KEYBINDINGS

    @kb.add("c-q", filter=is_new_job_view)
    def _(event):

        tui.main_view.new_event_window.event_type_text_area.buffer.cancel_completion()
        state.current_view = View.MAIN


    @kb.add("c-up", filter=is_new_job_view)
    @kb.add("s-tab", filter=is_new_job_view)
    def _(event):
        event.app.layout.focus_previous()

    @kb.add("enter", filter=is_new_job_view)
    def _(event):
        try:
            job = tui.new_job_view.parse_form()
        except Exception as e:
            log(f"ERROR: {e}")
            return
        # log(f"{job}")
        tui.main_view.new_event_window.event_type_text_area.buffer.cancel_completion()

        new_job(job)
        tui.refresh()
        tui.new_job_view.refresh()
        event.app.invalidate()
        state.current_view = View.MAIN

    #NEW EVENT KEYBINDINGS

    @kb.add("c-q", filter=is_new_event_view)
    def _(event):
        state.current_view = View.MAIN
        tui.main_view.new_event_window.event_type_text_area.buffer.cancel_completion()
        event.app.invalidate()

    @kb.add("enter", filter=is_new_event_view)
    def _(event):
        try: 
            job_event : JobEvent = tui.main_view.new_event_window.parse_form()
        except Exception as e:
            raise Exception(e)
        new_job_event(job_event)

        tui.main_view.new_event_window.event_type_text_area.buffer.cancel_completion()
        tui.refresh()
        state.current_view = View.MAIN
        event.app.invalidate()

    #SHARED KEYBINDINGS

    @kb.add("c-space", filter=(is_new_job_view | is_new_event_view))
    def _(event):
        #open completions
        buffer = event.app.current_buffer

        if buffer.completer is not None:
            buffer.start_completion(select_first=False)

    @kb.add("c-down", filter=is_new_job_view | is_new_event_view)
    @kb.add("tab", filter=(is_new_job_view | is_new_event_view))
    def _(event):
        event.app.layout.focus_next()

    return kb