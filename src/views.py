from datetime import datetime

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

from src.controller import (
    get_cv_sent_event_type,
    get_event_types,
    get_jobs,
    get_keywords,
)
from src.logger import log
from src.models import Job, JobEvent, Keyword
from src.state import State, View


class TUI:
    def __init__(self, state: State) -> None:
        self.state = state
        self.refresh()
        log(f"{[j.title for j in self.state.jobs]}")
        self.kb = KeyBindings()
        self.main_view = MainView(state)
        self.new_job_view = NewJobView(state)

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
        self.state.jobs = get_jobs()
        self.state.event_types = get_event_types()


class MainView:
    def __init__(self, state: State):
        self.selected_index: int = 0
        self.state = state
        self.menu_window = Window(
            FormattedTextControl(self._get_styled_job_titles_list), width=70
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

            now = datetime.now()
            past_events = [j for j in job.job_events if j.date < now]
            future_events = [j for j in job.job_events if j.date >= now]

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
                event_date = last_event.date.date()
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
                for e in self.state.event_types:
                    text += f"{e.name}\n"
                log(text)
                return text
        return ""


class NewJobView:
    def __init__(self, state) -> None:
        self.title = TextArea(height=1, prompt="", multiline=False)
        self.company = TextArea(height=1, prompt="", multiline=False)
        self.db_keywords = [k.keyword for k in get_keywords()]
        self.keywords = TextArea(
            height=1,
            prompt="",
            multiline=False,
            completer=WordCompleter(self.db_keywords, ignore_case=True),
        )
        self.link = TextArea(height=1, prompt="", multiline=False)
        self.description = TextArea(height=10, prompt="", multiline=True)

        self.cv_sent_type = get_cv_sent_event_type()

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
        db_keywords = get_keywords()
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
        job.job_events.append(JobEvent(event_type=self.cv_sent_type))
        return job


class NewEventWindow:
    def __init__(self, state: State) -> None:
        self.state = state
        self.is_visible = False
        self.float = Float(
            ConditionalContainer(
                Frame(
                    HSplit(
                        [
                            Frame(TextArea(
                                prompt="",
                                multiline=False,
                                height=1,
                                completer=WordCompleter([i.name for i in state.event_types]),
                            )),
                            Frame(TextArea(
                                text=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
                                multiline=False,
                                height=1,
                            ))
                        ]
                    ),
                    width=30,
                ),
                filter=Condition(lambda: self.is_visible),
            )
        )
