from gtri.search import NarrowResult, SearchResult, narrow_branches


BRANCHES = ("main", "feat-login", "feat-signup", "fix-typo")


class TestNarrowBranches:
    def test_no_search_term(self):
        result = narrow_branches(BRANCHES, "")
        assert result == NarrowResult(
            kind=SearchResult.NO_SEARCH,
            branches=BRANCHES,
            matched=(),
            search_term="",
        )

    def test_only_one_total_no_search(self):
        result = narrow_branches(("main",), "")
        assert result.kind == SearchResult.ONLY_ONE_TOTAL
        assert result.branches == ("main",)

    def test_one_branch_with_matching_search(self):
        result = narrow_branches(("main",), "main")
        assert result.kind == SearchResult.SINGLE_MATCH
        assert result.matched == ("main",)

    def test_one_branch_with_nonmatching_search(self):
        result = narrow_branches(("main",), "fea")
        assert result.kind == SearchResult.NO_MATCHES
        assert result.matched == ()

    def test_single_match(self):
        result = narrow_branches(BRANCHES, "typo")
        assert result.kind == SearchResult.SINGLE_MATCH
        assert result.matched == ("fix-typo",)
        assert result.search_term == "typo"

    def test_multiple_matches(self):
        result = narrow_branches(BRANCHES, "feat")
        assert result.kind == SearchResult.MULTIPLE_MATCHES
        assert result.matched == ("feat-login", "feat-signup")
        assert result.search_term == "feat"

    def test_no_matches(self):
        result = narrow_branches(BRANCHES, "nonexistent")
        assert result.kind == SearchResult.NO_MATCHES
        assert result.matched == ()
        assert result.search_term == "nonexistent"

    def test_case_insensitive(self):
        result = narrow_branches(BRANCHES, "FEAT")
        assert result.kind == SearchResult.MULTIPLE_MATCHES
        assert result.matched == ("feat-login", "feat-signup")

    def test_case_insensitive_single(self):
        result = narrow_branches(BRANCHES, "TYPO")
        assert result.kind == SearchResult.SINGLE_MATCH
        assert result.matched == ("fix-typo",)

    def test_branches_always_preserved(self):
        result = narrow_branches(BRANCHES, "feat")
        assert result.branches == BRANCHES
