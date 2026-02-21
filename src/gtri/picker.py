from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Input, OptionList, Static


def filter_items(items: tuple[str, ...], query: str) -> tuple[str, ...]:
    if not query:
        return items
    query_lower = query.lower()
    return tuple(item for item in items if query_lower in item.lower())


class FuzzyPickerApp(App[str | None]):
    CSS = """
    #title {
        dock: top;
        padding: 0 1;
        color: $text-muted;
    }
    #filter-input {
        dock: top;
    }
    #option-list {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(
        self,
        items: tuple[str, ...],
        title: str = "Select",
        initial_value: str = "",
    ) -> None:
        super().__init__()
        self._items = items
        self._title = title
        self._initial_value = initial_value

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self._title, id="title")
            yield Input(
                value=self._initial_value,
                placeholder="Type to filter...",
                id="filter-input",
            )
            yield OptionList(*self._get_filtered_options(), id="option-list")

    def _get_filtered_options(self, query: str = "") -> list[str]:
        q = query or self._initial_value
        return list(filter_items(self._items, q))

    def on_mount(self) -> None:
        if self._initial_value:
            self._refresh_options(self._initial_value)
        self.query_one("#filter-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._refresh_options(event.value)

    def _refresh_options(self, query: str) -> None:
        option_list = self.query_one("#option-list", OptionList)
        option_list.clear_options()
        filtered = self._get_filtered_options(query)
        for item in filtered:
            option_list.add_option(item)
        if filtered:
            option_list.highlighted = 0

    def on_key(self, event) -> None:
        if event.key in ("down", "up"):
            option_list = self.query_one("#option-list", OptionList)
            if event.key == "down":
                option_list.action_cursor_down()
            else:
                option_list.action_cursor_up()
            event.prevent_default()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._select_current()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.exit(str(event.option.prompt))

    def _select_current(self) -> None:
        option_list = self.query_one("#option-list", OptionList)
        if option_list.option_count == 0:
            self.exit(None)
            return
        highlighted = option_list.highlighted
        if highlighted is not None:
            option = option_list.get_option_at_index(highlighted)
            self.exit(str(option.prompt))
        else:
            self.exit(None)

    def action_cancel(self) -> None:
        self.exit(None)
