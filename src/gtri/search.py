from dataclasses import dataclass
from enum import Enum, auto


class SearchResult(Enum):
    ONLY_ONE_TOTAL = auto()
    SINGLE_MATCH = auto()
    MULTIPLE_MATCHES = auto()
    NO_MATCHES = auto()
    NO_SEARCH = auto()


@dataclass(frozen=True)
class NarrowResult:
    kind: SearchResult
    branches: tuple[str, ...]
    matched: tuple[str, ...]
    search_term: str


def narrow_branches(branches: tuple[str, ...], search_term: str) -> NarrowResult:
    if not search_term:
        if len(branches) <= 1:
            return NarrowResult(
                kind=SearchResult.ONLY_ONE_TOTAL,
                branches=branches,
                matched=branches,
                search_term="",
            )
        return NarrowResult(
            kind=SearchResult.NO_SEARCH,
            branches=branches,
            matched=(),
            search_term="",
        )

    term_lower = search_term.lower()
    matched = tuple(b for b in branches if term_lower in b.lower())

    if len(matched) == 1:
        kind = SearchResult.SINGLE_MATCH
    elif len(matched) > 1:
        kind = SearchResult.MULTIPLE_MATCHES
    else:
        kind = SearchResult.NO_MATCHES

    return NarrowResult(
        kind=kind,
        branches=branches,
        matched=matched,
        search_term=search_term,
    )
