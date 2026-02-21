import subprocess
import sys

from gtri import GtriError
from gtri.commands import (
    CommandCategory,
    PICKABLE_COMMANDS,
    classify_command,
    parse_branch_taking_args,
)
from gtri.exec import exec_replace, find_executable, run_subprocess
from gtri.output import print_command, print_error, print_info
from gtri.picker import FuzzyPickerApp
from gtri.search import SearchResult, narrow_branches
from gtri.worktree import parse_porcelain


USAGE = """\
[bold]gtri[/bold] — Interactive wrapper for git gtr with fuzzy worktree selection

[bold]USAGE:[/bold]
  gtri <subcommand> [search] [extra flags...]
  gtri

[bold]DESCRIPTION:[/bold]
  Presents a fuzzy picker to select a worktree, then passes the
  selected branch to git gtr along with any extra flags.

  Without a subcommand, prompts you to pick one first.

  If a search term is provided (first non-flag arg after subcommand):
    - Single match:    confirms and proceeds
    - Multiple matches: opens picker pre-filtered
    - No matches:       shows warning and exits

[bold]SUBCOMMANDS:[/bold]
  [green]Worktree selection[/green] (fuzzy pick an existing worktree):
    editor, ai, go, run, rm, mv, copy

  [green]Creation:[/green]
    new <branch>       Create a new worktree
    new-ai <branch>    Create a new worktree and launch AI session
                       (with --dangerously-skip-permissions)

  [green]Passthrough:[/green]
    list               List all worktrees (passes through to git gtr list)

[bold]EXAMPLES:[/bold]
  gtri ai                    Pick worktree, then: git gtr ai <branch>
  gtri ai feat               If "feat" matches one branch, confirm and go
  gtri rm --delete-branch    Pick worktree, then: git gtr rm <branch> --delete-branch
  gtri new my-feature        Create worktree: git gtr new my-feature
  gtri new-ai my-feature     Create worktree + launch AI session
  gtri list                  List all worktrees
  gtri                       Pick subcommand, then pick worktree\
"""


def check_dependencies() -> None:
    if not find_executable("git"):
        raise GtriError("git is required but not installed")
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise GtriError("not inside a git repository")
    if not find_executable("git-gtr"):
        raise GtriError(
            "git-gtr is required but not installed. "
            "See https://github.com/coderabbitai/git-worktree-runner"
        )


def fetch_worktrees():
    result = subprocess.run(
        ["git", "gtr", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    worktrees = parse_porcelain(result.stdout)
    if not worktrees:
        raise GtriError("no worktrees found. Create one with: gtri new <branch>")
    return worktrees


def run_picker(items: tuple[str, ...], title: str = "Select", initial_value: str = "") -> str | None:
    app = FuzzyPickerApp(items=items, title=title, initial_value=initial_value)
    return app.run()


def confirm_branch(branch: str) -> bool:
    from rich.prompt import Confirm

    return Confirm.ask(f"Use [bold]{branch}[/bold]?")


def resolve_branch(branches: tuple[str, ...], search_term: str) -> str:
    result = narrow_branches(branches, search_term)

    if result.kind == SearchResult.ONLY_ONE_TOTAL:
        return result.branches[0]

    if result.kind == SearchResult.NO_MATCHES:
        raise GtriError(f"no worktrees matching '{search_term}'")

    if result.kind == SearchResult.SINGLE_MATCH:
        if confirm_branch(result.matched[0]):
            return result.matched[0]
        selected = run_picker(branches, title="Select worktree...")
    elif result.kind == SearchResult.MULTIPLE_MATCHES:
        selected = run_picker(
            result.matched,
            title="Select worktree...",
            initial_value=result.search_term,
        )
    else:
        selected = run_picker(branches, title="Select worktree...")

    if not selected:
        raise GtriError("no worktree selected")
    return selected


def dispatch(subcmd: str, args: tuple[str, ...]) -> None:
    category = classify_command(subcmd)

    if category is None:
        raise GtriError(f"unknown subcommand: {subcmd}")

    if category == CommandCategory.PASSTHROUGH:
        exec_replace(["git", "gtr", subcmd, *args])
        return

    if category == CommandCategory.CREATION:
        if not args:
            raise GtriError(f"usage: gtri {subcmd} <branch-name>")
        branch = args[0]
        extra = args[1:]

        if subcmd == "new-ai":
            print_info(f"Creating branch: {branch}")
            run_subprocess(["git", "gtr", "new", branch])
            print_info("Running git gtr ai with --dangerously-skip-permissions...")
            exec_replace(["git", "gtr", "ai", branch, "--", "--dangerously-skip-permissions", *extra])
        else:
            print_command(f"git gtr new {branch}")
            exec_replace(["git", "gtr", "new", branch, *extra])
        return

    parsed = parse_branch_taking_args(args)
    worktrees = fetch_worktrees()
    branches = tuple(wt.branch for wt in worktrees)
    branch = resolve_branch(branches, parsed.search_term)

    cmd = ["git", "gtr", subcmd, branch, *parsed.extra_flags]
    print_command(" ".join(cmd))
    exec_replace(cmd)


def print_usage() -> None:
    from rich.console import Console

    Console().print(USAGE)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if argv and argv[0] in ("--help", "-h"):
        print_usage()
        raise SystemExit(0)

    try:
        check_dependencies()

        if not argv:
            subcmd = run_picker(
                PICKABLE_COMMANDS,
                title="Select subcommand...",
            )
            if not subcmd:
                raise GtriError("no subcommand selected")
            dispatch(subcmd, ())
        else:
            subcmd = argv[0]
            rest = tuple(argv[1:])
            dispatch(subcmd, rest)

    except GtriError as e:
        print_error(str(e))
        return 1

    return 0
