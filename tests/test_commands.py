import pytest

from gtri.commands import (
    ALL_COMMANDS,
    CommandCategory,
    ParsedArgs,
    classify_command,
    parse_branch_taking_args,
)


class TestClassifyCommand:
    @pytest.mark.parametrize("cmd", ["editor", "ai", "go", "run", "rm", "mv", "copy"])
    def test_branch_taking(self, cmd):
        assert classify_command(cmd) == CommandCategory.BRANCH_TAKING

    @pytest.mark.parametrize("cmd", ["new", "new-ai"])
    def test_creation(self, cmd):
        assert classify_command(cmd) == CommandCategory.CREATION

    @pytest.mark.parametrize("cmd", ["pr", "pr-ai"])
    def test_pr(self, cmd):
        assert classify_command(cmd) == CommandCategory.PR

    def test_passthrough(self):
        assert classify_command("list") == CommandCategory.PASSTHROUGH

    def test_unknown_returns_none(self):
        assert classify_command("bogus") is None


class TestParseBranchTakingArgs:
    def test_no_args(self):
        result = parse_branch_taking_args(())
        assert result == ParsedArgs(search_term="", extra_flags=())

    def test_search_term_only(self):
        result = parse_branch_taking_args(("feat",))
        assert result == ParsedArgs(search_term="feat", extra_flags=())

    def test_flags_only(self):
        result = parse_branch_taking_args(("--delete-branch",))
        assert result == ParsedArgs(search_term="", extra_flags=("--delete-branch",))

    def test_search_then_flags(self):
        result = parse_branch_taking_args(("feat", "--delete-branch", "--force"))
        assert result == ParsedArgs(
            search_term="feat", extra_flags=("--delete-branch", "--force")
        )

    def test_flags_before_search(self):
        """Flags before any non-flag arg are captured; first non-flag is search."""
        result = parse_branch_taking_args(("--force", "feat"))
        assert result == ParsedArgs(search_term="feat", extra_flags=("--force",))

    def test_second_positional_treated_as_flag(self):
        """Only the first non-flag arg is the search term, rest go to extra_flags."""
        result = parse_branch_taking_args(("feat", "extra"))
        assert result == ParsedArgs(search_term="feat", extra_flags=("extra",))


class TestAllCommands:
    def test_contains_all_known_commands(self):
        expected = {"editor", "ai", "go", "run", "rm", "mv", "copy", "new", "new-ai", "list", "pr", "pr-ai"}
        assert set(ALL_COMMANDS) == expected
