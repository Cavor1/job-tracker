from datetime import datetime, timezone

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import (
    CompletionsMenu,
    ConditionalContainer,
    Float,
    FloatContainer,
)
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from src.logger import log
from src.models import Job, JobEvent, JobEventType, Keyword
from src.state import State, View, load_state


class TUI:
    def __init__(self, state: State) -> None:
        self.state : State= state
        self.refresh()
        self.kb : KeyBindings = KeyBindings()
        self.main_view : MainView = MainView(state)
        self.new_job_view : NewJobView = NewJobView(state)

    def get_view(self):
        match self.state.current_view:
            case View.MAIN:
                self.main_view.new_event_window.is_visible = False

                return self.main_view.container
            case View.NEW_JOB:
                return self.new_job_view.container
            case View.NEW_EVENT:
                self.main_view.new_event_window.is_visible = True
                return self.main_view.container

    def refresh(self):
        log("State refresh")
        load_state(self.state)


class MainView:
    def __init__(self, state: State):
        self.selected_index: int = 0
        self.state = state
        self.state.selected_job_id = self.state.jobs[self.selected_index].id
        self.menu_window = Window(
            FormattedTextControl(self._get_styled_job_titles_list), width=75
        )
        self.details_window = Window(FormattedTextControl(self._get_job_details))
        self.new_event_window = NewEventWindow(state)

        self.new_event_float = self.new_event_window.float

        self.container = self._create_container()

    def _create_container(self):
        return FloatContainer(
            Frame(
                HSplit(
                    [
                        Box(
                            VSplit(
                                [
                                    Frame(self.menu_window, title="Jobs"),
                                    Frame(self.details_window, title="Details"),
                                ]
                            ),
                            padding=1,
                        ),
                        Box(
                            Label("[c-a] : new job | [c-q] : exit | [enter] : submit"),
                            height=1,
                        ),
                    ]
                ),
                title="Job Tracker",
            ),
            floats=[
                self.new_event_float,
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(
                        max_height=8,
                        scroll_offset=1,
                    ),
                ),
            ],
        )

    def _get_styled_job_titles_list(self) -> list[tuple[str, str]]:
        text: list[tuple[str, str]] = []
        title_w = 35
        event_w = 20

        for i, job in enumerate(self.state.jobs):
            style = "class:selected" if i == self.selected_index else ""
            marker = "> " if i == self.selected_index else "  "

            now = datetime.now(timezone.utc)
            past_events = [j for j in job.job_events if j.date.replace(tzinfo=timezone.utc) < now]
            log(str([e.event_type.name for e in past_events]))
            future_events = [j for j in job.job_events if j.date.replace(tzinfo=timezone.utc) >= now]

            # next future event or last event if no future events.
            last_event = (
                max(past_events, key=lambda e: e.date, default=None)
                if not future_events
                else min(future_events, key=lambda e: e.date)
            )
            if last_event is None:
                event_name = ""
                event_date = ""
            else:
                event_name = last_event.event_type.name
                event_date = last_event.date.strftime("%Y-%m-%d %H:%M")

            text.append(
                (
                    style,
                    f"{marker}{job.title[:title_w]:<{title_w}}{event_name[:event_w]:<{event_w}} {event_date}\n",
                )
            )

        return text

    def _get_job_details(self):
        for i, j in enumerate(self.state.jobs):
            if i == self.selected_index:
                text = ""
                for event in self.state.event_types:
                    text += "" #"{event.name}\n"
                return text
        return ""
    def select_prev(self):
        self.selected_index = (self.selected_index - 1) % len(
            self.state.jobs
        )
        self.state.selected_job_id = self.state.jobs[self.selected_index].id
    def select_next(self):
        self.selected_index = (self.selected_index + 1) % len(
            self.state.jobs
        )
        self.state.selected_job_id = self.state.jobs[self.selected_index].id

