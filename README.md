# gtri

Interactive wrapper for [`git gtr`](https://github.com/coderabbitai/git-worktree-runner) (git-worktree-runner) with fuzzy worktree selection via [`gum`](https://github.com/charmbracelet/gum).

## Why? Bash completions exist.

`git gtr` has excellent bash completions. If you type `git gtr ai <tab>`, it completes worktree branch names for you. Problem solved, right?

Not if your terminal doesn't support them. [Warp](https://www.warp.dev/), for example, doesn't support bash's programmable completion (`complete -F`). So tab-completing `git gtr ai feat<tab>` into `git gtr ai feature/user-auth` simply doesn't work — you get nothing, or worse, filesystem path completions.

`gtri` works around this by replacing tab completion with interactive fuzzy selection. Instead of typing the branch name and hoping your terminal completes it, you get a searchable list powered by `gum filter`. This works in any terminal, regardless of completion support.

If your terminal handles bash completions fine, you probably don't need this.

## Install

### Dependencies

- [git gtr](https://github.com/coderabbitai/git-worktree-runner) — the worktree runner itself
- [gum](https://github.com/charmbracelet/gum) — for interactive fuzzy filtering and confirmation prompts

### Script

Copy `gtri` somewhere on your `PATH` and make it executable:

```bash
curl -o ~/bin/gtri https://raw.githubusercontent.com/dmwyatt/gtri/main/gtri
chmod +x ~/bin/gtri
```

Or clone and symlink:

```bash
git clone https://github.com/dmwyatt/gtri.git
ln -s "$(pwd)/gtri/gtri" ~/bin/gtri
```

## Usage

```
gtri <subcommand> [search] [extra flags...]
gtri
```

### With a subcommand

Pick a worktree from a fuzzy list, then run `git gtr <subcommand> <branch> [flags]`:

```bash
gtri ai                     # fuzzy-pick a worktree → git gtr ai <branch>
gtri editor                 # fuzzy-pick → git gtr editor <branch>
gtri rm --delete-branch     # fuzzy-pick → git gtr rm <branch> --delete-branch
```

### With a search term

Provide a partial match to skip or narrow the picker:

```bash
gtri ai auth                # "auth" matches feature/user-auth → confirm → go
gtri ai feature             # "feature" matches 3 branches → picker pre-filtered
gtri rm login --delete-branch  # matches bugfix/login → confirm → rm with flag
```

- **One match**: asks for confirmation, then proceeds
- **Multiple matches**: opens the picker with your search term pre-populated
- **No matches**: falls through to the full picker

### Without a subcommand

Prompts you to pick a subcommand first, then pick a worktree:

```bash
gtri                        # pick subcommand → pick worktree → run
```

### Single worktree

If only one worktree exists, it's selected automatically — no picker shown.

## Supported subcommands

These are the `git gtr` subcommands that take a branch/worktree argument:

`editor` · `ai` · `go` · `run` · `rm` · `mv` · `copy`

## License

MIT
