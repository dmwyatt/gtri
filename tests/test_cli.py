from unittest.mock import patch, MagicMock, call
import subprocess

import pytest

from gtri import GtriError
from gtri.cli import (
    check_dependencies,
    fetch_worktrees,
    resolve_branch,
    dispatch,
    main,
)
from gtri.search import SearchResult, NarrowResult


class TestCheckDependencies:
    def test_all_present(self):
        with patch("gtri.cli.find_executable", return_value="/usr/bin/something"):
            with patch("gtri.cli.subprocess.run"):
                check_dependencies()

    def test_git_missing(self):
        def fake_find(name):
            if name == "git":
                return None
            return "/usr/bin/something"

        with patch("gtri.cli.find_executable", side_effect=fake_find):
            with pytest.raises(GtriError, match="git is required"):
                check_dependencies()

    def test_git_gtr_missing(self):
        def fake_find(name):
            if name == "git-gtr":
                return None
            return "/usr/bin/something"

        with patch("gtri.cli.find_executable", side_effect=fake_find):
            with patch("gtri.cli.subprocess.run"):
                with pytest.raises(GtriError, match="git-gtr is required"):
                    check_dependencies()

    def test_not_in_git_repo(self):
        with patch("gtri.cli.find_executable", return_value="/usr/bin/something"):
            with patch(
                "gtri.cli.subprocess.run",
                side_effect=subprocess.CalledProcessError(1, "git"),
            ):
                with pytest.raises(GtriError, match="not inside a git repository"):
                    check_dependencies()


class TestFetchWorktrees:
    def test_parses_output(self):
        mock_result = MagicMock()
        mock_result.stdout = "/tmp/a\tmain\tclean\n/tmp/b\tfeat\tmodified\n"
        with patch("subprocess.run", return_value=mock_result):
            result = fetch_worktrees()
        assert len(result) == 2
        assert result[0].branch == "main"
        assert result[1].branch == "feat"

    def test_no_worktrees(self):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(GtriError, match="no worktrees found"):
                fetch_worktrees()


class TestResolveBranch:
    def test_only_one_total(self):
        branches = ("main",)
        result = resolve_branch(branches, "")
        assert result == "main"

    def test_single_match_confirmed(self):
        branches = ("main", "feat-login", "fix-typo")
        with patch("gtri.cli.confirm_branch", return_value=True):
            result = resolve_branch(branches, "typo")
        assert result == "fix-typo"

    def test_single_match_declined_opens_picker(self):
        branches = ("main", "feat-login", "fix-typo")
        with patch("gtri.cli.confirm_branch", return_value=False):
            with patch("gtri.cli.run_picker", return_value="main"):
                result = resolve_branch(branches, "typo")
        assert result == "main"

    def test_multiple_matches_opens_picker(self):
        branches = ("main", "feat-login", "feat-signup")
        with patch("gtri.cli.run_picker", return_value="feat-login"):
            result = resolve_branch(branches, "feat")
        assert result == "feat-login"

    def test_no_matches_opens_full_picker(self):
        branches = ("main", "feat-login")
        with patch("gtri.cli.run_picker", return_value="main"):
            result = resolve_branch(branches, "zzz")
        assert result == "main"

    def test_no_search_opens_full_picker(self):
        branches = ("main", "feat-login")
        with patch("gtri.cli.run_picker", return_value="feat-login"):
            result = resolve_branch(branches, "")
        assert result == "feat-login"

    def test_one_branch_nonmatching_search_opens_picker(self):
        """Regression: 'gtri rm fea' with only 'main' must NOT auto-select main."""
        branches = ("main",)
        with patch("gtri.cli.run_picker", return_value="main") as mock_picker:
            result = resolve_branch(branches, "fea")
        mock_picker.assert_called_once()
        assert result == "main"

    def test_one_branch_matching_search_confirms(self):
        branches = ("main",)
        with patch("gtri.cli.confirm_branch", return_value=True):
            result = resolve_branch(branches, "main")
        assert result == "main"

    def test_picker_cancelled(self):
        branches = ("main", "feat-login")
        with patch("gtri.cli.run_picker", return_value=None):
            with pytest.raises(GtriError, match="no worktree selected"):
                resolve_branch(branches, "")