class NewJobView:
    def __init__(self, state : State) -> None:
        self.state : State = state
        self.title : TextArea= TextArea(height=1, prompt="", multiline=False)
        self.company : TextArea= TextArea(height=1, prompt="", multiline=False)
        self.db_keywords : list[str] = [k.keyword for k in self.state.keywords]
        self.keywords : TextArea = TextArea(
            height=1,
            prompt="",
            multiline=False,
            completer=WordCompleter(self.db_keywords, ignore_case=True),
        )
        self.link : TextArea= TextArea(height=1, prompt="", multiline=False)
        self.description : TextArea= TextArea(height=10, prompt="", multiline=True)

        self.container = FloatContainer(
            Frame(
                HSplit(
                    [
                        Box(
                            HSplit(
                                [
                                    Label("link"),
                                    Frame(self.link),
                                    Label("title"),
                                    Frame(self.title),
                                    Label("company"),
                                    Frame(self.company),
                                    Label("keywords"),
                                    Frame(self.keywords),
                                    Label("description"),
                                    Frame(self.description),
                                ]
                            )
                        ),
                        Box(
                            Label(
                                "[c-up][c-down] / [s-tab][tab] : navigation | [c-space] : autocomplete | [c-q] : exit | [enter] submit"
                            ),
                            height=1,
                        ),
                    ]
                ),
                title="New Job",
            ),
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(
                        max_height=8,
                        scroll_offset=1,
                    ),
                ),
            ],
        )
    def refresh(self):
        self.db_keywords.clear()
        self.db_keywords.extend([k.keyword for k in self.state.keywords])
        self.keywords.text = ""
        self.link.text = ""
        self.company.text = ""
        self.title.text = ""



    def validate_form(self):
        error = ""
        if not self.title.text.strip():
            error += "no title;"
        if not self.link.text.strip():
            error += "no link"
        if not self.link.text.strip():
            error += "no keywords"
        return error

    def parse_form(self) -> Job:

        error = self.validate_form()
        if error:
            raise Exception(error)

        form_keywords = {kw.strip().lower() for kw in self.keywords.text.split()}
        db_keywords = self.state.keywords
        db_keywords_by_name = {kw.keyword: kw for kw in db_keywords}
        job_keywords: list[Keyword] = []

        for keyword_text in form_keywords:
            if keyword_text in db_keywords_by_name:
                keyword = db_keywords_by_name[keyword_text]

            else:
                keyword = Keyword(keyword=keyword_text)
                db_keywords_by_name[keyword_text] = keyword

            job_keywords.append(keyword)

        job = Job(
            title=self.title.text.strip(),
            link=self.link.text.strip(),
            company=self.company.text.strip() or None,
            keywords=job_keywords,
            description=self.description.text.strip() or None,
        )
        job.job_events.append(JobEvent(event_type=self.state.cv_sent_type))
        return job


class NewEventWindow:
    def __init__(self, state: State) -> None:
        self.state = state
        self.is_visible = False
        self.event_type_text_area = TextArea(
            multiline=False,
            height=1,
            completer=WordCompleter([i.name for i in state.event_types]),
        )
        self.date_text_area = TextArea(
            text=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
            multiline=False,
            height=1,
        )

        self.float = Float(
            ConditionalContainer(
                Frame(
                    HSplit(
                        [
                            Frame(self.event_type_text_area),
                            Frame(self.date_text_area),
                        ]
                    ),
                    width=30,
                ),
                filter=Condition(lambda: self.is_visible),
            )
        )

    def validate_form(self):
        error = ""
        if self.event_type_text_area.text not in [et.name for et in self.state.event_types]:
            error += f"no selected type :{self.event_type_text_area.text};"
        return error

    def parse_form(self):
        error = self.validate_form()
        if error:
            raise ValueError(error)

        event_type : JobEventType = [et for et in self.state.event_types if et.name == self.event_type_text_area.text][0]
        job_event = JobEvent(event_type=event_type)
        if self.state.selected_job_id is not None:
            job_event.job_id = self.state.selected_job_id
        else:
            raise ValueError("No job selected")
        return job_event