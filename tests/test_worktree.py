from gtri.worktree import Worktree, parse_porcelain


class TestWorktree:
    def test_frozen(self):
        wt = Worktree(path="/tmp/foo", branch="main", status="clean")
        assert wt.path == "/tmp/foo"
        assert wt.branch == "main"
        assert wt.status == "clean"

    def test_equality(self):
        a = Worktree(path="/a", branch="b", status="c")
        b = Worktree(path="/a", branch="b", status="c")
        assert a == b


class TestParsePorcelain:
    def test_single_worktree(self):
        raw = "/home/user/project\tmain\tclean"
        result = parse_porcelain(raw)
        assert result == (Worktree(path="/home/user/project", branch="main", status="clean"),)

    def test_multiple_worktrees(self):
        raw = (
            "/home/user/project\tmain\tclean\n"
            "/home/user/feat\tfeat-login\tmodified"
        )
        result = parse_porcelain(raw)
        assert result == (
            Worktree(path="/home/user/project", branch="main", status="clean"),
            Worktree(path="/home/user/feat", branch="feat-login", status="modified"),
        )

    def test_empty_lines_skipped(self):
        raw = "/home/user/project\tmain\tclean\n\n"
        result = parse_porcelain(raw)
        assert result == (Worktree(path="/home/user/project", branch="main", status="clean"),)

    def test_blank_branch_skipped(self):
        raw = "/home/user/project\t\tclean"
        result = parse_porcelain(raw)
        assert result == ()

    def test_empty_input(self):
        result = parse_porcelain("")
        assert result == ()

    def test_whitespace_only(self):
        result = parse_porcelain("   \n  \n")
        assert result == ()
