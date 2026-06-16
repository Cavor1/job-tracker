from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import CompletionsMenu, Float, FloatContainer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from src.controller import get_jobs, get_keywords
from src.logger import log
from src.models import Job, Keyword
from src.state import State, View


class TUI:
    def __init__(self, state: State) -> None:
        self.state = state
        self.state.jobs = get_jobs()
        log(f"{[j.title for j in self.state.jobs]}")
        self.kb = KeyBindings()
        self.main_view = MainView(state)
        self.new_job_view = NewJobView(state)

    def get_view(self):
        match self.state.current_view:
            case View.MAIN:
                return self.main_view.container
            case View.NEW_JOB:
                return self.new_job_view.container

    def refresh(self):
        self.state.jobs = get_jobs()


class MainView:
    def __init__(self, state: State):
        self.selected_index: int = 0
        self.state = state
        self.menu_window = Window(
            FormattedTextControl(self.get_styled_job_titles_list), width=30
        )
        self.details_window = Window(FormattedTextControl(self.get_job_details))
        self.container = Frame(
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
                    Box(Label("[c-a] : new job | [c-q] : exit | [enter] : submit"), height=1),
                ]
            ),
            title="Job Tracker",
        )

    def get_styled_job_titles_list(self) -> list[tuple[str, str]]:
        text: list[tuple[str, str]] = []

        for i, j in enumerate(self.state.jobs):
            if i == self.selected_index:
                text.append(("class:selected", f"> {j.title}\n"))
            else:
                text.append(("", f"{j.title}\n"))
        return text

    def get_job_details(self):
        for i, j in enumerate(self.state.jobs):
            if i == self.selected_index:
                return j.description
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
            completer=WordCompleter(self.db_keywords),
        )
        self.link = TextArea(height=1, prompt="", multiline=False)
        self.description = TextArea(height=10, prompt="", multiline=True)

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
                        Box(Label("[c-up][c-down] : navigation | [q] : exit"), height=1),
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

        return Job(
            title=self.title.text.strip(),
            link=self.link.text.strip(),
            company=self.company.text.strip() or None,
            keywords=job_keywords,
            description=self.description.text.strip() or None,
        )
