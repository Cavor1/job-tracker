
from enum import Enum

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import AnyContainer, BufferControl
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Frame, Label, TextArea
from prompt_toolkit.filters import Condition
from src.models import Job
from src.state import State, View
from src.controller import get_jobs
from src.logger import log



class TUI():
    def __init__(self,state : State) -> None:
        self.state = state
        self.state.jobs = get_jobs()
        log(f'{[j.title for j in self.state.jobs]}')
        self.kb = KeyBindings()
        self.main_view = MainView(state)
        self.new_job_view = NewJobView(state)
    def get_view(self):
        match self.state.current_view:
            case View.MAIN:
                return self.main_view.container
            case View.NEW_JOB:
                return self.new_job_view.container  

        
class MainView():
    def __init__(self,state : State):
        self.selected_index : int = 0
        self.state = state
        self.menu_window = Window(FormattedTextControl(self.get_styled_job_titles_list),width=30)
        self.details_window = Window(FormattedTextControl(self.get_job_details))
        self.container =  HSplit([
            Frame(
                Box(
                    VSplit(
                        [
                            Frame(self.menu_window, title="Jobs"),
                            Frame(self.details_window, title="Details"),
                        ]
                    ),
                    padding=1,
                ),
                title="Job Tracker",
            )
        ])

    def get_styled_job_titles_list(self) -> list[tuple[str,str]]:
        text: list[tuple[str,str]]= []
        for i,j in enumerate(self.state.jobs):
            if i == self.selected_index:
                text.append(('class:selected',f'> {j.title}\n')) 
            else:
                text.append(('',f'{j.title}\n'))
        log(f'{text}')
        return text

    def get_job_details(self):
        for i,j in enumerate(self.state.jobs):
            if i == self.selected_index:
                return j.description
        return ""
    

class NewJobView():
    def __init__(self, state) -> None:
        self.title = Frame(TextArea(height=1,prompt="",multiline=False))
        self.company = Frame(TextArea(height=1,prompt="",multiline=False))

        self.keywords = Frame(TextArea(height=10,prompt="",multiline=False))
        self.link = Frame(TextArea(height=10,prompt="",multiline=False))
        self.description = Frame(TextArea(height=10,prompt="",multiline=True))

        self.container = Frame(Box(HSplit([
            Label("link"),
            self.link,
            Label("title"),
            self.title,
            Label("company"),
            self.company,
            Label("keywords"),
            self.keywords,
            Label("description"),
            self.description
            ])),title="New Job")