class TestDispatch:
    def test_branch_taking_command(self):
        with patch("gtri.cli.fetch_worktrees") as mock_fetch:
            mock_fetch.return_value = (MagicMock(branch="main"),)
            with patch("gtri.cli.resolve_branch", return_value="main"):
                with patch("gtri.cli.exec_replace") as mock_exec:
                    dispatch("ai", ("main",))
                    mock_exec.assert_called_once_with(
                        ["git", "gtr", "ai", "main"]
                    )

    def test_branch_taking_with_extra_flags(self):
        with patch("gtri.cli.fetch_worktrees") as mock_fetch:
            mock_fetch.return_value = (MagicMock(branch="main"),)
            with patch("gtri.cli.resolve_branch", return_value="main"):
                with patch("gtri.cli.exec_replace") as mock_exec:
                    dispatch("rm", ("main", "--delete-branch"))
                    mock_exec.assert_called_once_with(
                        ["git", "gtr", "rm", "main", "--delete-branch"]
                    )

    def test_new_command(self):
        with patch("gtri.cli.exec_replace") as mock_exec:
            dispatch("new", ("my-feature",))
            mock_exec.assert_called_once_with(["git", "gtr", "new", "my-feature"])

    def test_new_requires_branch(self):
        with pytest.raises(GtriError, match="usage: gtri new <branch"):
            dispatch("new", ())

    def test_new_ai_command(self):
        with patch("gtri.cli.run_subprocess") as mock_run:
            with patch("gtri.cli.exec_replace") as mock_exec:
                dispatch("new-ai", ("my-feature",))
                mock_run.assert_called_once_with(
                    ["git", "gtr", "new", "my-feature"]
                )
                mock_exec.assert_called_once_with(
                    ["git", "gtr", "ai", "my-feature", "--", "--dangerously-skip-permissions"]
                )

    def test_new_ai_requires_branch(self):
        with pytest.raises(GtriError, match="usage: gtri new-ai <branch"):
            dispatch("new-ai", ())

    def test_list_command(self):
        with patch("gtri.cli.exec_replace") as mock_exec:
            dispatch("list", ())
            mock_exec.assert_called_once_with(["git", "gtr", "list"])

    def test_unknown_command(self):
        with pytest.raises(GtriError, match="unknown subcommand"):
            dispatch("bogus", ())


class TestMain:
    def test_help_flag(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_h_flag(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["-h"])
        assert exc_info.value.code == 0

    def test_dispatches_subcommand(self):
        with patch("gtri.cli.check_dependencies"):
            with patch("gtri.cli.dispatch") as mock_dispatch:
                main(["list"])
                mock_dispatch.assert_called_once_with("list", ())

    def test_no_args_picks_subcommand(self):
        with patch("gtri.cli.check_dependencies"):
            with patch("gtri.cli.run_picker", return_value="list"):
                with patch("gtri.cli.dispatch") as mock_dispatch:
                    main([])
                    mock_dispatch.assert_called_once_with("list", ())

    def test_no_args_picker_cancelled(self):
        with patch("gtri.cli.check_dependencies"):
            with patch("gtri.cli.run_picker", return_value=None):
                result = main([])
                assert result == 1

    def test_gtri_error_printed(self, capsys):
        with patch("gtri.cli.check_dependencies", side_effect=GtriError("test error")):
            result = main(["list"])
            assert result == 1

    def test_no_args_picker_excludes_creation_commands(self):
        """Regression: zero-arg picker must not offer 'new'/'new-ai' since they
        require a branch argument that can't be provided through the picker."""
        picker_items = None

        def capture_picker(items, **kwargs):
            nonlocal picker_items
            picker_items = items
            return "ai"

        with patch("gtri.cli.check_dependencies"):
            with patch("gtri.cli.run_picker", side_effect=capture_picker):
                with patch("gtri.cli.dispatch"):
                    main([])

        assert "new" not in picker_items
        assert "new-ai" not in picker_items
        assert "ai" in picker_items
        assert "list" in picker_items


class TestMainExitCode:
    """Regression: main() return value must propagate as process exit code."""

    def test_entry_point_uses_sys_exit(self):
        """The console_scripts entry point must call sys.exit(main())."""
        from pathlib import Path

        main_path = Path(__file__).parent.parent / "src" / "gtri" / "__main__.py"
        source = main_path.read_text()
        assert "sys.exit" in source
