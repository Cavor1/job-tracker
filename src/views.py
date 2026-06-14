
from enum import Enum

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import AnyContainer, BufferControl
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Frame
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
        self.buffer1 = Buffer()
        self.buffer2 = Buffer()
        self.container = VSplit([
            Window(content=BufferControl(buffer=self.buffer1)),
            Window(width=1, char='|'),
            Window(content=BufferControl(buffer=self.buffer2)),
        ])
