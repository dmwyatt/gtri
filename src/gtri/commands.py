from dataclasses import dataclass
from enum import Enum, auto


class CommandCategory(Enum):
    BRANCH_TAKING = auto()
    CREATION = auto()
    PASSTHROUGH = auto()
    PR = auto()


@dataclass(frozen=True)
class ParsedArgs:
    search_term: str
    extra_flags: tuple[str, ...]


BRANCH_TAKING_COMMANDS = ("editor", "ai", "go", "run", "rm", "mv", "copy")
CREATION_COMMANDS = ("new", "new-ai")
PASSTHROUGH_COMMANDS = ("list",)
PR_COMMANDS = ("pr", "pr-ai")
ALL_COMMANDS = BRANCH_TAKING_COMMANDS + CREATION_COMMANDS + PASSTHROUGH_COMMANDS + PR_COMMANDS
PICKABLE_COMMANDS = BRANCH_TAKING_COMMANDS + PASSTHROUGH_COMMANDS + PR_COMMANDS


_CATEGORY_MAP = {
    c: CommandCategory.BRANCH_TAKING for c in BRANCH_TAKING_COMMANDS
} | {
    c: CommandCategory.CREATION for c in CREATION_COMMANDS
} | {
    c: CommandCategory.PASSTHROUGH for c in PASSTHROUGH_COMMANDS
} | {
    c: CommandCategory.PR for c in PR_COMMANDS
}


def classify_command(cmd: str) -> CommandCategory | None:
    return _CATEGORY_MAP.get(cmd)


def parse_branch_taking_args(args: tuple[str, ...]) -> ParsedArgs:
    search_term = ""
    extra_flags: list[str] = []
    for arg in args:
        if not search_term and not arg.startswith("-"):
            search_term = arg
        else:
            extra_flags.append(arg)
    return ParsedArgs(search_term=search_term, extra_flags=tuple(extra_flags))
