from gtri.pr import PullRequest, format_pr_item, parse_pr_item


class TestPullRequest:
    def test_fields(self):
        pr = PullRequest(number=42, title="Fix login bug", branch="fix/login-bug")
        assert pr.number == 42
        assert pr.title == "Fix login bug"
        assert pr.branch == "fix/login-bug"


class TestFormatPrItem:
    def test_formats_with_number_title_and_branch(self):
        pr = PullRequest(number=123, title="Add caching layer", branch="feature/caching")
        assert format_pr_item(pr) == "#123 Add caching layer (feature/caching)"

    def test_single_digit_number(self):
        pr = PullRequest(number=1, title="Init", branch="main")
        assert format_pr_item(pr) == "#1 Init (main)"


class TestParsePrItem:
    def test_roundtrips_with_format(self):
        pr = PullRequest(number=123, title="Add caching layer", branch="feature/caching")
        formatted = format_pr_item(pr)
        branch = parse_pr_item(formatted)
        assert branch == "feature/caching"

    def test_title_with_parentheses(self):
        pr = PullRequest(
            number=99, title="Fix bug (regression)", branch="fix/regression"
        )
        formatted = format_pr_item(pr)
        branch = parse_pr_item(formatted)
        assert branch == "fix/regression"

    def test_extracts_branch_from_last_parenthesized_group(self):
        """Branch is always the last (parenthesized) group."""
        item = "#10 Some (tricky) title (my-branch)"
        assert parse_pr_item(item) == "my-branch"
