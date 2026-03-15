import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PullRequest:
    number: int
    title: str
    branch: str


def format_pr_item(pr: PullRequest) -> str:
    return f"#{pr.number} {pr.title} ({pr.branch})"


def parse_pr_item(item: str) -> str:
    match = re.search(r"\(([^)]+)\)$", item)
    if not match:
        raise ValueError(f"cannot parse branch from picker item: {item}")
    return match.group(1)
