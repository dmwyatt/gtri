# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`gtri` is a Python CLI tool that wraps [`git gtr`](https://github.com/coderabbitai/git-worktree-runner) (git-worktree-runner) with interactive fuzzy worktree selection. It uses a Textual TUI picker instead of relying on shell tab completion, making it work in terminals that don't support bash's programmable completion.

External runtime dependencies: `git`, `git-gtr`, and `gh` (GitHub CLI, required for PR commands).

## Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_search.py::test_name

# Run the CLI
uv run gtri

# Check cyclomatic complexity
uv run radon cc src/gtri/ -s
```

## Architecture

The CLI entry point is `gtri.cli:main` (registered as the `gtri` console script). The flow is:

1. **`cli.py`** — Orchestration: parses argv, checks dependencies, fetches worktrees, dispatches to the appropriate handler based on command category. This is the only module with side effects and subprocess calls for worktree listing.

2. **`commands.py`** — Pure command classification. Categorizes subcommands into four types:
   - `BRANCH_TAKING` — needs a worktree picker (editor, ai, go, run, rm, mv, copy)
   - `CREATION` — takes a branch name argument (new, new-ai)
   - `PR` — fetches open PRs via `gh`, shows picker, creates worktree (pr, pr-ai)
   - `PASSTHROUGH` — forwarded directly to `git gtr` (list)

3. **`search.py`** — Pure branch narrowing logic. Given branches and a search term, returns a `NarrowResult` with a `SearchResult` kind (ONLY_ONE_TOTAL, SINGLE_MATCH, MULTIPLE_MATCHES, NO_MATCHES, NO_SEARCH).

4. **`picker.py`** — Textual TUI app (`FuzzyPickerApp`) for fuzzy selection from a list of items. Used for both subcommand and worktree selection.

5. **`pr.py`** — Pure PR data: `PullRequest` dataclass, formatting for picker display, and parsing branch from picker selection.

6. **`worktree.py`** — Parses `git gtr list --porcelain` tab-delimited output into `Worktree` dataclasses.

7. **`exec.py`** — Thin wrappers around `shutil.which`, `subprocess.run`, and `os.execvp`. The `exec_replace` function replaces the current process (no return).

8. **`output.py`** — Rich-based console output helpers (error to stderr, info/command to stdout).

All domain logic (commands, search, worktree parsing) is pure and side-effect-free. Only `cli.py` and `exec.py` perform I/O.

## Conventions

- All user-facing errors raise `GtriError` (defined in `__init__.py`). The `main()` function catches these and prints them via Rich. Do not use `sys.exit()` or `print()` for error reporting elsewhere.
- `exec_replace()` calls `os.execvp` which replaces the process — code after an `exec_replace()` call is unreachable.

## Testing

- Uses `pytest` with `pytest-asyncio` (async mode: auto) for Textual app tests.
- Tests are in `tests/` mirroring `src/gtri/` module names.
- The Textual picker tests use `app.run_test()` for async TUI testing.

## CI

GitHub Actions CI runs `uv run pytest` on PRs when code files change. PRs also get automated Claude code review and security review.
