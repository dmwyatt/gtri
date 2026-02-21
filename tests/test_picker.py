import pytest

from gtri.picker import filter_items, FuzzyPickerApp


class TestFilterItems:
    def test_empty_query(self):
        items = ("main", "feat-login", "feat-signup")
        assert filter_items(items, "") == items

    def test_case_insensitive_match(self):
        items = ("main", "feat-login", "feat-signup")
        assert filter_items(items, "FEAT") == ("feat-login", "feat-signup")

    def test_no_matches(self):
        items = ("main", "feat-login")
        assert filter_items(items, "zzz") == ()

    def test_single_match(self):
        items = ("main", "feat-login")
        assert filter_items(items, "main") == ("main",)

    def test_substring_match(self):
        items = ("main", "feat-login", "fix-login-bug")
        assert filter_items(items, "login") == ("feat-login", "fix-login-bug")


class TestFuzzyPickerApp:
    @pytest.mark.asyncio
    async def test_select_with_enter(self):
        app = FuzzyPickerApp(items=("main", "feat-login", "feat-signup"), title="Select")
        async with app.run_test() as pilot:
            await pilot.press("enter")
        assert app.return_value == "main"

    @pytest.mark.asyncio
    async def test_cancel_with_escape(self):
        app = FuzzyPickerApp(items=("main", "feat-login"), title="Select")
        async with app.run_test() as pilot:
            await pilot.press("escape")
        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_arrow_down_then_select(self):
        app = FuzzyPickerApp(items=("main", "feat-login", "feat-signup"), title="Select")
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("enter")
        assert app.return_value == "feat-login"

    @pytest.mark.asyncio
    async def test_filter_then_select(self):
        app = FuzzyPickerApp(items=("main", "feat-login", "feat-signup"), title="Select")
        async with app.run_test() as pilot:
            await pilot.press("f", "e", "a", "t")
            await pilot.pause()
            await pilot.press("enter")
        assert app.return_value in ("feat-login", "feat-signup")

    @pytest.mark.asyncio
    async def test_initial_value_filters(self):
        app = FuzzyPickerApp(
            items=("main", "feat-login", "feat-signup"),
            title="Select",
            initial_value="feat",
        )
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
        assert app.return_value in ("feat-login", "feat-signup")

    @pytest.mark.asyncio
    async def test_empty_items(self):
        app = FuzzyPickerApp(items=(), title="Select")
        async with app.run_test() as pilot:
            await pilot.press("enter")
        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_clear_filter_shows_all_items(self):
        """Regression: clearing the input when initial_value is set must show
        all items, not re-apply the initial filter."""
        app = FuzzyPickerApp(
            items=("main", "feat-login", "feat-signup"),
            title="Select",
            initial_value="feat",
        )
        async with app.run_test() as pilot:
            await pilot.pause()
            # Clear "feat" (4 chars) by pressing backspace
            await pilot.press("backspace", "backspace", "backspace", "backspace")
            await pilot.pause()
            # "main" should now be the first item (all items visible)
            await pilot.press("enter")
        assert app.return_value == "main"
